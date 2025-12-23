"""
Feedback Router - Handles recruiter feedback for adaptive learning
Allows recruiters to submit hiring decisions to improve AI scoring
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Application, Applicant
from app.schemas import (
    FeedbackRequest, FeedbackResponse, WeightsResponse,
    ApplicationDecisionRequest
)
from app.dependencies import get_current_user, require_recruiter

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """
    Submit feedback data for adaptive learning
    Updates scoring weights based on recruiter decisions
    
    Only recruiters can submit feedback
    """
    try:
        from app.services.learning_service import AdaptiveWeightLearner
        
        learner = AdaptiveWeightLearner(db)
        
        # Convert feedback entries to format expected by learner
        feedback_data = []
        for entry in request.feedback_data:
            # Verify application exists and belongs to recruiter
            application = db.query(Application).filter(
                Application.id == entry.application_id
            ).first()
            
            if not application:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Application {entry.application_id} not found"
                )
            
            # Verify recruiter has access to this job
            job = db.query(Application.job).filter(Application.id == entry.application_id).first()
            if job and job.recruiter_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to provide feedback for this application"
                )
            
            # Get applicant scores if available
            applicant = None
            if application.applicant_id:
                applicant = db.query(Applicant).filter(Applicant.id == application.applicant_id).first()
            
            feedback_entry = {
                "ai_score": entry.ai_score or (applicant.overall_score if applicant else 0),
                "hired": entry.hired,
                "skill_score": entry.skill_score or (applicant.skill_score if applicant else 0),
                "experience_score": entry.experience_score or (applicant.experience_score if applicant else 0),
                "education_score": entry.education_score or (applicant.education_score if applicant else 0),
                "semantic_score": entry.semantic_score or (applicant.match_score if applicant else 0)
            }
            feedback_data.append(feedback_entry)
        
        # Update weights
        recruiter_id = request.recruiter_id or current_user.id
        updated_weights = learner.update_weights(
            feedback_data=feedback_data,
            recruiter_id=recruiter_id,
            job_id=request.job_id,
            learning_rate=request.learning_rate
        )
        
        # Get iteration count
        from app.models import ScoringWeights
        weights_record = None
        if recruiter_id and request.job_id:
            weights_record = db.query(ScoringWeights).filter(
                ScoringWeights.recruiter_id == recruiter_id,
                ScoringWeights.job_id == request.job_id
            ).first()
        elif recruiter_id:
            weights_record = db.query(ScoringWeights).filter(
                ScoringWeights.recruiter_id == recruiter_id,
                ScoringWeights.job_id.is_(None)
            ).first()
        elif request.job_id:
            weights_record = db.query(ScoringWeights).filter(
                ScoringWeights.recruiter_id.is_(None),
                ScoringWeights.job_id == request.job_id
            ).first()
        else:
            weights_record = db.query(ScoringWeights).filter(
                ScoringWeights.recruiter_id.is_(None),
                ScoringWeights.job_id.is_(None)
            ).first()
        
        iteration_count = weights_record.iteration_count if weights_record else 0
        
        return FeedbackResponse(
            success=True,
            message="Weights updated successfully",
            updated_weights=updated_weights,
            iteration_count=iteration_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error submitting feedback: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process feedback: {str(e)}"
        )


@router.post("/decision", response_model=dict)
async def record_decision(
    request: ApplicationDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """
    Record a hiring decision for an application
    This automatically triggers adaptive learning
    
    Only recruiters can record decisions
    """
    # Find application
    application = db.query(Application).filter(
        Application.id == request.application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {request.application_id} not found"
        )
    
    # Verify recruiter has access
    job = application.job
    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to make decisions for this application"
        )
    
    # Get applicant scores
    applicant = None
    if application.applicant_id:
        applicant = db.query(Applicant).filter(Applicant.id == application.applicant_id).first()
    
    # Update application
    application.status = "hired" if request.hired else "rejected"
    application.hire_decision = request.hired
    application.ai_score_at_decision = applicant.overall_score if applicant else None
    
    if request.notes:
        application.notes = request.notes
    
    db.commit()
    db.refresh(application)
    
    # Trigger adaptive learning
    try:
        from app.services.learning_service import AdaptiveWeightLearner
        
        learner = AdaptiveWeightLearner(db)
        
        # Collect recent feedback data
        feedback_data = learner.collect_feedback_data(
            recruiter_id=current_user.id,
            job_id=application.job_id,
            limit=20  # Use last 20 decisions
        )
        
        if len(feedback_data) >= 2:
            # Update weights
            learner.update_weights(
                feedback_data=feedback_data,
                recruiter_id=current_user.id,
                job_id=application.job_id,
                learning_rate=0.1
            )
    except Exception as e:
        print(f"Error in adaptive learning: {e}")
        # Don't fail the request if learning fails
    
    return {
        "success": True,
        "message": "Decision recorded and weights updated",
        "application_id": application.id,
        "decision": "hired" if request.hired else "rejected"
    }


@router.get("/weights", response_model=WeightsResponse)
async def get_weights(
    recruiter_id: Optional[int] = None,
    job_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current scoring weights
    Returns weights for specific recruiter/job or global weights
    """
    try:
        from app.services.learning_service import AdaptiveWeightLearner
        
        learner = AdaptiveWeightLearner(db)
        
        # Use current user's ID if recruiter and no ID specified
        if current_user.role == "recruiter" and recruiter_id is None:
            recruiter_id = current_user.id
        
        weights = learner.get_weights(recruiter_id, job_id)
        
        # Get weights record for metadata
        from app.models import ScoringWeights
        query = db.query(ScoringWeights)
        
        if recruiter_id and job_id:
            weights_record = query.filter(
                ScoringWeights.recruiter_id == recruiter_id,
                ScoringWeights.job_id == job_id
            ).first()
        elif recruiter_id:
            weights_record = query.filter(
                ScoringWeights.recruiter_id == recruiter_id,
                ScoringWeights.job_id.is_(None)
            ).first()
        elif job_id:
            weights_record = query.filter(
                ScoringWeights.recruiter_id.is_(None),
                ScoringWeights.job_id == job_id
            ).first()
        else:
            weights_record = query.filter(
                ScoringWeights.recruiter_id.is_(None),
                ScoringWeights.job_id.is_(None)
            ).first()
        
        return WeightsResponse(
            skill_weight=weights["skill_weight"],
            experience_weight=weights["experience_weight"],
            education_weight=weights["education_weight"],
            semantic_similarity_weight=weights["semantic_similarity_weight"],
            iteration_count=weights_record.iteration_count if weights_record else 0,
            last_updated=weights_record.last_updated.isoformat() if weights_record and weights_record.last_updated else None
        )
        
    except Exception as e:
        import traceback
        print(f"Error getting weights: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get weights: {str(e)}"
        )

