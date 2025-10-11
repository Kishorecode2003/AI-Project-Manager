from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import SessionLocal
from backend.schemas import UpdateOut
from backend.models import StatusUpdate, Task, Consultant
import traceback

router = APIRouter(prefix="/leave-updates", tags=["leave-updates"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[UpdateOut])
async def get_leave_updates(
    db: Session = Depends(get_db),
    state: Optional[int] = Query(0, description="State value for further filtering (0 or 1)")
):
    try:
        
        updates_query = db.query(
            StatusUpdate.id,
            Consultant.name.label("consultant_name"),
            Consultant.email.label("consultant_email"), 
            Task.name.label("task_name"),
            Task.id.label("task_id"), 
            StatusUpdate.status_label,
            StatusUpdate.status_pct,
            StatusUpdate.blockers,
            StatusUpdate.eta_date,
            StatusUpdate.created_at,
            StatusUpdate.summary,
            StatusUpdate.sentiment,
            StatusUpdate.reply_sent
        ).outerjoin(
            Task, StatusUpdate.task_id == Task.id
        ).outerjoin(
            Consultant, StatusUpdate.consultant_id == Consultant.id
        ).filter(
            StatusUpdate.intent == "leave"
        ).order_by(StatusUpdate.created_at.desc())

        if state is not None:
            updates_query = updates_query.filter(StatusUpdate.reply_sent == state)

        updates = updates_query.all()
        print("Raw SQL query results:", updates) 

        result = []
        for update in updates:
            result.append({
                
                "id": update[0],  # StatusUpdate.id
                "consultant_name": update[1],
                "consultant_email": update[2],
                "task_name": update[3],
                "task_id": update[4],  # Task.id (task_id)
                "status_label": update[5] or "Not Started",
                "status_pct": update[6] or 0,
                "blockers": update[7] or "None",
                "eta_date": update[8] or "N/A",
                "created_at": update[9],
                "summary": update[10],
                "sentiment": update[11],
                "state": update[12]
            })

        return result

    except Exception as e:
        print("Error fetching leave updates:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
