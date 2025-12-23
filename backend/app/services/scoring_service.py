"""
Scoring Service - Calculate candidate scores against job requirements
Uses AI modules from ai/ directory
Implements hybrid RAG + LLM approach as per AI_LAYER_DESIGN.md
"""
from typing import Dict, List, Any
import sys
import os

# Add ai directory to path (go up 3 levels from backend/app/services/ to root)
ai_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if ai_path not in sys.path:
    sys.path.insert(0, ai_path)

from ai.embeddings import EmbeddingVectorizer, SimilarityCalculator
from ai.rag import RAGPipeline
from ai.evaluation import CandidateEvaluator
from ai import utils as ai_utils
from typing import Optional
from sqlalchemy.orm import Session


class ScoringService:
    """
    Service for scoring candidates against job requirements
    Implements hybrid approach: 50% semantic similarity + 50% LLM reasoning
    Supports adaptive weights that learn from recruiter feedback
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.vectorizer = EmbeddingVectorizer()
        self.rag_pipeline = RAGPipeline()
        self.evaluator = CandidateEvaluator()
        # Weight for hybrid scoring (0.5 = 50% semantic, 50% LLM)
        self.semantic_weight = 0.5
        self.db = db
    
    def calculate_scores(
        self,
        resume_text: str,
        job_description: str,
        job_requirements: str,
        applicant_skills: List[str],
        applicant_experience_years: float,
        applicant_education: List[Dict[str, Any]],
        applicant_work_experience: List[Dict[str, Any]],
        recruiter_id: Optional[int] = None,
        job_id: Optional[int] = None,
        use_adaptive_weights: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive scores for candidate using hybrid approach
        Combines semantic similarity (embeddings) with LLM reasoning
        """
        
        # ===== STAGE 1: Semantic Similarity (Embeddings) =====
        resume_embedding = self.vectorizer.generate_embedding(resume_text)
        job_embedding = self.vectorizer.generate_embedding(job_description)
        semantic_match_score = SimilarityCalculator.calculate_match_score(resume_embedding, job_embedding)
        
        # Traditional scoring components (for skill/experience/education breakdown)
        semantic_skill_score = self._calculate_skill_score(applicant_skills, job_description, job_requirements)
        semantic_experience_score = self._calculate_experience_score(
            applicant_experience_years,
            applicant_work_experience,
            job_description
        )
        semantic_education_score = self._calculate_education_score(applicant_education, job_description)
        
        # ===== STAGE 2: LLM Evaluation =====
        llm_evaluation = self.evaluator.evaluate_candidate(
            cv_text=resume_text,
            job_text=job_description,
            job_requirements=job_requirements,
            candidate_skills=applicant_skills,
            candidate_experience_years=applicant_experience_years
        )
        
        llm_overall = llm_evaluation.get("overall_score", 50.0)
        llm_experience = llm_evaluation.get("experience_score", 50.0)
        llm_skill = llm_evaluation.get("skill_score", 50.0)
        llm_explanation = llm_evaluation.get("explanation", "")
        llm_available = llm_evaluation.get("llm_available", False)
        
        # ===== STAGE 3: Hybrid Scoring (50% semantic + 50% LLM) =====
        # Combine semantic and LLM scores using weighted average
        hybrid_overall = ai_utils.combine_scores(
            semantic_match_score,
            llm_overall,
            self.semantic_weight
        )
        
        hybrid_skill = ai_utils.combine_scores(
            semantic_skill_score,
            llm_skill,
            self.semantic_weight
        )
        
        hybrid_experience = ai_utils.combine_scores(
            semantic_experience_score,
            llm_experience,
            self.semantic_weight
        )
        
        # Education score remains semantic-only (LLM doesn't provide this)
        education_score = semantic_education_score
        
        # ===== STAGE 4: Final Weighted Overall Score =====
        # Use adaptive weights if available, otherwise use defaults
        if use_adaptive_weights and self.db:
            try:
                from app.services.learning_service import AdaptiveWeightLearner
                learner = AdaptiveWeightLearner(self.db)
                weights = learner.get_weights(recruiter_id, job_id)
                
                # Use adaptive weights
                overall_score = (
                    hybrid_skill * weights["skill_weight"] +
                    hybrid_experience * weights["experience_weight"] +
                    education_score * weights["education_weight"] +
                    hybrid_overall * weights["semantic_similarity_weight"]
                )
            except Exception as e:
                print(f"ScoringService: Error loading adaptive weights: {e}, using defaults")
                # Fallback to default weights
                overall_score = (
                    hybrid_overall * 0.35 +
                    hybrid_skill * 0.30 +
                    hybrid_experience * 0.25 +
                    education_score * 0.10
                )
        else:
            # Default weights
            overall_score = (
                hybrid_overall * 0.35 +
                hybrid_skill * 0.30 +
                hybrid_experience * 0.25 +
                education_score * 0.10
            )
        
        # Generate comprehensive explanation
        explanation = self._generate_hybrid_explanation(
            semantic_match_score, semantic_skill_score, semantic_experience_score,
            llm_overall, llm_skill, llm_experience, llm_explanation,
            hybrid_overall, hybrid_skill, hybrid_experience,
            applicant_skills, applicant_experience_years,
            llm_available
        )
        
        return {
            "match_score": round(hybrid_overall, 2),  # Hybrid match score
            "skill_score": round(hybrid_skill, 2),  # Hybrid skill score
            "experience_score": round(hybrid_experience, 2),  # Hybrid experience score
            "education_score": round(education_score, 2),
            "overall_score": round(overall_score, 2),
            "explanation": explanation,
            "resume_embedding": resume_embedding,
            "job_embedding": job_embedding,
            # Include breakdown for transparency
            "score_breakdown": {
                "semantic": {
                    "match": round(semantic_match_score, 2),
                    "skill": round(semantic_skill_score, 2),
                    "experience": round(semantic_experience_score, 2)
                },
                "llm": {
                    "overall": round(llm_overall, 2),
                    "skill": round(llm_skill, 2),
                    "experience": round(llm_experience, 2),
                    "available": llm_available
                },
                "hybrid": {
                    "match": round(hybrid_overall, 2),
                    "skill": round(hybrid_skill, 2),
                    "experience": round(hybrid_experience, 2)
                }
            }
        }
    
    def _calculate_skill_score(
        self,
        applicant_skills: List[str],
        job_description: str,
        job_requirements: str
    ) -> float:
        """Calculate skill match score"""
        if not applicant_skills:
            return 0.0
        
        # Extract skills from job description
        job_text = (job_description + " " + (job_requirements or "")).lower()
        
        # Common technical skills to look for
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'sql', 'postgresql',
            'mongodb', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git',
            'machine learning', 'deep learning', 'nlp', 'tensorflow', 'pytorch',
            'fastapi', 'django', 'flask', 'express', 'vue', 'angular', 'typescript',
            'html', 'css', 'sass', 'less', 'redux', 'graphql', 'rest api',
            'microservices', 'ci/cd', 'jenkins', 'github actions', 'terraform',
            'linux', 'bash', 'shell scripting', 'agile', 'scrum', 'devops'
        ]
        
        required_skills = []
        for skill in skill_keywords:
            if skill in job_text:
                required_skills.append(skill)
        
        if not required_skills:
            # If no specific skills found, give base score
            return 50.0
        
        # Match applicant skills with required skills
        applicant_skills_lower = [s.lower() for s in applicant_skills]
        matched_skills = sum(1 for req_skill in required_skills if any(
            req_skill in app_skill or app_skill in req_skill
            for app_skill in applicant_skills_lower
        ))
        
        # Calculate percentage
        score = (matched_skills / len(required_skills)) * 100
        return min(score, 100.0)
    
    def _calculate_experience_score(
        self,
        experience_years: float,
        work_experience: List[Dict[str, Any]],
        job_description: str
    ) -> float:
        """Calculate experience relevance score"""
        score = 0.0
        
        # Years of experience component (max 40 points)
        if experience_years >= 5:
            score += 40
        elif experience_years >= 3:
            score += 30
        elif experience_years >= 1:
            score += 20
        else:
            score += 10
        
        # Relevance of work experience (max 60 points)
        if work_experience:
            job_text_lower = job_description.lower()
            relevant_experiences = 0
            
            for exp in work_experience:
                title = exp.get('title', '').lower()
                description = exp.get('description', '').lower()
                combined = title + " " + description
                
                # Check if experience mentions relevant keywords
                if any(keyword in combined for keyword in ['developer', 'engineer', 'software', 'programming', 'coding']):
                    relevant_experiences += 1
            
            if work_experience:
                relevance_ratio = relevant_experiences / len(work_experience)
                score += relevance_ratio * 60
        
        return min(score, 100.0)
    
    def _calculate_education_score(
        self,
        education: List[Dict[str, Any]],
        job_description: str
    ) -> float:
        """Calculate education relevance score"""
        if not education:
            return 0.0
        
        job_text_lower = job_description.lower()
        
        # Check for degree requirements
        requires_degree = any(keyword in job_text_lower for keyword in [
            'bachelor', 'master', 'phd', 'degree', 'university', 'college'
        ])
        
        if not requires_degree:
            return 50.0  # Neutral score if no degree requirement
        
        # Check if candidate has relevant degree
        for edu in education:
            degree = edu.get('degree', '').lower()
            if any(keyword in degree for keyword in [
                'computer', 'software', 'engineering', 'science', 'technology',
                'information', 'data', 'math', 'statistics'
            ]):
                return 100.0
        
        # Has degree but not directly relevant
        return 60.0
    
    def _generate_hybrid_explanation(
        self,
        semantic_match: float,
        semantic_skill: float,
        semantic_experience: float,
        llm_overall: float,
        llm_skill: float,
        llm_experience: float,
        llm_explanation: str,
        hybrid_match: float,
        hybrid_skill: float,
        hybrid_experience: float,
        skills: List[str],
        experience_years: float,
        llm_available: bool
    ) -> Dict[str, Any]:
        """Generate comprehensive explanation combining semantic and LLM insights"""
        
        explanations = []
        
        # Hybrid match score explanation
        if hybrid_match >= 80:
            explanations.append("Excellent match with job requirements (semantic + AI analysis)")
        elif hybrid_match >= 60:
            explanations.append("Good alignment with job description")
        elif hybrid_match >= 40:
            explanations.append("Moderate match with job requirements")
        else:
            explanations.append("Limited alignment with job description")
        
        # Hybrid skill score explanation
        if hybrid_skill >= 80:
            explanations.append(f"Strong skill match: {len(skills)} relevant skills identified")
        elif hybrid_skill >= 60:
            explanations.append(f"Good skill coverage: {len(skills)} skills match requirements")
        else:
            explanations.append("Limited skill overlap with job requirements")
        
        # Hybrid experience explanation
        if hybrid_experience >= 80:
            explanations.append(f"Extensive relevant experience: {experience_years} years")
        elif hybrid_experience >= 60:
            explanations.append(f"Solid experience: {experience_years} years")
        else:
            explanations.append(f"Entry-level experience: {experience_years} years")
        
        # Include LLM reasoning if available
        llm_insight = ""
        if llm_available and llm_explanation:
            llm_insight = llm_explanation
        elif not llm_available:
            llm_insight = "LLM evaluation not available. Using semantic similarity only."
        
        return {
            "match_explanation": explanations[0] if explanations else "Score calculated",
            "skill_explanation": explanations[1] if len(explanations) > 1 else "Skills evaluated",
            "experience_explanation": explanations[2] if len(explanations) > 2 else "Experience assessed",
            "llm_insight": llm_insight,
            "overall_assessment": self._get_overall_assessment(hybrid_match, hybrid_skill, hybrid_experience),
            "scoring_method": "Hybrid (50% semantic similarity + 50% LLM reasoning)" if llm_available else "Semantic similarity only (LLM unavailable)"
        }
    
    def _get_overall_assessment(self, match: float, skill: float, exp: float) -> str:
        """Get overall assessment text"""
        avg_score = (match + skill + exp) / 3
        
        if avg_score >= 80:
            return "Highly qualified candidate with strong alignment to role"
        elif avg_score >= 60:
            return "Qualified candidate with good potential fit"
        elif avg_score >= 40:
            return "Moderate candidate, may require additional training"
        else:
            return "Limited qualifications for this role"
