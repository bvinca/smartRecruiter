from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserResponse"


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str  # "applicant" or "recruiter"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None  # Required for recruiters
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """Validate password length (bcrypt has 72-byte limit)"""
        if not v:
            raise ValueError('Password cannot be empty')
        # Check byte length, not character length
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError('Password cannot be longer than 72 bytes. Please use a shorter password.')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """Validate password length (bcrypt has 72-byte limit)"""
        if not v:
            raise ValueError('Password cannot be empty')
        # Check byte length, not character length
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError('Password cannot be longer than 72 bytes.')
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Job Schemas
class JobBase(BaseModel):
    title: str
    description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: str = "active"


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: Optional[str] = None


class Job(JobBase):
    id: int
    recruiter_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Applicant Schemas
class ApplicantBase(BaseModel):
    job_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None


class ApplicantCreate(ApplicantBase):
    pass


class ApplicantUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class Applicant(ApplicantBase):
    id: int
    resume_text: Optional[str] = None
    resume_file_path: Optional[str] = None
    resume_file_type: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    match_score: float = 0.0
    skill_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    overall_score: float = 0.0
    ai_summary: Optional[str] = None
    ai_feedback: Optional[str] = None
    interview_questions: Optional[List[str]] = None
    status: str = "pending"
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Scoring Schemas
class ScoreRequest(BaseModel):
    applicant_id: int
    job_id: int


class ScoreResponse(BaseModel):
    applicant_id: int
    job_id: int
    match_score: float
    skill_score: float
    experience_score: float
    education_score: float
    overall_score: float
    explanation: Dict[str, Any]


# Summary Schemas
class SummaryRequest(BaseModel):
    applicant_id: int
    job_id: int


class SummaryResponse(BaseModel):
    applicant_id: int
    summary: str
    feedback: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


# Upload Schemas
class UploadResponse(BaseModel):
    applicant_id: int
    message: str
    extracted_data: Dict[str, Any]


# Application Schemas
class ApplicationBase(BaseModel):
    job_id: int


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class RegenerateQuestionsRequest(BaseModel):
    feedback: str
    num_questions: Optional[int] = 5


# AI Enhancement Schemas
class JobDescriptionEnhancementRequest(BaseModel):
    description: str
    title: Optional[str] = None


class JobDescriptionEnhancementResponse(BaseModel):
    improved_description: str
    identified_issues: List[str]
    explanation: str
    bias_detected: bool
    improvements: List[str]
    llm_available: bool


class ResumeFeedbackRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = None
    job_requirements: Optional[str] = None


class ResumeFeedbackResponse(BaseModel):
    missing_skills: List[str]
    suggested_phrasing: List[Dict[str, str]]
    summary_feedback: str
    strengths: List[str]
    weaknesses: List[str]
    keyword_suggestions: List[str]
    llm_available: bool


class FairnessAuditRequest(BaseModel):
    job_id: Optional[int] = None
    group_key: Optional[str] = "group"
    score_key: Optional[str] = "overall_score"
    threshold: Optional[float] = 10.0


class FairnessAuditResponse(BaseModel):
    bias_detected: bool
    bias_magnitude: float
    group_analysis: Dict[str, Dict[str, Any]]
    recommendations: List[str]
    statistical_significance: float
    message: str


class XAIExplanationRequest(BaseModel):
    applicant_id: int
    job_id: Optional[int] = None


class XAIExplanationResponse(BaseModel):
    skills_explanation: str
    experience_explanation: str
    education_explanation: str
    soft_skills_explanation: str
    strengths: List[str]
    weaknesses: List[str]
    overall_summary: str
    score_breakdown: Dict[str, Dict[str, Any]]
    llm_available: bool


class SkillGapAnalysisRequest(BaseModel):
    job_id: int
    applicant_id: int


class SkillGapAnalysisResponse(BaseModel):
    skill_matches: Dict[str, float]
    missing_skills: List[str]
    strong_matches: List[str]
    weak_matches: List[str]
    overall_alignment: float
    total_job_skills: int
    matched_skills: int
    message: str


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    applicant_id: Optional[int] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    job: Optional["Job"] = None
    applicant: Optional[Dict[str, Any]] = None  # Include applicant data with scores and AI content (if resume uploaded)
    user: Optional[Dict[str, Any]] = None  # Include user data if no resume uploaded
    match_score: Optional[float] = None  # For applicants to see their match score
    
    class Config:
        from_attributes = True


# Profile Schemas
class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    email: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Interview Schemas
class InterviewBase(BaseModel):
    application_id: int
    scheduled_at: datetime
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None


class InterviewCreate(InterviewBase):
    pass


class InterviewUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None  # scheduled, completed, cancelled


class InterviewResponse(InterviewBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Analytics Schemas
class AnalyticsResponse(BaseModel):
    total_jobs: int
    active_jobs: int
    total_applications: int
    pending_applications: int
    shortlisted_applications: int
    rejected_applications: int
    hired_applications: int
    average_score: float
    top_skills: List[Dict[str, Any]]
    applications_by_job: List[Dict[str, Any]]


# Resume Analysis Schemas (for POST /resume/analyze)
class ResumeAnalysisRequest(BaseModel):
    resume_text: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    job_description: Optional[str] = None  # Optional for context-aware questions


class ResumeAnalysisResponse(BaseModel):
    summary: str
    interview_questions: List[str]


# Ranking Schemas
class RankedCandidateResponse(BaseModel):
    rank: int
    applicant_id: int
    name: str
    email: str
    match_score: float
    overall_score: float
    skills: List[str]
    experience_years: float
    ai_summary: Optional[str] = None
    status: str


# Application Response with Parsed Data
class ParsedResumeData(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str]
    education: List[Dict[str, Any]]
    experience_years: float
    work_experience: List[Dict[str, Any]]
