from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Annotated
from datetime import datetime
from enum import Enum

class Assignee(BaseModel):
    name: str
    email: str

class StatusLabel(str, Enum):
    NotStarted = "Not Started"
    InProgress = "In Progress"
    Blocked = "Blocked"
    Done = "Done"

class ConsultantCreate(BaseModel):
    name: str
    email: EmailStr

class ConsultantOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assignees: List[Assignee]  
 
class TaskOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: Optional[str]
    status_pct: Optional[int]
    last_updated_at: Optional[datetime]
    assignees: List[Assignee] = [] 
    
    class Config:
        orm_mode = False

class SendTaskEmail(BaseModel):
    task_id: int
    consultant_ids: List[int]
    subject: Optional[str]
    body: Optional[str]

class TaskSummary(BaseModel):
    task_name: str
    assignees: List[str] 

class DashboardSummary(BaseModel):
    overdue: List[TaskSummary] = []
    noUpdate: List[TaskSummary] = []
    atRisk: List[TaskSummary] = []
    done: List[TaskSummary] = []


class UpdateOut(BaseModel):
    id: int
    consultant_name: Optional[str] = None
    consultant_email: Optional[str] = None
    task_name: Optional[str] = None
    task_id: Optional[int] = None
    status_label: Optional[str] = "Not Started"
    status_pct: Optional[int] = 0
    blockers: Optional[str] = "None"
    eta_date: Optional[str] = "N/A"
    created_at: Optional[datetime] = None  
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    state: Optional[int] = 0

class SchedulerConfigOut(BaseModel):
    daily: str
    weekly: str
    timezone: Optional[str] = "UTC"

    class Config:
        orm_mode = True

class SchedulerConfigUpdate(BaseModel):
    daily: Annotated[str, Field(pattern=r"^\d{2}:\d{2}$")]
    weekly: Annotated[str, Field(pattern=r"^\d{2}:\d{2}$")]
    timezone: Optional[str] = "UTC"

class TaskReminderCreate(BaseModel):
    task_id: int
    reminder_time: str  
 
class TaskReminderResponse(BaseModel):
    id: int
    task_id: int
    reminder_time: str
    is_active: bool
    message: str
 
    class Config:
        from_attributes = True