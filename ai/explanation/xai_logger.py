"""
XAI Logger - Logs all AI scoring explanations and decisions for auditing
Provides traceability and accountability for AI decisions
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import sys
import os
import json

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '../../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.models import AIAuditLog
except ImportError:
    AIAuditLog = None
    print("AIAuditLog model not available. Install backend dependencies.")


class XAILogger:
    """
    Logs AI scoring decisions and explanations for audit trail
    Ensures transparency and accountability in AI decision-making
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize the logger
        
        Args:
            db: Database session (optional, can be provided per call)
        """
        self.db = db
    
    def log_scoring_decision(
        self,
        applicant_id: int,
        job_id: int,
        scores: Dict[str, float],
        explanation: Optional[Dict[str, Any]] = None,
        bias_magnitude: Optional[float] = None,
        fairness_status: Optional[str] = None,
        scoring_method: Optional[str] = None,
        llm_available: bool = False,
        db: Optional[Session] = None
    ) -> Optional[int]:
        """
        Log an AI scoring decision to the audit log
        
        Args:
            applicant_id: ID of the applicant/candidate
            job_id: ID of the job
            scores: Dictionary with score breakdown
            explanation: Optional XAI explanation dictionary
            bias_magnitude: Optional bias magnitude if fairness audit was performed
            fairness_status: Optional fairness status (fair, warning, bias_detected)
            scoring_method: Method used for scoring (e.g., "hybrid", "semantic_only")
            llm_available: Whether LLM was available during scoring
            db: Database session (uses self.db if not provided)
            
        Returns:
            ID of the created audit log entry, or None if logging failed
        """
        if AIAuditLog is None:
            print("XAILogger: AIAuditLog model not available, skipping log")
            return None
        
        db_session = db or self.db
        if not db_session:
            print("XAILogger: No database session available, skipping log")
            return None
        
        try:
            # Prepare explanation data
            explanation_text = None
            explanation_json = None
            
            if explanation:
                if isinstance(explanation, dict):
                    explanation_json = explanation
                    # Extract text summary if available
                    if "overall_summary" in explanation:
                        explanation_text = explanation["overall_summary"]
                    elif "message" in explanation:
                        explanation_text = explanation["message"]
                    else:
                        explanation_text = json.dumps(explanation, indent=2)
                elif isinstance(explanation, str):
                    explanation_text = explanation
            
            # Create audit log entry
            audit_log = AIAuditLog(
                applicant_id=applicant_id,
                job_id=job_id,
                overall_score=scores.get("overall_score", 0.0),
                skill_score=scores.get("skill_score"),
                experience_score=scores.get("experience_score"),
                education_score=scores.get("education_score"),
                match_score=scores.get("match_score"),
                explanation=explanation_text,
                explanation_json=explanation_json,
                bias_magnitude=bias_magnitude,
                fairness_status=fairness_status,
                scoring_method=scoring_method,
                llm_available=llm_available
            )
            
            db_session.add(audit_log)
            db_session.commit()
            db_session.refresh(audit_log)
            
            print(f"XAILogger: Logged scoring decision for applicant {applicant_id}, job {job_id}")
            return audit_log.id
            
        except Exception as e:
            import traceback
            print(f"XAILogger: Error logging decision: {e}")
            print(f"XAILogger: Traceback: {traceback.format_exc()}")
            if db_session:
                db_session.rollback()
            return None
    
    def get_audit_history(
        self,
        applicant_id: Optional[int] = None,
        job_id: Optional[int] = None,
        limit: int = 100,
        db: Optional[Session] = None
    ) -> list:
        """
        Get audit log history
        
        Args:
            applicant_id: Optional applicant ID to filter
            job_id: Optional job ID to filter
            limit: Maximum number of records to return
            db: Database session (uses self.db if not provided)
            
        Returns:
            List of audit log entries
        """
        if AIAuditLog is None:
            return []
        
        db_session = db or self.db
        if not db_session:
            return []
        
        try:
            query = db_session.query(AIAuditLog)
            
            if applicant_id:
                query = query.filter(AIAuditLog.applicant_id == applicant_id)
            
            if job_id:
                query = query.filter(AIAuditLog.job_id == job_id)
            
            logs = query.order_by(AIAuditLog.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": log.id,
                    "applicant_id": log.applicant_id,
                    "job_id": log.job_id,
                    "overall_score": log.overall_score,
                    "skill_score": log.skill_score,
                    "experience_score": log.experience_score,
                    "education_score": log.education_score,
                    "match_score": log.match_score,
                    "explanation": log.explanation,
                    "explanation_json": log.explanation_json,
                    "bias_magnitude": log.bias_magnitude,
                    "fairness_status": log.fairness_status,
                    "scoring_method": log.scoring_method,
                    "llm_available": log.llm_available,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in logs
            ]
            
        except Exception as e:
            import traceback
            print(f"XAILogger: Error getting audit history: {e}")
            print(f"XAILogger: Traceback: {traceback.format_exc()}")
            return []

