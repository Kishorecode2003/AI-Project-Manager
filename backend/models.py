
from sqlalchemy import Column, Integer, String, DateTime,Time, Text, ForeignKey, Table, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum
from datetime import datetime
 
class StatusEnum(str, enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    DONE = "Done"
 
assignment_table = Table(
    'assignments', Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('consultant_id', Integer, ForeignKey('consultants.id'))
)
 
class Consultant(Base):
    __tablename__ = 'consultants'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
 
    assignments = relationship('Task', secondary=assignment_table, back_populates='consultants')
 
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.NOT_STARTED)
    status_pct = Column(Integer, default=0)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
 
    consultants = relationship('Consultant', secondary=assignment_table, back_populates='assignments')
    status_updates = relationship('StatusUpdate', back_populates='task')
    reminders = relationship("TaskReminder", back_populates="task")
 
class EmailMessage(Base):
    __tablename__ = 'email_messages'
    id = Column(Integer, primary_key=True, index=True)
    external_message_id = Column(String, nullable=True, index=True, unique=True)
    direction = Column(String, nullable=False)  
    subject = Column(String)
    body_text = Column(Text)
    sender = Column(String)
    recipients = Column(Text)  
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    thread_id = Column(String, nullable=True)
    linked_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    linked_consultant_id = Column(Integer, ForeignKey('consultants.id'), nullable=True)
 
class StatusUpdate(Base):
    __tablename__ = 'status_updates'
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    consultant_id = Column(Integer, ForeignKey('consultants.id'))
    intent = Column(String, nullable=True)
    status_pct = Column(Integer, nullable=True)
    status_label = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    blockers = Column(Text, nullable=True)
    eta_date = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    source_email_id = Column(Integer, ForeignKey('email_messages.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reply_sent = Column(Integer, default=0)
 
    task = relationship('Task', back_populates='status_updates')
 
class PerformanceReport(Base):
    __tablename__ = 'performance_reports'
    id = Column(Integer, primary_key=True, index=True)
    consultant_id = Column(Integer, ForeignKey('consultants.id'))
    week_start = Column(String)
    week_end = Column(String)
    days_absent = Column(Integer, default=0)
    tasks_summary_json = Column(Text)
    score = Column(Integer, default=0)
    emailed_at = Column(DateTime(timezone=True), server_default=func.now())
 
class SchedulerConfig(Base):
    __tablename__ = "scheduler_config"
    id = Column(Integer, primary_key=True, index=True)
    daily = Column(String, default="10:00")   
    weekly = Column(String, default="16:00") 
    timezone = Column(String, default="UTC")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
 
class TaskReminder(Base):
    __tablename__ = 'task_reminders'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    reminder_time = Column(Time, nullable=False)  
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    task = relationship("Task", back_populates="reminders")
 