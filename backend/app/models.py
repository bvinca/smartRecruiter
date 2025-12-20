from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # "applicant" or "recruiter"
    first_name = Column(String(100))
    last_name = Column(String(100))
    company_name = Column(String(255))  # For recruiters
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    jobs = relationship("Job", back_populates="recruiter")
    applications = relationship("Application", back_populates="applicant_user")


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    location = Column(String(255))
    salary_range = Column(String(100))
    status = Column(String(50), default="active")  # active, closed, draft
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recruiter = relationship("User", back_populates="jobs")
    applicants = relationship("Applicant", back_populates="job")
    applications = relationship("Application", back_populates="job")


class Applicant(Base):
    __tablename__ = "applicants"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)  # Removed unique=True - same person can apply to multiple jobs
    phone = Column(String(50))
    
    # Resume data
    resume_text = Column(Text)
    resume_file_path = Column(String(500))
    resume_file_type = Column(String(50))  # pdf, docx, txt
    
    # Extracted information
    skills = Column(JSON)  # List of skills
    experience_years = Column(Float)
    education = Column(JSON)  # List of education entries
    work_experience = Column(JSON)  # List of work experiences
    
    # Scoring
    match_score = Column(Float, default=0.0)
    skill_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    
    # AI-generated content
    ai_summary = Column(Text)
    ai_feedback = Column(Text)
    interview_questions = Column(JSON)  # List of generated questions
    
    # Status
    status = Column(String(50), default="pending")  # pending, reviewing, shortlisted, rejected, hired
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="applicants")


class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=True)  # Link to parsed applicant data
    status = Column(String(50), default="pending")  # pending, reviewing, shortlisted, rejected, hired
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    applicant_user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")


class Embedding(Base):
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    embedding_vector = Column(JSON)  # Store embedding as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(500))
    meeting_link = Column(String(500))
    notes = Column(Text)
    status = Column(String(50), default="scheduled")  # scheduled, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    application = relationship("Application", backref="interviews")

