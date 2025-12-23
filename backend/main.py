import sys
import os

# Add root directory to path so ai/ module can be imported
# Go up 2 levels from backend/main.py to root
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import jobs, applicants, auth, applications, profile, interviews, analytics, resume, ranking, enhancement, fairness, explanation, visualization, emails, feedback
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartRecruiter API",
    description="AI-powered Applicant Tracking System with RAG capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applicants.router)
app.include_router(applications.router)
app.include_router(profile.router)
app.include_router(interviews.router)
app.include_router(analytics.router)
app.include_router(resume.router)  # Resume parsing endpoints
app.include_router(ranking.router)  # Candidate ranking
app.include_router(enhancement.router)  # AI enhancement features
app.include_router(fairness.router)  # Fairness auditing
app.include_router(explanation.router)  # XAI explanations
app.include_router(visualization.router)  # Skill gap visualization
app.include_router(emails.router)  # AI email generation
app.include_router(feedback.router)  # Adaptive learning feedback

# Serve visualization images
import os
reports_dir = os.path.join(os.path.dirname(__file__), '../ai/reports')
if os.path.exists(reports_dir):
    app.mount("/reports", StaticFiles(directory=reports_dir), name="reports")


@app.get("/")
def read_root():
    return {
        "status": "SmartRecruiter API Running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/debug/openai-status")
def check_openai_status():
    """Debug endpoint to check OpenAI API key configuration and test quota"""
    from app.config import settings
    
    api_key = settings.OPENAI_API_KEY
    has_key = bool(api_key and api_key.strip())
    key_length = len(api_key) if api_key else 0
    key_preview = api_key[:10] + "..." if api_key and len(api_key) > 10 else "N/A"
    
    # Try to initialize OpenAIClient
    client_status = "not_initialized"
    error_message = None
    quota_status = "unknown"
    quota_error = None
    
    try:
        from ai.llm.openai_client import OpenAIClient
        client = OpenAIClient()
        client_status = "initialized"
        
        # Test the API with a minimal request to check quota
        try:
            test_response = client.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'OK'"}],
                max_tokens=5
            )
            quota_status = "available"
            quota_error = None
        except Exception as quota_test_error:
            error_str = str(quota_test_error)
            if "quota" in error_str.lower() or "insufficient_quota" in error_str.lower() or "429" in error_str:
                quota_status = "exceeded"
                quota_error = "OpenAI API quota exceeded. Please add credits to your OpenAI account at https://platform.openai.com/account/billing"
            elif "rate limit" in error_str.lower():
                quota_status = "rate_limited"
                quota_error = "OpenAI API rate limit exceeded. Please wait a moment and try again."
            elif "invalid" in error_str.lower() and "api key" in error_str.lower():
                quota_status = "invalid_key"
                quota_error = "Invalid OpenAI API key. Please check your API key."
            else:
                quota_status = "error"
                quota_error = f"API test failed: {error_str}"
                
    except Exception as e:
        client_status = "failed"
        error_message = str(e)
    
    return {
        "api_key_configured": has_key,
        "api_key_length": key_length,
        "api_key_preview": key_preview,
        "api_key_starts_with_sk": api_key.startswith("sk-") if api_key else False,
        "openai_client_status": client_status,
        "quota_status": quota_status,
        "quota_error": quota_error,
        "error": error_message,
        "model_selection": {
            "embedding_model": settings.EMBEDDING_MODEL,
            "summarization_model": settings.SUMMARIZATION_MODEL,
            "question_generation_model": settings.QUESTION_GENERATION_MODEL
        },
        "action_required": "Add credits to your OpenAI account at https://platform.openai.com/account/billing" if quota_status == "exceeded" else None
    }