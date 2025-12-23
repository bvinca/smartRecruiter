"""
Adaptive Learning Service - Learns from recruiter feedback
Adjusts scoring weights dynamically based on hiring decisions
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("numpy not available. Install with: pip install numpy")

try:
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not available. Install with: pip install scikit-learn")

from app.models import ScoringWeights, Application, Applicant


# Default weights as per AI_FEATURE_IMPLEMENTATION_PLAN.md
DEFAULT_WEIGHTS = {
    "skill_weight": 0.4,
    "experience_weight": 0.3,
    "education_weight": 0.1,
    "semantic_similarity_weight": 0.2
}


class AdaptiveWeightLearner:
    """
    Learns optimal scoring weights from recruiter feedback
    Uses gradient-based updates to adjust weights based on hiring decisions
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_weights(
        self,
        recruiter_id: Optional[int] = None,
        job_id: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Get current scoring weights for a recruiter/job combination
        Returns default weights if none exist
        
        Args:
            recruiter_id: Optional recruiter ID for personalized weights
            job_id: Optional job ID for job-specific weights
            
        Returns:
            Dictionary with weight values
        """
        # Try to find existing weights
        query = self.db.query(ScoringWeights)
        
        if recruiter_id and job_id:
            # Most specific: recruiter + job
            weights = query.filter(
                ScoringWeights.recruiter_id == recruiter_id,
                ScoringWeights.job_id == job_id
            ).first()
        elif recruiter_id:
            # Recruiter-specific
            weights = query.filter(
                ScoringWeights.recruiter_id == recruiter_id,
                ScoringWeights.job_id.is_(None)
            ).first()
        elif job_id:
            # Job-specific
            weights = query.filter(
                ScoringWeights.recruiter_id.is_(None),
                ScoringWeights.job_id == job_id
            ).first()
        else:
            # Global weights
            weights = query.filter(
                ScoringWeights.recruiter_id.is_(None),
                ScoringWeights.job_id.is_(None)
            ).first()
        
        if weights:
            return {
                "skill_weight": float(weights.skill_weight),
                "experience_weight": float(weights.experience_weight),
                "education_weight": float(weights.education_weight),
                "semantic_similarity_weight": float(weights.semantic_similarity_weight)
            }
        
        # Return defaults if no weights found
        return DEFAULT_WEIGHTS.copy()
    
    def update_weights(
        self,
        feedback_data: List[Dict[str, Any]],
        recruiter_id: Optional[int] = None,
        job_id: Optional[int] = None,
        learning_rate: float = 0.1
    ) -> Dict[str, float]:
        """
        Update weights based on recruiter feedback
        
        Args:
            feedback_data: List of feedback entries, each with:
                - 'ai_score': Overall AI score (0-100)
                - 'hired': Boolean indicating if candidate was hired
                - 'skill_score': Optional skill score
                - 'experience_score': Optional experience score
                - 'education_score': Optional education score
            recruiter_id: Optional recruiter ID for personalized weights
            job_id: Optional job ID for job-specific weights
            learning_rate: Learning rate for weight updates (0.0 to 1.0)
            
        Returns:
            Updated weights dictionary
        """
        if not feedback_data or len(feedback_data) < 2:
            # Need at least 2 data points for learning
            return self.get_weights(recruiter_id, job_id)
        
        # Get current weights
        current_weights = self.get_weights(recruiter_id, job_id)
        
        if not SKLEARN_AVAILABLE or not NUMPY_AVAILABLE:
            # Fallback: Simple rule-based update
            return self._simple_weight_update(feedback_data, current_weights, learning_rate)
        
        # Use machine learning approach
        try:
            # Prepare data
            X = []
            y = []
            
            for entry in feedback_data:
                ai_score = entry.get('ai_score', 0)
                hired = 1 if entry.get('hired', False) else 0
                
                # Use component scores if available
                skill_score = entry.get('skill_score', ai_score * 0.4)
                exp_score = entry.get('experience_score', ai_score * 0.3)
                edu_score = entry.get('education_score', ai_score * 0.1)
                semantic_score = entry.get('semantic_score', ai_score * 0.2)
                
                X.append([skill_score, exp_score, edu_score, semantic_score])
                y.append(hired)
            
            X = np.array(X)
            y = np.array(y)
            
            # Train linear regression model
            model = LinearRegression()
            model.fit(X, y)
            
            # Extract learned coefficients (normalized to sum to 1.0)
            coefficients = model.coef_
            
            # Normalize coefficients to ensure they sum to 1.0
            total = np.sum(np.abs(coefficients))
            if total > 0:
                normalized_coefs = np.abs(coefficients) / total
            else:
                normalized_coefs = np.array([0.4, 0.3, 0.1, 0.2])  # Fallback to defaults
            
            # Update weights using learning rate
            new_weights = {
                "skill_weight": float(
                    current_weights["skill_weight"] * (1 - learning_rate) +
                    normalized_coefs[0] * learning_rate
                ),
                "experience_weight": float(
                    current_weights["experience_weight"] * (1 - learning_rate) +
                    normalized_coefs[1] * learning_rate
                ),
                "education_weight": float(
                    current_weights["education_weight"] * (1 - learning_rate) +
                    normalized_coefs[2] * learning_rate
                ),
                "semantic_similarity_weight": float(
                    current_weights["semantic_similarity_weight"] * (1 - learning_rate) +
                    normalized_coefs[3] * learning_rate
                )
            }
            
            # Normalize to ensure sum is 1.0
            total = sum(new_weights.values())
            if total > 0:
                for key in new_weights:
                    new_weights[key] /= total
            
            # Save to database
            self._save_weights(new_weights, recruiter_id, job_id)
            
            return new_weights
            
        except Exception as e:
            print(f"AdaptiveWeightLearner: Error in ML update: {e}")
            # Fallback to simple update
            return self._simple_weight_update(feedback_data, current_weights, learning_rate)
    
    def _simple_weight_update(
        self,
        feedback_data: List[Dict[str, Any]],
        current_weights: Dict[str, float],
        learning_rate: float
    ) -> Dict[str, float]:
        """
        Simple rule-based weight update when ML libraries unavailable
        """
        # Calculate average scores for hired vs not hired
        hired_scores = {
            "skill": [],
            "experience": [],
            "education": [],
            "semantic": []
        }
        not_hired_scores = {
            "skill": [],
            "experience": [],
            "education": [],
            "semantic": []
        }
        
        for entry in feedback_data:
            is_hired = entry.get('hired', False)
            target = hired_scores if is_hired else not_hired_scores
            
            ai_score = entry.get('ai_score', 0)
            target["skill"].append(entry.get('skill_score', ai_score * 0.4))
            target["experience"].append(entry.get('experience_score', ai_score * 0.3))
            target["education"].append(entry.get('education_score', ai_score * 0.1))
            target["semantic"].append(entry.get('semantic_score', ai_score * 0.2))
        
        # Calculate differences
        if hired_scores["skill"] and not_hired_scores["skill"]:
            skill_diff = np.mean(hired_scores["skill"]) - np.mean(not_hired_scores["skill"]) if NUMPY_AVAILABLE else 0
            exp_diff = np.mean(hired_scores["experience"]) - np.mean(not_hired_scores["experience"]) if NUMPY_AVAILABLE else 0
            edu_diff = np.mean(hired_scores["education"]) - np.mean(not_hired_scores["education"]) if NUMPY_AVAILABLE else 0
            sem_diff = np.mean(hired_scores["semantic"]) - np.mean(not_hired_scores["semantic"]) if NUMPY_AVAILABLE else 0
            
            # Adjust weights based on differences
            adjustments = {
                "skill_weight": skill_diff * learning_rate / 100.0,
                "experience_weight": exp_diff * learning_rate / 100.0,
                "education_weight": edu_diff * learning_rate / 100.0,
                "semantic_similarity_weight": sem_diff * learning_rate / 100.0
            }
            
            new_weights = {
                "skill_weight": max(0.1, min(0.6, current_weights["skill_weight"] + adjustments["skill_weight"])),
                "experience_weight": max(0.1, min(0.6, current_weights["experience_weight"] + adjustments["experience_weight"])),
                "education_weight": max(0.05, min(0.3, current_weights["education_weight"] + adjustments["education_weight"])),
                "semantic_similarity_weight": max(0.1, min(0.5, current_weights["semantic_similarity_weight"] + adjustments["semantic_similarity_weight"]))
            }
            
            # Normalize
            total = sum(new_weights.values())
            if total > 0:
                for key in new_weights:
                    new_weights[key] /= total
            
            self._save_weights(new_weights, None, None)
            return new_weights
        
        return current_weights
    
    def _save_weights(
        self,
        weights: Dict[str, float],
        recruiter_id: Optional[int],
        job_id: Optional[int]
    ):
        """Save or update weights in database"""
        # Find or create weights record
        query = self.db.query(ScoringWeights)
        
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
        
        if weights_record:
            # Update existing
            weights_record.skill_weight = weights["skill_weight"]
            weights_record.experience_weight = weights["experience_weight"]
            weights_record.education_weight = weights["education_weight"]
            weights_record.semantic_similarity_weight = weights["semantic_similarity_weight"]
            weights_record.iteration_count += 1
        else:
            # Create new
            weights_record = ScoringWeights(
                recruiter_id=recruiter_id,
                job_id=job_id,
                skill_weight=weights["skill_weight"],
                experience_weight=weights["experience_weight"],
                education_weight=weights["education_weight"],
                semantic_similarity_weight=weights["semantic_similarity_weight"],
                iteration_count=1
            )
            self.db.add(weights_record)
        
        self.db.commit()
    
    def collect_feedback_data(
        self,
        recruiter_id: Optional[int] = None,
        job_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Collect feedback data from applications for learning
        
        Args:
            recruiter_id: Optional recruiter ID to filter
            job_id: Optional job ID to filter
            limit: Maximum number of records to collect
            
        Returns:
            List of feedback dictionaries
        """
        query = self.db.query(Application).join(Applicant).filter(
            Application.hire_decision.isnot(None),  # Only decisions that were made
            Application.ai_score_at_decision.isnot(None)  # Must have AI score
        )
        
        if recruiter_id:
            # Filter by recruiter's jobs
            query = query.join(Applicant.job).filter(Applicant.job.has(recruiter_id=recruiter_id))
        
        if job_id:
            query = query.filter(Application.job_id == job_id)
        
        applications = query.order_by(Application.updated_at.desc()).limit(limit).all()
        
        feedback_data = []
        for app in applications:
            applicant = app.applicant_id and self.db.query(Applicant).filter(Applicant.id == app.applicant_id).first()
            
            if applicant:
                feedback_data.append({
                    "ai_score": app.ai_score_at_decision or 0,
                    "hired": app.hire_decision or False,
                    "skill_score": applicant.skill_score or 0,
                    "experience_score": applicant.experience_score or 0,
                    "education_score": applicant.education_score or 0,
                    "semantic_score": applicant.match_score or 0,
                    "application_id": app.id
                })
        
        return feedback_data

