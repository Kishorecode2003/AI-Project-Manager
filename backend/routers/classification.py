from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import re
from typing import Optional
from backend.database import SessionLocal
from backend import models
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
 
router = APIRouter(prefix="/tasks", tags=["tasks"])
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
class ProcessReplyRequest(BaseModel):
    task_id: int
    consultant_email: str
    email_subject: str
    email_body: str
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
def classify_intent(body: str) -> str:
    body_lower = body.lower()
    if any(word in body_lower for word in ["ooo", "vacation", "sick", "leave"]):
        return "leave"
    if any(word in body_lower for word in ["progress", "complete", "blocked", "eta", "%", "update"]):
        return "update"
    return "other"
 
def extract_percent_complete(body: str) -> Optional[int]:
    match = re.search(r"(\d{1,3})\s*%[\s\w]*complete", body, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d{1,3})\s*%", body)
    if match:
        return int(match.group(1))
    return None
 
def extract_eta(body: str) -> Optional[str]:
    match = re.search(r"eta[:\s\-]*([0-9]{4}-[0-9]{2}-[0-9]{2})", body, re.IGNORECASE)
    if match:
        return match.group(1)
    return None
 
def extract_blockers(body: str) -> Optional[str]:
    match = re.search(r"blocked by ([^\.\n]+)", body, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None
 
def extract_absence(body: str) -> Optional[str]:
    match = re.search(r"on leave from ([0-9\-]+) to ([0-9\-]+)(?: due to ([\w\s]+))?", body, re.IGNORECASE)
    if match:
        start, end, reason = match.groups()
        return f"On leave {start} to {end}" + (f" ({reason.strip()})" if reason else "")
    return None
 
def summarize_reply(body: str) -> str:
    percent = extract_percent_complete(body)
    blockers = extract_blockers(body)
    eta = extract_eta(body)
    absence = extract_absence(body)
    summary_parts = []
    if percent is not None:
        summary_parts.append(f"{percent}% complete")
    if blockers:
        summary_parts.append(f"Blocked by {blockers}")
    if eta:
        summary_parts.append(f"ETA: {eta}")
    if absence:
        summary_parts.append(absence)
    return ". ".join(summary_parts) + ("." if summary_parts else "")
 
def determine_status_label(intent: str, percent_complete: Optional[int], blockers: Optional[str]) -> str:
    if percent_complete is not None:
        if percent_complete == 0:
            return "Not Started"
        elif percent_complete == 100:
            return "Completed"
        else:
            return "In Progress"
    elif blockers:
        return "Blocked"
    elif intent == "leave":
        return "On Leave"
    elif intent == "update":
        return "In Progress"
    else:
        return "Unknown"
 
 
@router.post("/process-reply")
def process_reply(payload: ProcessReplyRequest, db=Depends(get_db)):
    logger.info(f"Processing reply for task_id={payload.task_id}, consultant={payload.consultant_email}")
    try:
        # 1. Validate task and consultant
        task = db.query(models.Task).filter(models.Task.id == payload.task_id).first()
        if not task:
            logger.error(f"Task with id {payload.task_id} not found")
            raise HTTPException(status_code=404, detail="Task not found")
        consultant = db.query(models.Consultant).filter_by(email=payload.consultant_email).first()
        if not consultant:
            logger.error(f"Consultant with email {payload.consultant_email} not found")
            raise HTTPException(status_code=404, detail="Consultant not found")
 
        # 2. Extract classification data
        intent = classify_intent(payload.email_body)
        percent_complete = extract_percent_complete(payload.email_body)
        eta_date = extract_eta(payload.email_body)
        blockers = extract_blockers(payload.email_body)
        summary = summarize_reply(payload.email_body)
        absence_detected = intent == "leave"
        status_label = determine_status_label(intent, percent_complete, blockers)
 
        # 3. Create EmailMessage record
        email_message = models.EmailMessage(
            external_message_id=None,
            direction='inbound',
            subject=payload.email_subject,
            body_text=payload.email_body,
            sender=payload.consultant_email,
            recipients=None,
            thread_id=None,
            linked_task_id=task.id,
            linked_consultant_id=consultant.id
        )
        db.add(email_message)
        db.flush()  # Get email_message.id
 
        # 4. Create StatusUpdate record
        status_update = models.StatusUpdate(
            task_id=task.id,
            consultant_id=consultant.id,
            intent=intent,
            status_pct=percent_complete,
            status_label=status_label,
            summary=summary if summary else None,
            blockers=blockers,
            eta_date=eta_date,
            sentiment=None,
            source_email_id=email_message.id
        )
        db.add(status_update)
 
        # 5. Update Task if progress provided
        if percent_complete is not None:
            task.status_pct = percent_complete
            if percent_complete == 0:
                task.status = models.StatusEnum.NOT_STARTED
            elif percent_complete == 100:
                task.status = models.StatusEnum.DONE
            elif blockers:
                task.status = models.StatusEnum.BLOCKED
            else:
                task.status = models.StatusEnum.IN_PROGRESS
 
        db.commit()
        db.refresh(email_message)
        db.refresh(status_update)
 
        logger.info(f"Reply processed: email_id={email_message.id}, status_update_id={status_update.id}")
 
        return {
            "intent": intent,
            "percent_complete": percent_complete,
            "eta_date": eta_date,
            "blockers": blockers,
            "summary": summary,
            "absence_detected": absence_detected,
            "status_label": status_label,
            "email_message_id": email_message.id,
            "status_update_id": status_update.id,
            "task_updated": percent_complete is not None
        }
 
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(status_code=400, detail="Database integrity constraint violated")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
 
 