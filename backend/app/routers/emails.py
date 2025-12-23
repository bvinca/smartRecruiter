"""
Email Router - API endpoints for AI-generated emails
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Applicant, Application
from app.schemas import EmailGenerateRequest, EmailGenerateResponse, EmailHistoryResponse, EmailSendRequest, EmailSendResponse
from app.dependencies import get_current_user
from app.services.email_service import EmailService

router = APIRouter(prefix="/emails", tags=["emails"])
email_service = EmailService()


@router.post("/applicants/{applicant_id}/generate", response_model=EmailGenerateResponse)
async def generate_email_for_applicant(
    applicant_id: int,
    request: EmailGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an AI email for a specific applicant
    
    Only recruiters can generate emails
    """
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can generate emails"
        )
    
    # Verify applicant exists
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Applicant with ID {applicant_id} not found"
        )
    
    # Verify job ownership (recruiter owns the job)
    from app.models import Job
    job = db.query(Job).filter(Job.id == applicant.job_id).first()
    if not job or job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to generate emails for this applicant"
        )
    
    try:
        result = email_service.generate_email_for_applicant(
            applicant_id=applicant_id,
            message_type=request.message_type,
            db=db,
            tone=request.tone,
            additional_context=request.additional_context
        )
        return EmailGenerateResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate email: {str(e)}"
        )


@router.post("/applications/{application_id}/generate", response_model=EmailGenerateResponse)
async def generate_email_for_application(
    application_id: int,
    request: EmailGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an AI email for a specific application
    
    Only recruiters can generate emails
    """
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can generate emails"
        )
    
    # Verify application exists
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )
    
    # Verify job ownership
    from app.models import Job
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job or job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to generate emails for this application"
        )
    
    try:
        result = email_service.generate_email_for_application(
            application_id=application_id,
            message_type=request.message_type,
            db=db,
            tone=request.tone,
            additional_context=request.additional_context
        )
        return EmailGenerateResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate email: {str(e)}"
        )


@router.get("/applicants/{applicant_id}/history", response_model=List[EmailHistoryResponse])
async def get_applicant_email_history(
    applicant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get email history for an applicant
    
    Only recruiters can view email history
    """
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view email history"
        )
    
    # Verify applicant exists and recruiter has access
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Applicant with ID {applicant_id} not found"
        )
    
    from app.models import Job
    job = db.query(Job).filter(Job.id == applicant.job_id).first()
    if not job or job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view email history for this applicant"
        )
    
    history = email_service.get_email_history(applicant_id=applicant_id, db=db)
    return [EmailHistoryResponse(**email) for email in history]


@router.get("/jobs/{job_id}/history", response_model=List[EmailHistoryResponse])
async def get_job_email_history(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get email history for all applicants of a job
    
    Only recruiters can view email history
    """
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view email history"
        )
    
    # Verify job exists and recruiter owns it
    from app.models import Job
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )
    
    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view email history for this job"
        )
    
    history = email_service.get_email_history(job_id=job_id, db=db)
    return [EmailHistoryResponse(**email) for email in history]


@router.post("/{email_id}/send", response_model=EmailSendResponse)
async def send_email(
    email_id: int,
    request: Optional[EmailSendRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a previously generated email
    
    Only recruiters can send emails
    """
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can send emails"
        )
    
    # Verify email exists and recruiter has access
    from app.models import EmailLog, Job
    email_log = db.query(EmailLog).filter(EmailLog.id == email_id).first()
    if not email_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email with ID {email_id} not found"
        )
    
    # Verify job ownership
    job = db.query(Job).filter(Job.id == email_log.job_id).first()
    if not job or job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to send this email"
        )
    
    try:
        subject = request.subject if request else None
        result = email_service.send_email(
            email_id=email_id,
            db=db,
            subject=subject
        )
        return EmailSendResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )

