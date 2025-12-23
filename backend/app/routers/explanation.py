"""
XAI Explanation Endpoints
Explainable AI for candidate scoring
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

# Add ai directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, require_recruiter
from ai.explanation.xai_explainer import XAIExplainer

router = APIRouter(prefix="/explanation", tags=["explanation"])

# Lazy-load explainer
_xai_explainer = None

def get_xai_explainer():
    """Get or create XAIExplainer (lazy initialization)"""
    global _xai_explainer
    if _xai_explainer is None:
        _xai_explainer = XAIExplainer()
    return _xai_explainer


@router.post("/scoring", response_model=schemas.XAIExplanationResponse)
def explain_scoring(
    request: schemas.XAIExplanationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Explain scoring breakdown for a candidate
    Available to both applicants and recruiters
    """
    # Get applicant
    applicant = db.query(models.Applicant).filter(
        models.Applicant.id == request.applicant_id
    ).first()
    
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    # Get job
    job = None
    if request.job_id:
        job = db.query(models.Job).filter(models.Job.id == request.job_id).first()
    elif applicant.job_id:
        job = db.query(models.Job).filter(models.Job.id == applicant.job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify access
    if current_user.role == "applicant":
        # Applicants can only see explanations for their own applications
        application = db.query(models.Application).filter(
            models.Application.applicant_id == applicant.id,
            models.Application.user_id == current_user.id
        ).first()
        if not application:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role == "recruiter":
        # Recruiters can only see explanations for their own jobs
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    # Prepare scores
    scores = {
        "skill_score": applicant.skill_score or 0.0,
        "experience_score": applicant.experience_score or 0.0,
        "education_score": applicant.education_score or 0.0,
        "match_score": applicant.match_score or 0.0,
        "overall_score": applicant.overall_score or 0.0
    }
    
    explainer = get_xai_explainer()
    
    try:
        result = explainer.explain_scoring(
            resume_text=applicant.resume_text or "",
            job_description=job.description or "",
            scores=scores,
            candidate_skills=applicant.skills or [],
            candidate_experience_years=applicant.experience_years or 0.0
        )
        return result
    except Exception as e:
        import traceback
        print(f"Error explaining scoring: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error explaining scoring: {str(e)}"
        )

