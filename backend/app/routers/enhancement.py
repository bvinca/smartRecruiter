"""
AI Enhancement Endpoints
Job description enhancement and resume analysis
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import sys
import os

# Add ai directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, require_recruiter
from ai.enhancement.job_description_enhancer import JobDescriptionEnhancer
from ai.enhancement.resume_analyzer import ResumeAnalyzer

router = APIRouter(prefix="/enhancement", tags=["enhancement"])

# Lazy-load enhancers
_job_enhancer = None
_resume_analyzer = None

def get_job_enhancer():
    """Get or create JobDescriptionEnhancer (lazy initialization)"""
    global _job_enhancer
    if _job_enhancer is None:
        _job_enhancer = JobDescriptionEnhancer()
    return _job_enhancer

def get_resume_analyzer():
    """Get or create ResumeAnalyzer (lazy initialization)"""
    global _resume_analyzer
    if _resume_analyzer is None:
        _resume_analyzer = ResumeAnalyzer()
    return _resume_analyzer


@router.post("/job-description", response_model=schemas.JobDescriptionEnhancementResponse)
def enhance_job_description(
    request: schemas.JobDescriptionEnhancementRequest,
    current_user: models.User = Depends(require_recruiter)
):
    """
    Enhance job description by analyzing for bias, clarity, and keyword optimization
    Only recruiters can use this feature
    """
    enhancer = get_job_enhancer()
    
    try:
        result = enhancer.enhance_job_description(
            job_description=request.description,
            job_title=request.title or ""
        )
        return result
    except Exception as e:
        import traceback
        print(f"Error enhancing job description: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error enhancing job description: {str(e)}"
        )


@router.post("/resume-analysis", response_model=schemas.ResumeFeedbackResponse)
def analyze_resume(
    request: schemas.ResumeFeedbackRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Analyze candidate resume and provide feedback
    Available to both applicants and recruiters
    """
    analyzer = get_resume_analyzer()
    
    try:
        result = analyzer.analyze_resume(
            resume_text=request.resume_text,
            job_description=request.job_description,
            job_requirements=request.job_requirements
        )
        return result
    except Exception as e:
        import traceback
        print(f"Error analyzing resume: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing resume: {str(e)}"
        )

