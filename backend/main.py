import sys
import os

# Add root directory to path so ai/ module can be imported
# Go up 2 levels from backend/main.py to root
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import jobs, applicants, auth, applications, profile, interviews, analytics, resume, ranking
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartRecruiter API",
    description="AI-powered Applicant Tracking System with RAG capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applicants.router)
app.include_router(applications.router)
app.include_router(profile.router)
app.include_router(interviews.router)
app.include_router(analytics.router)
app.include_router(resume.router)  # Resume parsing endpoints
app.include_router(ranking.router)  # Candidate ranking


@app.get("/")
def read_root():
    return {
        "status": "SmartRecruiter API Running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
