
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import SessionLocal
from backend.schemas import UpdateOut
from backend.models import StatusUpdate, Task, Consultant
import traceback

router = APIRouter(prefix="/updates", tags=["updates"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[UpdateOut])
async def get_updates(db: Session = Depends(get_db)):
    try:
        updates_query = db.query(
            StatusUpdate.id,
            Consultant.name.label("consultant_name"),
            Consultant.email.label("consultant_email"),
            Task.name.label("task_name"),
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
        ).order_by(StatusUpdate.created_at.desc())
        updates = updates_query.all()
        print("Number of updates:", len(updates)) 
        for update in updates:
            print("Update:", update)  
        result = []
        for update in updates:
            result.append({
                "id": update[0],
                "consultant_name": update[1] if update[1] else None,
                "consultant_email": update[2] if update[2] else None,
                "task_name": update[3] if update[3] else None,
                "status_label": update[4] if update[4] else "Not Started",
                "status_pct": update[5] if update[5] else 0,
                "blockers": update[6] if update[6] else "None",
                "eta_date": update[7] if update[7] else "N/A",
                "created_at": update[8].isoformat() if update[8] else None, 
                "summary": update[9] if update[9] else None,
                "sentiment": update[10] if update[10] else None,
                "state": update[11] if update[11] else 0
            })
        return result
    except Exception as e:
        print("Error fetching updates:", e)
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

