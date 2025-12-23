"""
XAI Explainer - Explainable AI for Candidate Scoring
Provides detailed explanations of why candidates scored as they did
"""
from typing import Dict, Any, Optional, List
import json
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '../../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.config import settings
except ImportError:
    class Settings:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    settings = Settings()

from ..llm.openai_client import OpenAIClient


class XAIExplainer:
    """
    Explainable AI component that breaks down scoring decisions
    Provides natural language explanations for each score component
    """
    
    def __init__(self):
        """Initialize the explainer with OpenAI client"""
        self.client = None
        self.use_llm = False
        
        api_key = settings.OPENAI_API_KEY
        if api_key and api_key.strip():
            try:
                self.client = OpenAIClient()
                self.use_llm = True
                print("XAIExplainer: Using OpenAI GPT-4o-mini")
            except Exception as e:
                print(f"XAIExplainer: Failed to initialize OpenAI client: {e}")
                self.use_llm = False
        else:
            print("XAIExplainer: OpenAI API key not configured")
    
    def explain_scoring(
        self,
        resume_text: str,
        job_description: str,
        scores: Dict[str, float],
        candidate_skills: Optional[List[str]] = None,
        candidate_experience_years: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Explain the scoring breakdown for a candidate
        
        Args:
            resume_text: Candidate's resume text
            job_description: Job description
            scores: Dictionary with score breakdown (e.g., {"skill_score": 85, "experience_score": 70})
            candidate_skills: Optional list of candidate skills
            candidate_experience_years: Optional years of experience
            
        Returns:
            Dictionary with detailed explanation:
            {
                "skills_explanation": str,
                "experience_explanation": str,
                "education_explanation": str,
                "soft_skills_explanation": str,
                "strengths": List[str],
                "weaknesses": List[str],
                "overall_summary": str,
                "score_breakdown": Dict[str, Dict]
            }
        """
        if not self.use_llm or not self.client:
            return self._generate_fallback_explanation(scores)
        
        prompt = self._build_explanation_prompt(
            resume_text, job_description, scores, candidate_skills, candidate_experience_years
        )
        
        try:
            print("XAIExplainer: Generating scoring explanation...")
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert recruiter. Explain candidate scoring decisions clearly and transparently, highlighting both strengths and areas for improvement."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=800
            )
            
            print(f"XAIExplainer: Received response (length: {len(response)})")
            
            # Parse JSON response
            result = self._parse_response(response, scores)
            result["llm_available"] = True
            return result
            
        except Exception as e:
            import traceback
            print(f"XAIExplainer: Error during explanation: {e}")
            print(f"XAIExplainer: Traceback: {traceback.format_exc()}")
            
            return self._generate_fallback_explanation(scores, error=str(e))
    
    def _build_explanation_prompt(
        self,
        resume_text: str,
        job_description: str,
        scores: Dict[str, float],
        candidate_skills: Optional[List[str]],
        candidate_experience_years: Optional[float]
    ) -> str:
        """Build the explanation prompt"""
        
        resume_truncated = resume_text[:2000] if len(resume_text) > 2000 else resume_text
        job_desc_truncated = job_description[:1500] if len(job_description) > 1500 else job_description
        
        prompt = f"""Explain the scoring breakdown for this candidate compared to the job requirements.

Job Description:
{job_desc_truncated}

Candidate Resume:
{resume_truncated}
"""
        
        if candidate_skills:
            prompt += f"\nCandidate Skills: {', '.join(candidate_skills[:20])}\n"
        
        if candidate_experience_years is not None:
            prompt += f"\nCandidate Experience: {candidate_experience_years} years\n"
        
        prompt += f"""
Current Scores:
- Skills Score: {scores.get('skill_score', 0):.1f}%
- Experience Score: {scores.get('experience_score', 0):.1f}%
- Education Score: {scores.get('education_score', 0):.1f}%
- Overall Score: {scores.get('overall_score', 0):.1f}%

Provide a detailed explanation of:
1. Why the candidate scored as they did in each category
2. What specific strengths contributed to their scores
3. What weaknesses or gaps affected their scores
4. How well they align with the job requirements

Return your explanation as JSON with this exact structure:
{{
  "skills_explanation": "<detailed explanation of skills score>",
  "experience_explanation": "<detailed explanation of experience score>",
  "education_explanation": "<detailed explanation of education score>",
  "soft_skills_explanation": "<explanation of soft skills alignment>",
  "strengths": ["<list of candidate strengths>"],
  "weaknesses": ["<list of areas for improvement>"],
  "overall_summary": "<2-3 paragraph overall assessment>"
}}

Important:
- Be specific and reference actual skills/experience from the resume
- Explain both positive and negative aspects
- Provide actionable insights
- Return ONLY valid JSON, no additional text"""
        
        return prompt
    
    def _parse_response(self, response: str, scores: Dict[str, float]) -> Dict[str, Any]:
        """Parse LLM response and extract JSON"""
        try:
            # Clean response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()
            
            # Parse JSON
            result = json.loads(response_clean)
            
            # Build score breakdown with explanations
            score_breakdown = {
                "skills": {
                    "score": scores.get("skill_score", 0),
                    "explanation": result.get("skills_explanation", ""),
                    "contribution": "30%"
                },
                "experience": {
                    "score": scores.get("experience_score", 0),
                    "explanation": result.get("experience_explanation", ""),
                    "contribution": "25%"
                },
                "education": {
                    "score": scores.get("education_score", 0),
                    "explanation": result.get("education_explanation", ""),
                    "contribution": "10%"
                },
                "match": {
                    "score": scores.get("match_score", 0),
                    "explanation": "Semantic similarity between resume and job description",
                    "contribution": "35%"
                }
            }
            
            return {
                "skills_explanation": result.get("skills_explanation", ""),
                "experience_explanation": result.get("experience_explanation", ""),
                "education_explanation": result.get("education_explanation", ""),
                "soft_skills_explanation": result.get("soft_skills_explanation", ""),
                "strengths": result.get("strengths", []),
                "weaknesses": result.get("weaknesses", []),
                "overall_summary": result.get("overall_summary", ""),
                "score_breakdown": score_breakdown
            }
            
        except json.JSONDecodeError as e:
            print(f"XAIExplainer: Failed to parse JSON: {e}")
            return self._generate_fallback_explanation(scores)
    
    def _generate_fallback_explanation(self, scores: Dict[str, float], error: Optional[str] = None) -> Dict[str, Any]:
        """Generate fallback explanation when LLM is unavailable"""
        return {
            "skills_explanation": f"Skills score: {scores.get('skill_score', 0):.1f}% - Based on keyword matching and skill overlap",
            "experience_explanation": f"Experience score: {scores.get('experience_score', 0):.1f}% - Based on years of experience and relevance",
            "education_explanation": f"Education score: {scores.get('education_score', 0):.1f}% - Based on degree relevance",
            "soft_skills_explanation": "Soft skills evaluated based on resume content",
            "strengths": ["Detailed explanation not available"],
            "weaknesses": ["Detailed explanation not available"],
            "overall_summary": f"Overall score: {scores.get('overall_score', 0):.1f}% - {'LLM explanation not available' if not error else error}",
            "score_breakdown": {
                "skills": {"score": scores.get("skill_score", 0), "contribution": "30%"},
                "experience": {"score": scores.get("experience_score", 0), "contribution": "25%"},
                "education": {"score": scores.get("education_score", 0), "contribution": "10%"},
                "match": {"score": scores.get("match_score", 0), "contribution": "35%"}
            },
            "llm_available": False
        }

