from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.services.scheduler import SchedulerConfig
from backend.schemas import SchedulerConfigOut, SchedulerConfigUpdate
from backend.services.scheduler import reschedule_jobs, get_scheduler_config
 
from apscheduler.triggers.cron import CronTrigger
from backend.database import SessionLocal
from backend import models, schemas
from backend.services.email_service import send_email
from backend.services.scheduler import sched
from datetime import time
import pytz
import logging
 
 
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)
 
router = APIRouter(prefix="/scheduler", tags=["scheduler"])
logger = logging.getLogger(__name__)
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
 
@router.post("/schedule-reminder", response_model=schemas.TaskReminderResponse)
def schedule_task_reminder(payload: schemas.TaskReminderCreate, db: Session = Depends(get_db)):
    # Fetch and validate task
    task = db.query(models.Task).filter(models.Task.id == payload.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.consultants:
        raise HTTPException(status_code=400, detail="No assignees found for this task")
    if not task.start_date or not task.end_date or task.start_date > task.end_date:
        raise HTTPException(status_code=400, detail="Invalid task dates")
 
    # Parse reminder time
    try:
        hour, minute = map(int, payload.reminder_time.split(':'))
        reminder_time_obj = time(hour, minute)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
 
    # Create reminder record
    reminder = models.TaskReminder(
        task_id=payload.task_id,
        reminder_time=reminder_time_obj,
        is_active=True
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
 
    # Unique job ID
    job_id = f"task_reminder_{payload.task_id}_{hour}_{minute}"
    try:
        sched.remove_job(job_id)
    except Exception:
        pass 
 
 
    trigger = CronTrigger(
    hour=hour,
    minute=minute,
    start_date=task.start_date,
    end_date=task.end_date,
    timezone=pytz.timezone('Asia/Kolkata')
    )
    sched.add_job(
        func=send_task_reminder_email,
        trigger=trigger,
        args=[payload.task_id],
        id=job_id,
        name=f"Task Reminder for {task.name}",
        replace_existing=True
    )
 
    return schemas.TaskReminderResponse(
        id=reminder.id,
        task_id=reminder.task_id,
        reminder_time=payload.reminder_time,
        is_active=reminder.is_active,
        message=f"Reminder scheduled daily at {payload.reminder_time} from {task.start_date} to {task.end_date}"
    )
 
 
def send_task_reminder_email(task_id: int):
    db = SessionLocal()
    try:
        logger.info(f"Running scheduled reminder for task_id={task_id}")
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task or not task.consultants:
            logger.warning(f"No task or consultants found for task_id={task_id}")
            return
        names = [a.name for a in task.consultants]
        greeting = f"Hello {'/'.join(names)}," if names else "Hello,"
        subject = f"Task Update Reminder: {task.name}"
        body = (
            f"{greeting}\n\n"
            f"This is a reminder to provide an update on your assigned task.\n\n"
            f"Task Name: {task.name}\n"
            f"Description: {task.description}\n"
            f"Start Date: {task.start_date}\n"
            f"End Date: {task.end_date}\n\n"
            f"Please share your progress, any blockers, or questions you might have.\n\n"
            f"Kindly ignore if already updated.\n\n"
            f"Best regards,\n"
            f"Sivasubramanian Murugesan"
        )
        to_emails = [a.email for a in task.consultants]
        try:
            send_email(subject, body, to_emails)
            logger.info(f"Sent reminder email for task_id={task_id} to {to_emails}")
        except Exception as e:
            logger.exception(f"Failed to send reminder email for task_id={task_id} to {to_emails}: {e}")
    except Exception as e:
        logger.exception(f"Exception in scheduled job for task_id={task_id}: {e}")
    finally:
        db.close()
 
 