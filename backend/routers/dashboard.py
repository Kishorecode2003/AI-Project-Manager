from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.database import SessionLocal
from backend.models import Task, StatusEnum
from backend.schemas import TaskSummary, DashboardSummary

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_dashboard_summary(db: Session):
    now = datetime.utcnow()
    forty_eight_hours_ago = now - timedelta(hours=48)
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

    # Fetch overdue tasks with names and assignees
    overdue_tasks = db.query(Task).filter(
        and_(
            Task.status != StatusEnum.DONE,
            Task.end_date < now.date()
        )
    ).all()

    # Fetch tasks with no update in 48 hours
    no_update_tasks = db.query(Task).filter(
        and_(
            Task.status != StatusEnum.DONE,
            Task.last_updated_at < forty_eight_hours_ago
        )
    ).all()

    # Fetch at-risk (blocked) tasks
    at_risk_tasks = db.query(Task).filter(
        Task.status == StatusEnum.BLOCKED
    ).all()

    # Fetch tasks done this week
    done_this_week_tasks = db.query(Task).filter(
        and_(
            Task.status == StatusEnum.DONE,
            Task.last_updated_at >= week_start
        )
    ).all()

    # Helper function to extract task name and assignee names
    def task_to_summary(task):
        assignee_names = [consultant.name for consultant in task.consultants]
        return TaskSummary(task_name=task.name, assignees=assignee_names)

    return {
        "overdue": [task_to_summary(task) for task in overdue_tasks],
        "noUpdate": [task_to_summary(task) for task in no_update_tasks],
        "atRisk": [task_to_summary(task) for task in at_risk_tasks],
        "done": [task_to_summary(task) for task in done_this_week_tasks],
    }

router = APIRouter(prefix="/summary", tags=["summary"])

@router.get("/dashboard", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)
