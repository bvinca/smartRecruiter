from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add ai directory to path (go up 3 levels from backend/app/routers/ to root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.database import get_db
from app import models, schemas
from app.services.scoring_service import ScoringService
from ai.nlp import ResumeParser
from ai.rag import RAGPipeline
from ai.embeddings import EmbeddingVectorizer, SimilarityCalculator
from app.dependencies import get_current_user, require_applicant, require_recruiter
import uuid

router = APIRouter(prefix="/applications", tags=["applications"])

resume_parser = ResumeParser()
scoring_service = ScoringService()
rag_pipeline = RAGPipeline()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/apply/{job_id}", response_model=schemas.ApplicationResponse)
async def apply_to_job(
    job_id: int,
    file: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_applicant)
):
    """Apply to a job (applicant only)"""
    # Verify job exists and is active
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "active":
        raise HTTPException(status_code=400, detail="Job is not accepting applications")
    
    # Check if already applied
    existing_application = db.query(models.Application).filter(
        models.Application.user_id == current_user.id,
        models.Application.job_id == job_id
    ).first()
    if existing_application:
        raise HTTPException(status_code=400, detail="You have already applied to this job")
    
    applicant_id = None
    
    # If resume file provided, parse it and create applicant record
    if file:
        file_content = await file.read()
        
        # Save file
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_ext}")
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Parse resume (AI enhancement handled separately)
        try:
            parsed_data = resume_parser.parse_file(file_content, file.filename, use_ai=False)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing resume: {str(e)}")
        
        # Create applicant record
        applicant_data = {
            "job_id": job_id,
            "first_name": parsed_data.get("first_name") or current_user.first_name or "Unknown",
            "last_name": parsed_data.get("last_name") or current_user.last_name or "",
            "email": parsed_data.get("email") or current_user.email,
            "phone": parsed_data.get("phone"),
            "resume_text": parsed_data.get("resume_text", ""),
            "resume_file_path": file_path,
            "resume_file_type": file_ext,
            "skills": parsed_data.get("skills", []),
            "experience_years": parsed_data.get("experience_years", 0.0),
            "education": parsed_data.get("education", []),
            "work_experience": parsed_data.get("work_experience", [])
        }
        
        db_applicant = models.Applicant(**applicant_data)
        db.add(db_applicant)
        db.flush()
        applicant_id = db_applicant.id
        
        # Calculate scores
        try:
            scores = scoring_service.calculate_scores(
                resume_text=parsed_data.get("resume_text", ""),
                job_description=job.description,
                job_requirements=job.requirements or "",
                applicant_skills=parsed_data.get("skills", []),
                applicant_experience_years=parsed_data.get("experience_years", 0.0),
                applicant_education=parsed_data.get("education", []),
                applicant_work_experience=parsed_data.get("work_experience", [])
            )
            
            # Update applicant scores
            db_applicant.match_score = scores["match_score"]
            db_applicant.skill_score = scores["skill_score"]
            db_applicant.experience_score = scores["experience_score"]
            db_applicant.education_score = scores["education_score"]
            db_applicant.overall_score = scores["overall_score"]
            
            # Step 4: AI Processing (RAG + GPT) - Generate summary
            try:
                summary_data = rag_pipeline.generate_summary(
                    resume_text=parsed_data.get("resume_text", ""),
                    job_description=job.description
                )
                # Only store summary if it's not the fallback error message
                summary_text = summary_data.get("summary", "")
                if summary_text and summary_text != "Unable to generate AI summary at this time.":
                    db_applicant.ai_summary = summary_text
                else:
                    # Don't store fallback message - leave as None
                    db_applicant.ai_summary = None
            except Exception as e:
                print(f"Error generating summary with RAG: {e}")
                db_applicant.ai_summary = None
            
            # Generate interview questions
            try:
                if not db_applicant.interview_questions:
                    questions = rag_pipeline.generate_interview_questions(
                        resume_text=parsed_data.get("resume_text", ""),
                        job_description=job.description,
                        num_questions=5
                    )
                    db_applicant.interview_questions = questions
            except Exception as e:
                print(f"Error generating interview questions: {e}")
            
            # Store embeddings for semantic matching (Step 7: Candidate Ranking)
            try:
                vectorizer = EmbeddingVectorizer()
                resume_embedding = vectorizer.generate_embedding(
                    parsed_data.get("resume_text", "")
                )
                embedding = models.Embedding(
                    applicant_id=db_applicant.id,
                    job_id=job.id,
                    embedding_vector=resume_embedding
                )
                db.add(embedding)
            except Exception as e:
                print(f"Error storing embeddings: {e}")
                # Fallback to scores embedding if available
                if scores.get("resume_embedding"):
                    embedding = models.Embedding(
                        applicant_id=db_applicant.id,
                        job_id=job.id,
                        embedding_vector=scores.get("resume_embedding", [])
                    )
                    db.add(embedding)
        except Exception as e:
            # Continue even if scoring fails
            print(f"Error calculating scores: {e}")
    
    # Step 5: Database Storage - Commit all changes
    # Create application record
    application = models.Application(
        user_id=current_user.id,
        job_id=job_id,
        applicant_id=applicant_id,
        status="pending"
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    
    # Load applicant data if exists
    applicant_data = None
    if applicant_id:
        applicant_data = db.query(models.Applicant).filter(
            models.Applicant.id == applicant_id
        ).first()
    
    # Prepare response with parsed data (Step 6: Feedback to Applicant)
    # Match ApplicationResponse schema structure
    response_data = {
        "id": application.id,
        "user_id": application.user_id,
        "job_id": application.job_id,
        "applicant_id": application.applicant_id,
        "status": application.status,
        "notes": application.notes,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
        "job": job,  # Use the full job object - includes all required fields
        "applicant": None,  # Will be populated if resume was uploaded
        "match_score": None  # Will be populated if resume was uploaded
    }
    
    # Include parsed resume data for applicant feedback (matches ApplicationResponse schema)
    if applicant_data:
        response_data["applicant"] = {
            "id": applicant_data.id,
            "first_name": applicant_data.first_name,
            "last_name": applicant_data.last_name,
            "email": applicant_data.email,
            "phone": applicant_data.phone,
            "skills": applicant_data.skills or [],
            "experience_years": applicant_data.experience_years or 0.0,
            "education": applicant_data.education or [],
            "work_experience": applicant_data.work_experience or [],
            "match_score": applicant_data.match_score or 0.0,
            "skill_score": applicant_data.skill_score or 0.0,
            "experience_score": applicant_data.experience_score or 0.0,
            "education_score": applicant_data.education_score or 0.0,
            "overall_score": applicant_data.overall_score or 0.0,
            "ai_summary": applicant_data.ai_summary,
            "ai_feedback": applicant_data.ai_feedback,
            "interview_questions": applicant_data.interview_questions or [],
            "resume_text": applicant_data.resume_text,
            "resume_file_path": applicant_data.resume_file_path,
            "resume_file_type": applicant_data.resume_file_type
        }
        response_data["match_score"] = applicant_data.overall_score or 0.0
    else:
        # If no resume uploaded, include basic user info
        response_data["user"] = {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email
        }
    
    return response_data


@router.get("/", response_model=List[schemas.ApplicationResponse])
def get_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get applications (role-based access)"""
    from sqlalchemy.orm import joinedload
    
    if current_user.role == "applicant":
        # Applicants see only their own applications
        applications = db.query(models.Application).options(
            joinedload(models.Application.job)
        ).filter(
            models.Application.user_id == current_user.id
        ).order_by(models.Application.created_at.desc()).offset(skip).limit(limit).all()
    else:
        # Recruiters see applications for their jobs with applicant data
        applications = db.query(models.Application).options(
            joinedload(models.Application.job)
        ).join(models.Job).filter(
            models.Job.recruiter_id == current_user.id
        ).order_by(models.Application.created_at.desc()).offset(skip).limit(limit).all()
    
    # For each application, load the applicant data if it exists, and user data if no applicant
    result = []
    for app in applications:
        app_dict = {
            "id": app.id,
            "user_id": app.user_id,
            "job_id": app.job_id,
            "applicant_id": app.applicant_id,
            "status": app.status,
            "notes": app.notes,
            "created_at": app.created_at,
            "updated_at": app.updated_at,
            "job": app.job
        }
        
        # Load applicant data if available (has resume)
        if app.applicant_id:
            applicant = db.query(models.Applicant).filter(
                models.Applicant.id == app.applicant_id
            ).first()
            if applicant:
                # Add applicant data to response (will be accessible via applicant_id lookup on frontend)
                app_dict["applicant"] = {
                    "id": applicant.id,
                    "first_name": applicant.first_name,
                    "last_name": applicant.last_name,
                    "email": applicant.email,
                    "phone": applicant.phone,
                    "skills": applicant.skills,
                    "experience_years": applicant.experience_years,
                    "education": applicant.education,
                    "work_experience": applicant.work_experience,
                    "match_score": applicant.match_score,
                    "skill_score": applicant.skill_score,
                    "experience_score": applicant.experience_score,
                    "education_score": applicant.education_score,
                    "overall_score": applicant.overall_score,
                    "ai_summary": applicant.ai_summary,
                    "ai_feedback": applicant.ai_feedback,
                    "interview_questions": applicant.interview_questions,
                    "resume_text": applicant.resume_text,
                    "resume_file_path": applicant.resume_file_path,
                    "resume_file_type": applicant.resume_file_type
                }
                # Add match score for applicants to see
                app_dict["match_score"] = applicant.overall_score
        else:
            # No resume uploaded - include user information instead
            user = db.query(models.User).filter(models.User.id == app.user_id).first()
            if user:
                app_dict["user"] = {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": None  # User model doesn't have phone
                }
        
        result.append(app_dict)
    
    return result


@router.get("/{application_id}", response_model=schemas.ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific application"""
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check access
    if current_user.role == "applicant":
        if application.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    else:
        # Recruiter - check if job belongs to them
        job = db.query(models.Job).filter(models.Job.id == application.job_id).first()
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    return application


@router.put("/{application_id}", response_model=schemas.ApplicationResponse)
def update_application(
    application_id: int,
    application_update: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_recruiter)
):
    """Update application status (recruiter only)"""
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Verify job belongs to recruiter
    job = db.query(models.Job).filter(models.Job.id == application.job_id).first()
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = application_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    return application

