"""
Resume upload and parsing endpoints
Following RESUME_PARSING_PLAN.md specifications
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os

# Add ai directory to path (go up 3 levels from backend/app/routers/ to root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.database import get_db
from app import models, schemas
from app.utils.file_helpers import FileHelper
from app.dependencies import get_current_user
from app.config import settings
from ai.nlp import ResumeParser
from ai.llm import Summarizer, QuestionGenerator

router = APIRouter(prefix="/resume", tags=["resume"])

resume_parser = ResumeParser()

# Initialize AI services only if OpenAI API key is available
try:
    summarizer = Summarizer()
    question_generator = QuestionGenerator()
except (ValueError, Exception) as e:
    print(f"AI services not available: {e}")
    summarizer = None
    question_generator = None

file_helper = FileHelper()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Upload a resume file and extract structured data.
    
    Following RESUME_PARSING_PLAN.md Section 7:
    POST /resume/upload
    
    Request: form-data containing file
    Response: parsed resume data
    """
    # Validate file type
    if not file_helper.validate_file_type(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Supported: PDF, DOCX, TXT"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Save file
    file_path = file_helper.save_uploaded_file(
        file_content,
        file.filename,
        prefix="resume"
    )
    
    # Parse resume (Step 1-4: Upload, Text Extraction, NLP, Skill Extraction)
    try:
        parsed_data = resume_parser.parse_file(file_content, file.filename, use_ai=False)
    except Exception as e:
        # Clean up file on error
        file_helper.delete_file(file_path)
        raise HTTPException(status_code=400, detail=f"Error parsing resume: {str(e)}")
    
    # Format response as specified in plan
    response = {
        "parsed_resume": {
            "name": f"{parsed_data.get('first_name', '')} {parsed_data.get('last_name', '')}".strip(),
            "email": parsed_data.get("email"),
            "phone": parsed_data.get("phone"),
            "skills": parsed_data.get("skills", []),
            "education": [edu.get("institution", "") for edu in parsed_data.get("education", [])],
            "experience": f"{parsed_data.get('experience_years', 0)} years" if parsed_data.get('experience_years') else "Not specified",
            "work_experience": parsed_data.get("work_experience", []),
            "entities": parsed_data.get("entities", {}),
            "file_path": file_path
        }
    }
    
    return response


@router.post("/analyze", response_model=schemas.ResumeAnalysisResponse)
async def analyze_resume(
    resume_data: schemas.ResumeAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Send structured resume data for AI summarization and interview question generation.
    
    Following RESUME_PARSING_PLAN.md Section 7:
    POST /resume/analyze
    
    Response: AI summary and interview questions
    """
    if not summarizer:
        raise HTTPException(
            status_code=503,
            detail="AI analysis not available. OpenAI API key not configured."
        )
    
    # Convert request to parsed data format
    parsed_data = {
        "resume_text": resume_data.resume_text or "",
        "skills": resume_data.skills or [],
        "experience_years": resume_data.experience_years or 0.0,
        "education": resume_data.education or [],
        "work_experience": resume_data.work_experience or []
    }
    
    # Generate AI summary (Step 5: Semantic Enhancement)
    try:
        summary = summarizer.summarize_candidate(parsed_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )
    
    # Generate interview questions
    try:
        if question_generator:
            interview_questions = question_generator.generate_interview_questions(
                parsed_data,
                job_description=resume_data.job_description,
                num_questions=5
            )
        else:
            interview_questions = QuestionGenerator()._default_questions()
    except Exception as e:
        # Use default questions if generation fails
        interview_questions = QuestionGenerator()._default_questions()
    
    # Format response as specified in plan
    response = {
        "summary": summary,
        "interview_questions": interview_questions
    }
    
    return response

