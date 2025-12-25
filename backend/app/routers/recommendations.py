"""
Recommendations Router - AI-powered job and candidate recommendations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add ai directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, require_recruiter
from ai.embeddings.recommender import Recommender

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Initialize recommender
recommender = Recommender()


@router.get("/jobs/{applicant_id}", response_model=List[dict])
async def get_job_recommendations(
    applicant_id: int,
    top_k: int = 5,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get job recommendations for an applicant
    Returns top jobs based on resume similarity
    """
    # Get applicant
    applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Applicant {applicant_id} not found"
        )
    
    # Verify access (applicant can see their own, recruiter can see any)
    if current_user.role == "applicant":
        # Check if this applicant belongs to the current user
        application = db.query(models.Application).filter(
            models.Application.applicant_id == applicant_id,
            models.Application.user_id == current_user.id
        ).first()
        if not application:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view recommendations for your own applications"
            )
    
    if not applicant.resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Applicant resume text is required for recommendations"
        )
    
    # Get all active jobs
    jobs = db.query(models.Job).filter(models.Job.status == "active").all()
    
    if not jobs:
        return []
    
    # Prepare job data
    job_data = [
        {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements or ""
        }
        for job in jobs
    ]
    
    # Get recommendations
    recommendations = recommender.recommend_jobs_for_candidate(
        candidate_resume_text=applicant.resume_text,
        available_jobs=job_data,
        top_k=top_k
    )
    
    # Get full job objects for recommended jobs
    recommended_job_ids = [rec["job_id"] for rec in recommendations]
    recommended_jobs = db.query(models.Job).filter(models.Job.id.in_(recommended_job_ids)).all()
    
    # Add similarity scores to job objects
    job_scores = {rec["job_id"]: rec["similarity_score"] for rec in recommendations}
    
    result = []
    for job in recommended_jobs:
        job_dict = {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "location": job.location,
            "salary_range": job.salary_range,
            "status": job.status,
            "recruiter_id": job.recruiter_id,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "similarity_score": job_scores.get(job.id, 0.0),
            "match_percentage": job_scores.get(job.id, 0.0)
        }
        result.append(job_dict)
    
    # Sort by similarity score
    result.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return result


@router.get("/candidates/{job_id}", response_model=List[dict])
async def get_candidate_recommendations(
    job_id: int,
    top_k: int = 5,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_recruiter)
):
    """
    Get candidate recommendations for a job
    Returns top candidates based on resume similarity
    Only recruiters can access this
    """
    # Get job
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    # Verify recruiter owns this job
    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view recommendations for your own jobs"
        )
    
    # Get all applicants with resume text
    applicants = db.query(models.Applicant).filter(
        models.Applicant.resume_text.isnot(None),
        models.Applicant.resume_text != ""
    ).all()
    
    if not applicants:
        return []
    
    # Prepare candidate data
    candidate_data = [
        {
            "id": applicant.id,
            "resume_text": applicant.resume_text,
            "name": f"{applicant.first_name} {applicant.last_name}",
            "email": applicant.email
        }
        for applicant in applicants
    ]
    
    # Get recommendations
    recommendations = recommender.recommend_candidates_for_job(
        job_description=job.description,
        job_requirements=job.requirements or "",
        available_candidates=candidate_data,
        top_k=top_k
    )
    
    # Get full applicant objects
    recommended_ids = [rec["candidate_id"] for rec in recommendations]
    recommended_applicants = db.query(models.Applicant).filter(
        models.Applicant.id.in_(recommended_ids)
    ).all()
    
    # Create result with similarity scores
    candidate_scores = {rec["candidate_id"]: rec["similarity_score"] for rec in recommendations}
    
    result = []
    for applicant in recommended_applicants:
        result.append({
            "id": applicant.id,
            "first_name": applicant.first_name,
            "last_name": applicant.last_name,
            "email": applicant.email,
            "phone": applicant.phone,
            "skills": applicant.skills,
            "experience_years": applicant.experience_years,
            "overall_score": applicant.overall_score,
            "similarity_score": candidate_scores.get(applicant.id, 0.0),
            "match_percentage": candidate_scores.get(applicant.id, 0.0)
        })
    
    # Sort by similarity score
    result.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return result


@router.get("/similar/{applicant_id}", response_model=List[dict])
async def get_similar_candidates(
    applicant_id: int,
    top_k: int = 5,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_recruiter)
):
    """
    Find candidates similar to a reference candidate
    Useful for recruiters to find candidates with similar profiles
    Only recruiters can access this
    """
    # Get reference applicant
    reference_applicant = db.query(models.Applicant).filter(
        models.Applicant.id == applicant_id
    ).first()
    
    if not reference_applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Applicant {applicant_id} not found"
        )
    
    if not reference_applicant.resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reference applicant resume text is required"
        )
    
    # Get all other applicants with resume text
    other_applicants = db.query(models.Applicant).filter(
        models.Applicant.id != applicant_id,
        models.Applicant.resume_text.isnot(None),
        models.Applicant.resume_text != ""
    ).all()
    
    if not other_applicants:
        return []
    
    # Prepare candidate data
    candidate_data = [
        {
            "id": applicant.id,
            "resume_text": applicant.resume_text,
            "name": f"{applicant.first_name} {applicant.last_name}",
            "email": applicant.email
        }
        for applicant in other_applicants
    ]
    
    # Find similar candidates
    similar = recommender.find_similar_candidates(
        reference_candidate_resume=reference_applicant.resume_text,
        other_candidates=candidate_data,
        top_k=top_k
    )
    
    # Get full applicant objects
    similar_ids = [s["candidate_id"] for s in similar]
    similar_applicants = db.query(models.Applicant).filter(
        models.Applicant.id.in_(similar_ids)
    ).all()
    
    # Create result with similarity scores
    similarity_scores = {s["candidate_id"]: s["similarity_score"] for s in similar}
    
    result = []
    for applicant in similar_applicants:
        result.append({
            "id": applicant.id,
            "first_name": applicant.first_name,
            "last_name": applicant.last_name,
            "email": applicant.email,
            "skills": applicant.skills,
            "experience_years": applicant.experience_years,
            "overall_score": applicant.overall_score,
            "similarity_score": similarity_scores.get(applicant.id, 0.0),
            "match_percentage": similarity_scores.get(applicant.id, 0.0)
        })
    
    # Sort by similarity score
    result.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return result

