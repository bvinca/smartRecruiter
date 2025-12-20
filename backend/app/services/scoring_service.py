"""
Scoring Service - Calculate candidate scores against job requirements
Uses AI modules from ai/ directory
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


class ScoringService:
    """Service for scoring candidates against job requirements"""
    
    def __init__(self):
        self.vectorizer = EmbeddingVectorizer()
        self.rag_pipeline = RAGPipeline()
    
    def calculate_scores(
        self,
        resume_text: str,
        job_description: str,
        job_requirements: str,
        applicant_skills: List[str],
        applicant_experience_years: float,
        applicant_education: List[Dict[str, Any]],
        applicant_work_experience: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive scores for candidate"""
        
        # 1. Semantic Match Score (using embeddings)
        resume_embedding = self.vectorizer.generate_embedding(resume_text)
        job_embedding = self.vectorizer.generate_embedding(job_description)
        match_score = SimilarityCalculator.calculate_match_score(resume_embedding, job_embedding)
        
        # 2. Skill Score
        skill_score = self._calculate_skill_score(applicant_skills, job_description, job_requirements)
        
        # 3. Experience Score
        experience_score = self._calculate_experience_score(
            applicant_experience_years,
            applicant_work_experience,
            job_description
        )
        
        # 4. Education Score
        education_score = self._calculate_education_score(applicant_education, job_description)
        
        # 5. Overall Score (weighted average)
        overall_score = (
            match_score * 0.35 +
            skill_score * 0.30 +
            experience_score * 0.25 +
            education_score * 0.10
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            match_score, skill_score, experience_score, education_score,
            applicant_skills, applicant_experience_years
        )
        
        return {
            "match_score": round(match_score, 2),
            "skill_score": round(skill_score, 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "overall_score": round(overall_score, 2),
            "explanation": explanation,
            "resume_embedding": resume_embedding,
            "job_embedding": job_embedding
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
    
    def _generate_explanation(
        self,
        match_score: float,
        skill_score: float,
        experience_score: float,
        education_score: float,
        skills: List[str],
        experience_years: float
    ) -> Dict[str, Any]:
        """Generate human-readable explanation of scores"""
        explanations = []
        
        # Match score explanation
        if match_score >= 80:
            explanations.append("Excellent semantic match with job requirements")
        elif match_score >= 60:
            explanations.append("Good alignment with job description")
        elif match_score >= 40:
            explanations.append("Moderate match with job requirements")
        else:
            explanations.append("Limited alignment with job description")
        
        # Skill score explanation
        if skill_score >= 80:
            explanations.append(f"Strong skill match: {len(skills)} relevant skills identified")
        elif skill_score >= 60:
            explanations.append(f"Good skill coverage: {len(skills)} skills match requirements")
        else:
            explanations.append("Limited skill overlap with job requirements")
        
        # Experience explanation
        if experience_years >= 5:
            explanations.append(f"Extensive experience: {experience_years} years")
        elif experience_years >= 3:
            explanations.append(f"Solid experience: {experience_years} years")
        else:
            explanations.append(f"Entry-level experience: {experience_years} years")
        
        return {
            "match_explanation": explanations[0] if explanations else "Score calculated",
            "skill_explanation": explanations[1] if len(explanations) > 1 else "Skills evaluated",
            "experience_explanation": explanations[2] if len(explanations) > 2 else "Experience assessed",
            "overall_assessment": self._get_overall_assessment(match_score, skill_score, experience_score)
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
