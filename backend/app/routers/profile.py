from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os

# Add ai directory to path (go up 3 levels from backend/app/routers/ to root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.database import get_db
from app import models, schemas
from ai.nlp import ResumeParser
from app.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/profile", tags=["profile"])

resume_parser = ResumeParser()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=schemas.ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get current user's profile"""
    return current_user


@router.put("/", response_model=schemas.ProfileResponse)
def update_profile(
    profile_update: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update current user's profile"""
    update_data = profile_update.dict(exclude_unset=True)
    
    # Recruiters can update company_name, applicants cannot
    if current_user.role == "applicant" and "company_name" in update_data:
        del update_data["company_name"]
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/resume", response_model=dict)
def get_resume_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get parsed resume data from most recent application (applicant only)"""
    if current_user.role != "applicant":
        raise HTTPException(status_code=403, detail="Only applicants can view resume data")
    
    # Get the most recent application with parsed resume data
    latest_application = db.query(models.Application).filter(
        models.Application.user_id == current_user.id,
        models.Application.applicant_id.isnot(None)
    ).order_by(models.Application.created_at.desc()).first()
    
    if not latest_application or not latest_application.applicant_id:
        return {
            "message": "No resume data found",
            "extracted_data": None,
            "parsed_resume": None
        }
    
    # Get the applicant record with parsed data
    applicant = db.query(models.Applicant).filter(
        models.Applicant.id == latest_application.applicant_id
    ).first()
    
    if not applicant:
        return {
            "message": "No resume data found",
            "extracted_data": None,
            "parsed_resume": None
        }
    
    # Return complete parsed resume data including AI-generated content
    parsed_resume_data = {
        "name": f"{applicant.first_name} {applicant.last_name}",
        "first_name": applicant.first_name,
        "last_name": applicant.last_name,
        "email": applicant.email,
        "phone": applicant.phone,
        "skills": applicant.skills or [],
        "experience_years": applicant.experience_years or 0.0,
        "education": applicant.education or [],
        "work_experience": applicant.work_experience or [],
        "resume_text": applicant.resume_text or "",
        "ai_summary": applicant.ai_summary,
        "interview_questions": applicant.interview_questions or [],
        "file_path": applicant.resume_file_path,
        "resume_file_type": applicant.resume_file_type
    }
    
    return {
        "message": "Resume data retrieved successfully",
        "file_path": applicant.resume_file_path,
        "extracted_data": parsed_resume_data,  # Keep for backward compatibility
        "parsed_resume": parsed_resume_data  # Also return as parsed_resume for consistency
    }


@router.post("/resume", response_model=dict)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Upload resume for applicant profile (applicant only)"""
    if current_user.role != "applicant":
        raise HTTPException(status_code=403, detail="Only applicants can upload resumes")
    
    # Read file content
    file_content = await file.read()
    
    # Save file
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"profile_{current_user.id}_{file_id}.{file_ext}")
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Parse resume (AI enhancement handled separately)
    try:
        parsed_data = resume_parser.parse_file(file_content, file.filename, use_ai=False)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing resume: {str(e)}")
    
    # Store resume data in user profile (we could add a resume field to User model)
    # For now, return the parsed data
    return {
        "message": "Resume uploaded successfully",
        "file_path": file_path,
        "extracted_data": {
            "skills": parsed_data.get("skills", []),
            "experience_years": parsed_data.get("experience_years", 0.0),
            "education": parsed_data.get("education", []),
            "work_experience": parsed_data.get("work_experience", []),
            "resume_text": parsed_data.get("resume_text", "")
        }
    }


@router.delete("/", response_model=dict)
def delete_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete user profile (privacy control)"""
    # Soft delete - deactivate account
    current_user.is_active = False
    db.commit()
    
    return {"message": "Profile deactivated successfully"}

