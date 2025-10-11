
from fastapi import APIRouter, Depends, HTTPException
from backend import schemas
from backend.database import SessionLocal
from backend import models
from backend.utils.templates import task_assignment_template
from backend.services.email_service import send_email
import logging
 
router = APIRouter(prefix="/tasks", tags=["tasks"])
 
from pydantic import BaseModel
 
class SendTaskEmailRequest(BaseModel):
    task_id: int
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
 
@router.post("/", response_model=schemas.TaskOut)
def create_task(payload: schemas.TaskCreate, db=Depends(get_db)):
    t = models.Task(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date
    )
    db.add(t)
    db.commit()
    db.refresh(t)
 
    consultants = []
    for assignee in payload.assignees:
        consultant = db.query(models.Consultant).filter_by(email=assignee.email).first()
        if not consultant:
            consultant = models.Consultant(name=assignee.name, email=assignee.email)
            db.add(consultant)
            db.commit()
            db.refresh(consultant)
        consultants.append(consultant)
    t.consultants = consultants
    db.commit()
    db.refresh(t)
    # return t
    response = {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "start_date": t.start_date,
        "end_date": t.end_date,
        "status": t.status,
        "status_pct": t.status_pct,
        "last_updated_at": t.last_updated_at,
        "assignees": [{"name": c.name, "email": c.email} for c in t.consultants]
    }
    return response


 
@router.get("/", response_model=list[schemas.TaskOut])
def list_tasks(db=Depends(get_db)):
    tasks = db.query(models.Task).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "start_date": t.start_date,
            "end_date": t.end_date,
            "status": t.status,
            "status_pct": t.status_pct,
            "last_updated_at": t.last_updated_at,
            "assignees": [{"name": c.name, "email": c.email} for c in t.consultants]
        }
        for t in tasks
    ]
 
@router.post("/send-update")
def send_update_request(payload: SendTaskEmailRequest, db=Depends(get_db)):
    logger.info(f"Received request to send update for task_id={payload.task_id}")
 
    # Fetch the task and assignees
    task = db.query(models.Task).filter(models.Task.id == payload.task_id).first()
    if not task:
        logger.error(f"Task with id {payload.task_id} not found")
        raise HTTPException(status_code=404, detail="Task not found")
    assignees = task.consultants
    if not assignees:
        logger.error(f"No assignees found for task id {payload.task_id}")
        raise HTTPException(status_code=400, detail="No assignees for this task")
 
    # Compose subject and body
    names = [a.name for a in assignees]
    greeting = f"Hello {'/'.join(names)}," if names else "Hello,"
    subject = f"Task Assignment: {task.name}"
    body = (
        f"{greeting}\n\n"
        f"You have been assigned a new task.\n\n"
        f"Task Name: {task.name}\n"
        f"Description: {task.description}\n"
        f"Start Date: {task.start_date}\n"
        f"End Date: {task.end_date}\n\n"
        f"Please review the task details and reach out if you have any questions.\n\n"
        f"Best regards,\n"
        f"Sivasubramanian Murugesan"
    )
 
    html_body = None 
 
    # Collect emails
    to_emails = [a.email for a in assignees]
    logger.info(f"Sending task assignment email to: {to_emails}")
 
    try:
        # Send the email using Azure Communication Services Email SDK
        from backend.services.email_service import send_email
        send_email(subject, body, to_emails, html_body=html_body)
        logger.info(f"Email sent successfully for task_id={payload.task_id}")
    except Exception as e:
        logger.error(f"Failed to send email for task_id={payload.task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send email")
 
    # Save outbound email record
    from backend.models import EmailMessage as EmailModel
    em = EmailModel(
        external_message_id=None,
        direction='outbound',
        subject=subject,
        body_text=body,
        sender=None,
        recipients=','.join(to_emails),
        linked_task_id=task.id
    )
    db.add(em)
    db.commit()
    logger.info(f"Email record saved for task_id={payload.task_id}")
 
    return {"status": "ok", "sent_to": to_emails}
 
 