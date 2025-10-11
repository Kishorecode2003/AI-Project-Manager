from fastapi import APIRouter, Depends, HTTPException
from backend import schemas
from backend.database import SessionLocal
from backend import models

router = APIRouter(prefix="/consultants", tags=["consultants"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ConsultantOut)
def create_consultant(consultant: schemas.ConsultantCreate, db=Depends(get_db)):
    existing = db.query(models.Consultant).filter(models.Consultant.email == consultant.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Consultant with this email already exists")
    c = models.Consultant(
        name=consultant.name,
        email=consultant.email,
        role=consultant.role,
        manager_email=consultant.manager_email,
        work_days=consultant.work_days
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.get("/", response_model=list[schemas.ConsultantOut])
def list_consultants(db=Depends(get_db)):
    return db.query(models.Consultant).all()
