
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.services.email_service import send_email
from backend.models import EmailMessage as EmailModel, Task, Consultant
from backend.database import SessionLocal
from backend import models
from backend.routers.classification import (
    classify_intent, extract_percent_complete, extract_eta,
    extract_blockers, summarize_reply
)
import openai  
import os
import re
 
router = APIRouter(prefix="/tasks", tags=["tasks"])
 
class DraftReplyRequest(BaseModel):
    task_id: int
    consultant_email: str
    email_subject: str
    email_body: str
 
class DraftReplyResponse(BaseModel):
    consultant_email: str
    reply_subject: str
    reply_body: str
 
class SendReplyMailRequest(BaseModel):
    task_id: int
    consultant_email: str
    reply_subject: str
    reply_body: str
 
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
def get_task_and_consultant(db, task_id, consultant_email):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    consultant = db.query(models.Consultant).filter(models.Consultant.email == consultant_email).first()
    return task, consultant
 
def strip_subject_line(text: str) -> str:
    """
    Removes a leading 'Subject: ...' line from the text, if present.
    """
    # Remove 'Subject: ...' line at the very start (with or without trailing newline)
    return re.sub(r"^Subject:.*\n+", "", text, flags=re.IGNORECASE)
 
@router.post("/draft-reply", response_model=DraftReplyResponse)
def draft_reply(payload: DraftReplyRequest, db=Depends(get_db)):
    # Analyze the incoming email
    intent = classify_intent(payload.email_body)
    percent_complete = extract_percent_complete(payload.email_body)
    eta_date = extract_eta(payload.email_body)
    blockers = extract_blockers(payload.email_body)
    summary = summarize_reply(payload.email_body)
 
    # Fetch task and consultant info for context
    task, consultant = get_task_and_consultant(db, payload.task_id, payload.consultant_email)
    if not task or not consultant:
        raise HTTPException(status_code=404, detail="Task or consultant not found")
 
    prompt = (
        f"You are a project manager. An assignee ({consultant.name}) replied to a task update email.\n"
        f"Task: {task.name}\n"
        f"Description: {task.description}\n"
        f"Assignee's reply:\n{payload.email_body}\n"
        f"Summary of reply: {summary}\n"
        f"Draft a concise, firm reply acknowledging the update. "
        f"If the reply mentions blockers, instruct the assignee to resolve or escalate promptly. "
        f"If progress is reported, acknowledge it without excessive praise. "
        f"If absence/leave is mentioned, confirm receipt and remind them of their responsibilities. "
        f"Do not be overly gentle or apologetic. "
        f"Ensures the closing is always 'Best Regards,Sivasubramanian Murugesan'. "
 
    )
 
    # Create Azure OpenAI client (new SDK style)
    client = openai.AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
 
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),  # Your deployment name
        messages=[
            {"role": "system", "content": "You are a helpful project manager assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7,
    )
 
    # Remove any leading 'Subject: ...' line from the reply body
    reply_body = response.choices[0].message.content.strip()
    reply_body = strip_subject_line(reply_body)
 
    reply_subject = f"Re: {payload.email_subject}"
 
    return DraftReplyResponse(
        consultant_email=payload.consultant_email,
        reply_subject=reply_subject,
        reply_body=reply_body
    )
 
 
@router.post("/send-mail")
def send_mail(payload: SendReplyMailRequest, db=Depends(get_db)):
    # Fetch consultant and task for context
    task = db.query(Task).filter(Task.id == payload.task_id).first()
    consultant = db.query(Consultant).filter(Consultant.email == payload.consultant_email).first()
    if not task or not consultant:
        raise HTTPException(status_code=404, detail="Task or consultant not found")
 
    # Compose email
    subject = payload.reply_subject
    body = payload.reply_body
    to_emails = [consultant.email]
 
    try:
        send_email(subject, body, to_emails)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send email")
 
    # Log the outbound email
    em = EmailModel(
        external_message_id=None,
        direction='outbound',
        subject=subject,
        body_text=body,
        sender=None,
        recipients=consultant.email,
        linked_task_id=task.id,
        linked_consultant_id=consultant.id
    )
    db.add(em)
    db.commit()

    status_update = db.query(models.StatusUpdate).filter(
        models.StatusUpdate.task_id == task.id,
        models.StatusUpdate.consultant_id == consultant.id,
        models.StatusUpdate.intent == "leave"
    ).order_by(models.StatusUpdate.created_at.desc()).first()
    if status_update:
        status_update.reply_sent = 1
        db.commit()
 
    return {"status": "ok", "sent_to": to_emails}
 
 