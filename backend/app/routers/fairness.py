"""
AI Fairness Auditor Endpoints
Detect bias in recruitment decisions
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import sys
import os

# Add ai directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.database import get_db
from app import models, schemas
from app.dependencies import require_recruiter
from ai.evaluation.fairness_checker import FairnessChecker

router = APIRouter(prefix="/fairness", tags=["fairness"])

# Lazy-load fairness checker
_fairness_checker = None

def get_fairness_checker():
    """Get or create FairnessChecker (lazy initialization)"""
    global _fairness_checker
    if _fairness_checker is None:
        _fairness_checker = FairnessChecker()
    return _fairness_checker


@router.post("/audit", response_model=schemas.FairnessAuditResponse)
def audit_fairness(
    request: schemas.FairnessAuditRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_recruiter)
):
    """
    Audit fairness for a job posting
    Analyzes scoring data across candidate groups to detect bias
    Only recruiters can access this
    """
    fairness_checker = get_fairness_checker()
    
    # Get applicants for the job
    if request.job_id:
        # Verify job belongs to recruiter
        job = db.query(models.Job).filter(
            models.Job.id == request.job_id,
            models.Job.recruiter_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get all applicants for this job
        applicants = db.query(models.Applicant).filter(
            models.Applicant.job_id == request.job_id
        ).all()
        
        if len(applicants) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 applicants to perform fairness audit"
            )
        
        # Prepare candidate data for analysis
        # Group by education type (STEM vs non-STEM) as example
        candidate_data = []
        for applicant in applicants:
            # Determine group based on education
            group = "unknown"
            if applicant.education:
                education_text = " ".join([
                    edu.get("degree", "") + " " + edu.get("institution", "")
                    for edu in applicant.education
                ]).lower()
                
                stem_keywords = ['computer', 'engineering', 'science', 'technology', 'math', 'statistics']
                if any(keyword in education_text for keyword in stem_keywords):
                    group = "stem"
                else:
                    group = "non_stem"
            else:
                group = "no_education"
            
            candidate_data.append({
                "group": group,
                "overall_score": applicant.overall_score or 0.0,
                "skill_score": applicant.skill_score or 0.0,
                "experience_score": applicant.experience_score or 0.0,
                "experience_years": applicant.experience_years or 0.0
            })
    else:
        # Audit all applicants (for admin/global analysis)
        applicants = db.query(models.Applicant).all()
        
        if len(applicants) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 applicants to perform fairness audit"
            )
        
        candidate_data = []
        for applicant in applicants:
            group = "unknown"
            if applicant.education:
                education_text = " ".join([
                    edu.get("degree", "") + " " + edu.get("institution", "")
                    for edu in applicant.education
                ]).lower()
                
                stem_keywords = ['computer', 'engineering', 'science', 'technology', 'math', 'statistics']
                if any(keyword in education_text for keyword in stem_keywords):
                    group = "stem"
                else:
                    group = "non_stem"
            else:
                group = "no_education"
            
            candidate_data.append({
                "group": group,
                "overall_score": applicant.overall_score or 0.0,
                "skill_score": applicant.skill_score or 0.0,
                "experience_score": applicant.experience_score or 0.0,
                "experience_years": applicant.experience_years or 0.0
            })
    
    try:
        result = fairness_checker.audit_fairness(
            candidate_data=candidate_data,
            group_key=request.group_key,
            score_key=request.score_key,
            threshold=request.threshold
        )
        return result
    except Exception as e:
        import traceback
        print(f"Error auditing fairness: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error auditing fairness: {str(e)}"
        )

