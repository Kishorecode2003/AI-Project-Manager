from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone as pytz_timezone
from sqlalchemy.orm import Session
from backend.models import SchedulerConfig
import logging
from datetime import datetime, timedelta
from backend.services.imap_service import poll_inbound_and_process
from backend.services.email_service import send_email
from backend.database import SessionLocal
from backend import models
from backend.utils.templates import task_assignment_template

sched = BackgroundScheduler()

def start_scheduler(app=None):
    # Poll inbound emails every 5 minutes
    sched.add_job(poll_inbound_and_process, 'interval', minutes=5, id='imap_poll')

    # Daily reminders at 10:00 server time
    sched.add_job(daily_reminder_job, 'cron', hour=10, minute=0, id='daily_reminder')

    # Weekly performance on Friday 16:00
    sched.add_job(weekly_performance_job, 'cron', day_of_week='fri', hour=16, minute=0, id='weekly_report')

    sched.start()
    print('Scheduler started at', datetime.utcnow())


def daily_reminder_job():
    print('Daily reminder job running at', datetime.utcnow())


def weekly_performance_job():
    print('Weekly performance job running at', datetime.utcnow())
    session = SessionLocal()
    # naive weekly report: for each consultant generate a simple report and email
    consultants = session.query(models.Consultant).all()
    for c in consultants:
        # compute a simple score based on number of updates
        updates = session.query(models.StatusUpdate).filter(models.StatusUpdate.consultant_id == c.id).all()
        n_updates = len(updates)
        score = min(100, n_updates * 10)
        # create report row
        report = models.PerformanceReport(
            consultant_id=c.id,
            week_start=str((datetime.utcnow() - timedelta(days=7)).date()),
            week_end=str(datetime.utcnow().date()),
            days_absent=0,
            tasks_summary_json='{}',
            score=score
        )
        session.add(report)
        session.commit()
        # send a basic email
        subject = f"Your weekly performance summary ({report.week_start}–{report.week_end})"
        body = f"Hello {c.name},\n\nThis is your automated weekly report. Score: {score}/100.\nUpdates received: {n_updates}\n\nRegards\nPM System"
        try:
            send_email(subject, body, [c.email])
        except Exception as e:
            print('Failed to send weekly report to', c.email, e)
    session.close()


def get_scheduler_config(db: Session):
    config = db.query(SchedulerConfig).first()
    if not config:
        config = SchedulerConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

def schedule_jobs(config: SchedulerConfig, send_daily_reminders, send_weekly_reports):
    sched.remove_all_jobs()
    tz = pytz_timezone(config.timezone or "UTC")
    # Daily reminder
    hour, minute = map(int, config.daily.split(":"))
    sched.add_job(
        send_daily_reminders,
        CronTrigger(hour=hour, minute=minute, timezone=tz),
        id="daily_reminder"
    )
    # Weekly report (Friday by default)
    hour, minute = map(int, config.weekly.split(":"))
    sched.add_job(
        send_weekly_reports,
        CronTrigger(day_of_week="fri", hour=hour, minute=minute, timezone=tz),
        id="weekly_report"
    )
    logging.info("Scheduled jobs updated.")

def reschedule_jobs(db: Session, send_daily_reminders, send_weekly_reports):
    config = get_scheduler_config(db)
    schedule_jobs(config, send_daily_reminders, send_weekly_reports)
