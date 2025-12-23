"""
Candidate Ranking Endpoint
Following PARSING_WORKFLOW.md Section 7: Candidate Ranking
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os

# Add ai directory to path (go up 3 levels from backend/app/routers/ to root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.database import get_db
from app import models, schemas
from ai.embeddings import EmbeddingVectorizer, SimilarityCalculator
from ai import utils as ai_utils
from app.dependencies import require_recruiter

router = APIRouter(prefix="/ranking", tags=["ranking"])

# Lazy-load vectorizer only when needed to avoid unnecessary OpenAI API calls
_vectorizer = None

def get_vectorizer():
    """Get or create EmbeddingVectorizer (lazy initialization)"""
    global _vectorizer
    if _vectorizer is None:
        _vectorizer = EmbeddingVectorizer()
    return _vectorizer


@router.get("/job/{job_id}", response_model=List[schemas.RankedCandidateResponse])
def rank_candidates_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_recruiter)
):
    """
    Rank candidates for a specific job by semantic similarity.
    
    Following PARSING_WORKFLOW.md Section 7:
    - Generates embeddings for each parsed resume
    - Computes semantic similarity with job description
    - Returns ranked list of applicants
    """
    # Verify job belongs to recruiter
    job = db.query(models.Job).filter(
        models.Job.id == job_id,
        models.Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get all applicants for this job
    applicants = db.query(models.Applicant).filter(
        models.Applicant.job_id == job_id
    ).all()
    
    if not applicants:
        return []
    
    # Generate job description embedding (lazy-load vectorizer)
    vectorizer = get_vectorizer()
    job_text = f"{job.title}\n{job.description}\n{job.requirements or ''}"
    job_embedding = vectorizer.generate_embedding(job_text)
    
    # Get or generate resume embeddings
    ranked_candidates = []
    
    for applicant in applicants:
        # Try to get existing embedding
        embedding_record = db.query(models.Embedding).filter(
            models.Embedding.applicant_id == applicant.id,
            models.Embedding.job_id == job_id
        ).first()
        
        if embedding_record and embedding_record.embedding_vector:
            resume_embedding = embedding_record.embedding_vector
        else:
            # Generate new embedding
            resume_text = applicant.resume_text or ""
            if resume_text:
                resume_embedding = vectorizer.generate_embedding(resume_text)
                # Store embedding
                if not embedding_record:
                    embedding_record = models.Embedding(
                        applicant_id=applicant.id,
                        job_id=job_id,
                        embedding_vector=resume_embedding
                    )
                    db.add(embedding_record)
                else:
                    embedding_record.embedding_vector = resume_embedding
            else:
                resume_embedding = None
        
        # Calculate match score
        if resume_embedding:
            match_score = SimilarityCalculator.calculate_match_score(
                resume_embedding,
                job_embedding
            )
        else:
            match_score = applicant.overall_score or 0.0
        
        ranked_candidates.append({
            "applicant_id": applicant.id,
            "name": f"{applicant.first_name} {applicant.last_name}",
            "email": applicant.email,
            "match_score": match_score,
            "overall_score": applicant.overall_score or 0.0,
            "skills": applicant.skills or [],
            "experience_years": applicant.experience_years or 0.0,
            "ai_summary": applicant.ai_summary,
            "status": applicant.status
        })
    
    # Normalize scores per job posting (Stage 6: Normalization and Ranking)
    match_scores = [c["match_score"] for c in ranked_candidates]
    if match_scores and len(set(match_scores)) > 1:  # Only normalize if scores vary
        normalized_scores = ai_utils.normalize_scores(match_scores)
        for candidate, normalized_score in zip(ranked_candidates, normalized_scores):
            candidate["normalized_score"] = normalized_score
    else:
        # All scores are the same, use original scores
        for candidate in ranked_candidates:
            candidate["normalized_score"] = candidate["match_score"]
    
    # Sort by match score descending
    ranked_candidates.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Add rank number
    for idx, candidate in enumerate(ranked_candidates, 1):
        candidate["rank"] = idx
    
    db.commit()
    
    return ranked_candidates

