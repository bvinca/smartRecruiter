from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
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
from app.dependencies import get_current_user, require_recruiter
import uuid

router = APIRouter(prefix="/applicants", tags=["applicants"])

resume_parser = ResumeParser()
scoring_service = ScoringService()

# Lazy-load RAG pipeline only when needed to avoid unnecessary OpenAI API calls
_rag_pipeline = None

def get_rag_pipeline():
    """Get or create RAGPipeline (lazy initialization)"""
    global _rag_pipeline
    if _rag_pipeline is None:
        try:
            _rag_pipeline = RAGPipeline()
        except (ValueError, Exception) as e:
            print(f"RAG pipeline not available: {e}")
            _rag_pipeline = None
    return _rag_pipeline

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=schemas.UploadResponse)
async def upload_cv(
    job_id: int,
    file: UploadFile = File(...),
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Upload and parse a CV/resume"""
    # Verify job exists
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Read file content
    file_content = await file.read()
    
    # Save file
    file_ext = file.filename.split('.')[-1]
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
        "first_name": parsed_data.get("first_name") or first_name or "Unknown",
        "last_name": parsed_data.get("last_name") or last_name or "",
        "email": parsed_data.get("email") or email or f"{file_id}@example.com",
        "phone": parsed_data.get("phone") or phone,
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
    db.commit()
    db.refresh(db_applicant)
    
    return {
        "applicant_id": db_applicant.id,
        "message": "Resume uploaded and parsed successfully",
        "extracted_data": {
            "skills": parsed_data.get("skills", []),
            "experience_years": parsed_data.get("experience_years", 0.0),
            "education": parsed_data.get("education", []),
            "work_experience": parsed_data.get("work_experience", [])
        }
    }


@router.get("/", response_model=List[schemas.Applicant])
def get_applicants(
    job_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get applicants (role-based access)"""
    if current_user.role == "recruiter":
        # Recruiters see applicants for their jobs only
        query = db.query(models.Applicant).join(models.Job).filter(
            models.Job.recruiter_id == current_user.id
        )
        if job_id:
            # Verify job belongs to recruiter
            job = db.query(models.Job).filter(
                models.Job.id == job_id,
                models.Job.recruiter_id == current_user.id
            ).first()
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            query = query.filter(models.Applicant.job_id == job_id)
    else:
        # Applicants see only their own applications
        # This would require linking applicants to users
        # For now, return empty or implement application linking
        query = db.query(models.Applicant).filter(
            models.Applicant.email == current_user.email
        )
        if job_id:
            query = query.filter(models.Applicant.job_id == job_id)
    
    applicants = query.order_by(models.Applicant.overall_score.desc()).offset(skip).limit(limit).all()
    return applicants


@router.get("/{applicant_id}", response_model=schemas.Applicant)
def get_applicant(
    applicant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific applicant by ID (role-based access)"""
    applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    # Check access - recruiters can see applicants for their jobs, applicants can see their own
    if current_user.role == "recruiter":
        job = db.query(models.Job).filter(models.Job.id == applicant.job_id).first()
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    # Applicants can't directly access applicant records, they use applications
    
    return applicant


@router.post("/{applicant_id}/score", response_model=schemas.ScoreResponse)
def score_applicant(applicant_id: int, db: Session = Depends(get_db)):
    """Calculate and update scores for an applicant"""
    applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    job = db.query(models.Job).filter(models.Job.id == applicant.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Calculate scores
    scores = scoring_service.calculate_scores(
        resume_text=applicant.resume_text or "",
        job_description=job.description,
        job_requirements=job.requirements or "",
        applicant_skills=applicant.skills or [],
        applicant_experience_years=applicant.experience_years or 0.0,
        applicant_education=applicant.education or [],
        applicant_work_experience=applicant.work_experience or []
    )
    
    # Update applicant scores
    applicant.match_score = scores["match_score"]
    applicant.skill_score = scores["skill_score"]
    applicant.experience_score = scores["experience_score"]
    applicant.education_score = scores["education_score"]
    applicant.overall_score = scores["overall_score"]
    
    # Store embeddings
    embedding = models.Embedding(
        applicant_id=applicant.id,
        job_id=job.id,
        embedding_vector=scores["resume_embedding"]
    )
    db.add(embedding)
    
    db.commit()
    db.refresh(applicant)
    
    return {
        "applicant_id": applicant.id,
        "job_id": job.id,
        "match_score": scores["match_score"],
        "skill_score": scores["skill_score"],
        "experience_score": scores["experience_score"],
        "education_score": scores["education_score"],
        "overall_score": scores["overall_score"],
        "explanation": scores["explanation"]
    }


@router.post("/{applicant_id}/summary", response_model=schemas.SummaryResponse)
def generate_summary(applicant_id: int, db: Session = Depends(get_db)):
    """Generate AI summary and feedback for applicant"""
    applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    job = db.query(models.Job).filter(models.Job.id == applicant.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Generate summary
    rag_pipeline = get_rag_pipeline()
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="AI features not available. OpenAI API key not configured."
        )
    
    summary_data = rag_pipeline.generate_summary(
        resume_text=applicant.resume_text or "",
        job_description=job.description
    )
    
    # Generate feedback
    scores = {
        "match_score": applicant.match_score,
        "skill_score": applicant.skill_score,
        "experience_score": applicant.experience_score
    }
    feedback = rag_pipeline.generate_feedback(
        resume_text=applicant.resume_text or "",
        job_description=job.description,
        scores=scores
    )
    
    # Generate interview questions
    questions = rag_pipeline.generate_interview_questions(
        resume_text=applicant.resume_text or "",
        job_description=job.description,
        num_questions=5
    )
    
    # Update applicant record - only store if not fallback messages
    summary_text = summary_data.get("summary", "")
    if summary_text and summary_text != "Unable to generate AI summary at this time.":
        applicant.ai_summary = summary_text
    else:
        applicant.ai_summary = None
    
    # Only store feedback if it's not an error message
    if feedback and feedback != "Unable to generate AI feedback at this time.":
        applicant.ai_feedback = feedback
    else:
        applicant.ai_feedback = None
    
    # Only store questions if they're valid (not error messages)
    if questions and isinstance(questions, list) and len(questions) > 0:
        # Check if first question is not an error message
        if not (isinstance(questions[0], str) and "Unable to generate" in questions[0]):
            applicant.interview_questions = questions
        else:
            applicant.interview_questions = None
    else:
        applicant.interview_questions = None
    
    db.commit()
    db.refresh(applicant)
    
    return {
        "applicant_id": applicant.id,
        "summary": summary_data["summary"],
        "feedback": feedback,
        "strengths": summary_data["strengths"],
        "weaknesses": summary_data["weaknesses"],
        "recommendations": summary_data["recommendations"]
    }


@router.post("/{applicant_id}/regenerate-questions", response_model=dict)
def regenerate_questions(
    applicant_id: int,
    request: schemas.RegenerateQuestionsRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_recruiter)
):
    """
    Regenerate interview questions based on recruiter feedback
    Only recruiters can provide feedback and regenerate questions
    """
    applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    # Get the job to access job description
    job = db.query(models.Job).filter(models.Job.id == applicant.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify the recruiter owns this job
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only regenerate questions for applicants in your own jobs")
    
    # Check if applicant has interview questions
    if not applicant.interview_questions or len(applicant.interview_questions) == 0:
        raise HTTPException(
            status_code=400,
            detail="No existing interview questions found. Please generate questions first."
        )
    
    # Get RAG pipeline
    rag_pipeline = get_rag_pipeline()
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="AI features not available. OpenAI API key not configured."
        )
    
    try:
        print(f"Regenerating questions for applicant {applicant_id} with feedback: {request.feedback[:100]}...")
        
        # Regenerate questions with feedback
        new_questions = rag_pipeline.regenerate_questions_with_feedback(
            resume_text=applicant.resume_text or "",
            current_questions=applicant.interview_questions,
            feedback=request.feedback,
            job_description=job.description or "",
            num_questions=request.num_questions or 5
        )
        
        # Check if questions are valid (not default/error messages)
        if new_questions and isinstance(new_questions, list) and len(new_questions) > 0:
            default_questions = [
                "Tell me about your experience with the technologies mentioned in this role.",
                "Describe a challenging project you worked on and how you solved it.",
                "How do you stay updated with industry trends?",
                "What motivates you in your career?",
                "Why are you interested in this position?"
            ]
            is_default = new_questions[0] in default_questions if new_questions else False
            
            if not is_default:
                # Update applicant with new questions
                applicant.interview_questions = new_questions
                db.commit()
                db.refresh(applicant)
                
                print(f"Successfully regenerated and stored {len(new_questions)} interview questions")
                return {
                    "success": True,
                    "message": f"Successfully regenerated {len(new_questions)} interview questions",
                    "questions": new_questions
                }
            else:
                return {
                    "success": False,
                    "message": "Regenerated questions appear to be default/placeholder questions. Please check your OpenAI API quota.",
                    "questions": applicant.interview_questions  # Return original questions
                }
        else:
            return {
                "success": False,
                "message": "Failed to regenerate questions. Please try again.",
                "questions": applicant.interview_questions  # Return original questions
            }
    except Exception as e:
        import traceback
        print(f"Error regenerating questions: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error regenerating questions: {str(e)}"
        )


@router.put("/{applicant_id}", response_model=schemas.Applicant)
def update_applicant(
    applicant_id: int,
    applicant_update: schemas.ApplicantUpdate,
    db: Session = Depends(get_db)
):
    """Update applicant information"""
    db_applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not db_applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    update_data = applicant_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_applicant, field, value)
    
    db.commit()
    db.refresh(db_applicant)
    return db_applicant


@router.get("/{applicant_id}/download")
def download_resume(
    applicant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_recruiter)
):
    """Download resume file (recruiter only)"""
    applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    # Verify job belongs to recruiter
    job = db.query(models.Job).filter(models.Job.id == applicant.job_id).first()
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not applicant.resume_file_path or not os.path.exists(applicant.resume_file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
    
    return FileResponse(
        applicant.resume_file_path,
        media_type="application/pdf" if applicant.resume_file_type == "pdf" else "application/msword",
        filename=f"{applicant.first_name}_{applicant.last_name}_resume.{applicant.resume_file_type}"
    )

