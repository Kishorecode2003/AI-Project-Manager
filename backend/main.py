from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routers import consultants, tasks, dashboard, Updates, Scheduler, classification, reply,leave_updates
from backend.services.scheduler import start_scheduler

app = FastAPI(title='AI Project Manager')

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.on_event('startup')
def startup_event():
    init_db()
    # start scheduler
    start_scheduler(app)

# Include routers
app.include_router(consultants.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)
app.include_router(Updates.router)
app.include_router(Scheduler.router)
app.include_router(classification.router)
app.include_router(reply.router)
app.include_router(leave_updates.router)

@app.get('/')
def root():
    return {"message": "AI PM Backend running"}
