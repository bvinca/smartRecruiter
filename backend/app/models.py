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
    # Adaptive learning: Track recruiter decision for learning
    hire_decision = Column(Boolean, nullable=True)  # True = hired, False = rejected, None = pending
    ai_score_at_decision = Column(Float, nullable=True)  # Store AI score when decision was made
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


class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=True)  # Nullable for user-based applications
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    recipient_email = Column(String(255), nullable=False)
    message_type = Column(String(50), nullable=False)  # acknowledgment, feedback, rejection, interview_invitation
    email_content = Column(Text, nullable=False)
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    applicant = relationship("Applicant", backref="email_logs")
    job = relationship("Job", backref="email_logs")


class ScoringWeights(Base):
    """
    Stores adaptive scoring weights that learn from recruiter feedback
    Weights are adjusted based on hiring decisions vs AI predictions
    """
    __tablename__ = "scoring_weights"
    
    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null = global weights
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)  # Null = global, specific = job-specific
    
    # Adaptive weights (must sum to ~1.0)
    skill_weight = Column(Float, default=0.4, nullable=False)
    experience_weight = Column(Float, default=0.3, nullable=False)
    education_weight = Column(Float, default=0.1, nullable=False)
    semantic_similarity_weight = Column(Float, default=0.2, nullable=False)
    
    # Metadata
    iteration_count = Column(Integer, default=0)  # Number of learning iterations
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recruiter = relationship("User", backref="scoring_weights")
    job = relationship("Job", backref="scoring_weights")


class AIAuditLog(Base):
    """
    Audit log for AI scoring decisions and explanations
    Stores all AI scoring operations for traceability and accountability
    """
    __tablename__ = "ai_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Scoring data
    overall_score = Column(Float, nullable=False)
    skill_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)
    match_score = Column(Float, nullable=True)
    
    # Explanation data
    explanation = Column(Text, nullable=True)  # XAI explanation text
    explanation_json = Column(JSON, nullable=True)  # Structured explanation data
    
    # Fairness data
    bias_magnitude = Column(Float, nullable=True)
    fairness_status = Column(String(50), nullable=True)  # fair, warning, bias_detected
    
    # Metadata
    scoring_method = Column(String(100), nullable=True)  # e.g., "hybrid", "semantic_only"
    llm_available = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships - specify foreign_keys to avoid ambiguity
    applicant = relationship("Applicant", foreign_keys=[applicant_id], backref="audit_logs")
    job = relationship("Job", foreign_keys=[job_id], backref="audit_logs")


class FairnessMetric(Base):
    """
    Historical fairness metrics for tracking bias over time
    """
    __tablename__ = "fairness_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    
    # Fairness metrics
    mean_score_difference = Column(Float, nullable=False)  # MSD
    disparate_impact_ratio = Column(Float, nullable=False)  # DIR
    bias_magnitude = Column(Float, nullable=False)
    bias_detected = Column(Boolean, default=False)
    
    # Group analysis
    group_analysis = Column(JSON, nullable=True)  # Store group statistics
    
    # Demographic breakdown (if available)
    gender_breakdown = Column(JSON, nullable=True)
    experience_tier_breakdown = Column(JSON, nullable=True)
    education_level_breakdown = Column(JSON, nullable=True)
    
    # Metadata
    candidate_count = Column(Integer, nullable=False)
    threshold_used = Column(Float, default=10.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("Job", backref="fairness_metrics")
