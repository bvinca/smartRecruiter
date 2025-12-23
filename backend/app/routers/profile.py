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

# Lazy-load RAG pipeline only when needed
_rag_pipeline = None

def get_rag_pipeline():
    """Get or create RAGPipeline (lazy initialization)"""
    global _rag_pipeline
    if _rag_pipeline is None:
        try:
            from ai.rag import RAGPipeline
            _rag_pipeline = RAGPipeline()
        except (ValueError, Exception) as e:
            print(f"RAG pipeline not available: {e}")
            _rag_pipeline = None
    return _rag_pipeline


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


@router.post("/resume/generate-summary", response_model=dict)
def generate_resume_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate AI summary for current user's resume (applicant only)"""
    print(f"Generate summary called for user: {current_user.email}, role: {current_user.role}")
    
    if current_user.role != "applicant":
        raise HTTPException(status_code=403, detail="Only applicants can generate resume summaries")
    
    # Get the most recent application with parsed resume data
    latest_application = db.query(models.Application).filter(
        models.Application.user_id == current_user.id,
        models.Application.applicant_id.isnot(None)
    ).order_by(models.Application.created_at.desc()).first()
    
    print(f"Latest application: {latest_application}")
    
    applicant = None
    job = None
    
    if latest_application and latest_application.applicant_id:
        # Get the applicant record from application
        applicant = db.query(models.Applicant).filter(
            models.Applicant.id == latest_application.applicant_id
        ).first()
        
        if applicant:
            # Get the job for context
            job = db.query(models.Job).filter(models.Job.id == applicant.job_id).first() if applicant.job_id else None
    
    # If no applicant from application, try to find by email
    if not applicant:
        applicant = db.query(models.Applicant).filter(
            models.Applicant.email == current_user.email
        ).order_by(models.Applicant.created_at.desc()).first()
        
        if applicant and applicant.job_id:
            job = db.query(models.Job).filter(models.Job.id == applicant.job_id).first()
    
    if not applicant:
        raise HTTPException(
            status_code=404, 
            detail="No resume found. Please upload a resume when applying to a job first."
        )
    
    if not applicant.resume_text:
        raise HTTPException(
            status_code=404, 
            detail="Resume text not found. Please upload a resume with text content."
        )
    
    if not job:
        raise HTTPException(
            status_code=404, 
            detail="No job found for your resume. Please apply to a job first to generate an AI summary."
        )
    
    print(f"Using applicant: {applicant.id}, job: {job.id if job else 'None'}")
    
    # Get the applicant record
    applicant = db.query(models.Applicant).filter(
        models.Applicant.id == latest_application.applicant_id
    ).first()
    
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant record not found")
    
    # Get the job for context
    job = db.query(models.Job).filter(models.Job.id == applicant.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Generate summary using RAG pipeline
    rag_pipeline = get_rag_pipeline()
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="AI features not available. OpenAI API key not configured."
        )
    
    try:
        print(f"Calling RAG pipeline with resume_text length: {len(applicant.resume_text or '')}, job description: {job.description[:100] if job.description else 'None'}...")
        summary_data = rag_pipeline.generate_summary(
            resume_text=applicant.resume_text or "",
            job_description=job.description or ""
        )
        
        print(f"Summary data received: {summary_data}")
        
        # Only store summary if it's not the fallback error message
        summary_text = summary_data.get("summary", "")
        error_detail = summary_data.get("error", "")
        
        if summary_text and not summary_text.startswith("Unable to generate AI summary"):
            applicant.ai_summary = summary_text
            print(f"Storing summary: {summary_text[:100]}...")
        else:
            applicant.ai_summary = None
            if error_detail:
                print(f"Summary generation failed: {error_detail}")
            else:
                print("Summary is error message, not storing")
        
        # Generate interview questions
        try:
            questions = rag_pipeline.generate_interview_questions(
                resume_text=applicant.resume_text or "",
                job_description=job.description,
                num_questions=5
            )
            if questions and isinstance(questions, list) and len(questions) > 0:
                if not (isinstance(questions[0], str) and "Unable to generate" in questions[0]):
                    applicant.interview_questions = questions
                else:
                    applicant.interview_questions = None
            else:
                applicant.interview_questions = None
        except Exception as e:
            print(f"Error generating interview questions: {e}")
            applicant.interview_questions = None
        
        db.commit()
        db.refresh(applicant)
        
        # Return the actual summary from the data, not the stored value
        # (since we might not have stored it if it was an error)
        return_summary = summary_data.get("summary", "")
        error_detail = summary_data.get("error", "")
        
        if return_summary and return_summary.startswith("Unable to generate AI summary"):
            # If it's an error, return None so frontend knows it failed
            return_summary = None
        
        return {
            "message": "AI summary generated successfully" if return_summary else (error_detail or "AI summary generation failed"),
            "summary": return_summary,
            "strengths": summary_data.get("strengths", []),
            "weaknesses": summary_data.get("weaknesses", []),
            "recommendations": summary_data.get("recommendations", []),
            "interview_questions": applicant.interview_questions or [],
            "error": error_detail if error_detail else None
        }
    except Exception as e:
        import traceback
        print(f"Error generating summary: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating AI summary: {str(e)}"
        )


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

