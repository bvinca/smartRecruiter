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
from ai.nlp.multilingual_parser import MultilingualResumeParser
from ai.llm import Summarizer, QuestionGenerator
from ai.enhancement.resume_analyzer import ResumeAnalyzer

router = APIRouter(prefix="/resume", tags=["resume"])

resume_parser = ResumeParser()
multilingual_parser = MultilingualResumeParser()
resume_analyzer = ResumeAnalyzer()

# Lazy-load AI services only when needed to avoid unnecessary OpenAI API calls
_summarizer = None
_question_generator = None

def get_summarizer():
    """Get or create Summarizer (lazy initialization)"""
    global _summarizer
    if _summarizer is None:
        try:
            _summarizer = Summarizer()
        except (ValueError, Exception) as e:
            print(f"AI summarizer not available: {e}")
            _summarizer = None
    return _summarizer

def get_question_generator():
    """Get or create QuestionGenerator (lazy initialization)"""
    global _question_generator
    if _question_generator is None:
        try:
            _question_generator = QuestionGenerator()
        except (ValueError, Exception) as e:
            print(f"AI question generator not available: {e}")
            _question_generator = None
    return _question_generator

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
    # Lazy-load AI services only when needed
    summarizer = get_summarizer()
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
    question_generator = get_question_generator()
    try:
        if question_generator:
            interview_questions = question_generator.generate_interview_questions(
                parsed_data,
                job_description=resume_data.job_description,
                num_questions=5
            )
        else:
            question_gen = get_question_generator()
            if question_gen:
                interview_questions = question_gen._default_questions()
            else:
                # Fallback to default questions
                from ai.llm.question_generator import QuestionGenerator as QG
                interview_questions = QG()._default_questions()
    except Exception as e:
        # Use default questions if generation fails
        question_gen = get_question_generator()
        if question_gen:
            interview_questions = question_gen._default_questions()
        else:
            from ai.llm.question_generator import QuestionGenerator as QG
            interview_questions = QG()._default_questions()
    
    # Format response as specified in plan
    response = {
        "summary": summary,
        "interview_questions": interview_questions
    }
    
    return response


@router.post("/analyze-feedback", response_model=schemas.ResumeFeedbackResponse)
async def analyze_resume_feedback(
    request: schemas.ResumeFeedbackRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Analyze resume and provide constructive feedback to candidate
    Compares resume against job description to identify improvements
    Available to both applicants and recruiters
    """
    try:
        result = resume_analyzer.analyze_resume(
            resume_text=request.resume_text,
            job_description=request.job_description,
            job_requirements=request.job_requirements
        )
        return result
    except Exception as e:
        import traceback
        print(f"Error analyzing resume feedback: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing resume: {str(e)}"
        )


@router.post("/upload-multilingual")
async def upload_resume_multilingual(
    file: UploadFile = File(...),
    translate_to_english: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Upload a resume file with multilingual support
    Automatically detects language and optionally translates to English
    """
    # Validate file type
    if not file_helper.validate_file_type(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Supported: PDF, DOCX, TXT"
        )
    
    # Read file content
    file_content = await file.read()
    
    try:
        # Parse with multilingual support
        parsed_data = multilingual_parser.parse_file(
            file_content=file_content,
            filename=file.filename,
            use_ai=False,
            detect_language=True,
            translate_to_english=translate_to_english
        )
        
        return {
            "success": True,
            "parsed_data": parsed_data,
            "detected_language": parsed_data.get("detected_language", "en"),
            "translated": translate_to_english and parsed_data.get("detected_language") != "en"
        }
    except Exception as e:
        import traceback
        print(f"Error parsing multilingual resume: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing resume: {str(e)}"
        )

