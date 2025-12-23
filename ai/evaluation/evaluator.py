"""
LLM-based Candidate Evaluator
Uses GPT-4o-mini to provide contextual reasoning and scoring
"""
from typing import Dict, Any, Optional
import json
import sys
import os

# Add backend to path to import config
backend_path = os.path.join(os.path.dirname(__file__), '../../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.config import settings
except ImportError:
    # Fallback if config not available
    class Settings:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    settings = Settings()

from ..llm.openai_client import OpenAIClient


class CandidateEvaluator:
    """
    LLM-based evaluator that provides contextual reasoning for candidate-job matching
    Uses GPT-4o-mini to evaluate candidates beyond simple keyword matching
    """
    
    def __init__(self):
        """Initialize the evaluator with OpenAI client"""
        self.client = None
        self.use_llm = False
        
        # Check if OpenAI API key is available
        api_key = settings.OPENAI_API_KEY
        if api_key and api_key.strip():
            try:
                self.client = OpenAIClient()
                self.use_llm = True
                print("CandidateEvaluator: Using OpenAI GPT-4o-mini for evaluation")
            except Exception as e:
                print(f"CandidateEvaluator: Failed to initialize OpenAI client: {e}")
                self.use_llm = False
        else:
            print("CandidateEvaluator: OpenAI API key not configured, LLM evaluation disabled")
    
    def evaluate_candidate(
        self,
        cv_text: str,
        job_text: str,
        job_requirements: Optional[str] = None,
        candidate_skills: Optional[list] = None,
        candidate_experience_years: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluate candidate using LLM reasoning
        
        Args:
            cv_text: Candidate resume/CV text
            job_text: Job description
            job_requirements: Optional job requirements
            candidate_skills: Optional list of candidate skills
            candidate_experience_years: Optional years of experience
            
        Returns:
            Dictionary with scores and explanation:
            {
                "overall_score": int (0-100),
                "experience_score": int (0-100),
                "skill_score": int (0-100),
                "explanation": str
            }
        """
        if not self.use_llm or not self.client:
            # Fallback: return neutral scores if LLM not available
            return {
                "overall_score": 50,
                "experience_score": 50,
                "skill_score": 50,
                "explanation": "LLM evaluation not available. Using fallback scores.",
                "llm_available": False
            }
        
        # Build comprehensive prompt
        prompt = self._build_evaluation_prompt(
            cv_text, job_text, job_requirements, candidate_skills, candidate_experience_years
        )
        
        try:
            print("CandidateEvaluator: Evaluating candidate with LLM...")
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert AI recruiter. Evaluate candidates objectively and provide detailed reasoning for your scores."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent scoring
                max_tokens=500
            )
            
            print(f"CandidateEvaluator: Received LLM response (length: {len(response)})")
            
            # Parse JSON response
            result = self._parse_llm_response(response)
            result["llm_available"] = True
            return result
            
        except Exception as e:
            import traceback
            print(f"CandidateEvaluator: Error during LLM evaluation: {e}")
            print(f"CandidateEvaluator: Traceback: {traceback.format_exc()}")
            
            # Return fallback scores on error
            return {
                "overall_score": 50,
                "experience_score": 50,
                "skill_score": 50,
                "explanation": f"LLM evaluation failed: {str(e)}. Using fallback scores.",
                "llm_available": False,
                "error": str(e)
            }
    
    def _build_evaluation_prompt(
        self,
        cv_text: str,
        job_text: str,
        job_requirements: Optional[str],
        candidate_skills: Optional[list],
        candidate_experience_years: Optional[float]
    ) -> str:
        """Build the evaluation prompt for the LLM"""
        
        # Truncate text to avoid token limits
        cv_text_truncated = cv_text[:2000] if len(cv_text) > 2000 else cv_text
        job_text_truncated = job_text[:1500] if len(job_text) > 1500 else job_text
        
        prompt = f"""You are an AI recruiter. Evaluate how well this candidate fits the job.

Job Description:
{job_text_truncated}
"""
        
        if job_requirements:
            requirements_truncated = job_requirements[:800] if len(job_requirements) > 800 else job_requirements
            prompt += f"""
Job Requirements:
{requirements_truncated}
"""
        
        prompt += f"""
Candidate CV:
{cv_text_truncated}
"""
        
        if candidate_skills:
            prompt += f"""
Candidate Skills: {', '.join(candidate_skills[:20])}
"""
        
        if candidate_experience_years is not None:
            prompt += f"""
Candidate Experience: {candidate_experience_years} years
"""
        
        prompt += """
Evaluate the candidate's suitability for this role. Consider:
1. Technical skills alignment
2. Relevant work experience
3. Education and qualifications
4. Overall fit for the role

Rate suitability on a scale 0-100 for each dimension.

Return your evaluation as JSON in this exact format:
{
  "overall_score": <integer 0-100>,
  "experience_score": <integer 0-100>,
  "skill_score": <integer 0-100>,
  "explanation": "<2-3 sentence explanation of your evaluation>"
}

Important:
- Be objective and fair
- Consider both strengths and weaknesses
- Provide specific reasoning in the explanation
- Return ONLY valid JSON, no additional text
"""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and extract JSON"""
        try:
            # Try to extract JSON from response
            # Remove markdown code blocks if present
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
            
            # Validate and normalize scores
            overall_score = self._normalize_score(result.get("overall_score", 50))
            experience_score = self._normalize_score(result.get("experience_score", 50))
            skill_score = self._normalize_score(result.get("skill_score", 50))
            explanation = result.get("explanation", "Evaluation completed")
            
            return {
                "overall_score": overall_score,
                "experience_score": experience_score,
                "skill_score": skill_score,
                "explanation": explanation
            }
            
        except json.JSONDecodeError as e:
            print(f"CandidateEvaluator: Failed to parse JSON response: {e}")
            print(f"CandidateEvaluator: Response was: {response[:200]}")
            
            # Try to extract scores using regex as fallback
            import re
            overall_match = re.search(r'"overall_score":\s*(\d+)', response)
            experience_match = re.search(r'"experience_score":\s*(\d+)', response)
            skill_match = re.search(r'"skill_score":\s*(\d+)', response)
            explanation_match = re.search(r'"explanation":\s*"([^"]+)"', response)
            
            return {
                "overall_score": int(overall_match.group(1)) if overall_match else 50,
                "experience_score": int(experience_match.group(1)) if experience_match else 50,
                "skill_score": int(skill_match.group(1)) if skill_match else 50,
                "explanation": explanation_match.group(1) if explanation_match else "Evaluation completed (parsed with fallback)"
            }
    
    def _normalize_score(self, score: Any) -> int:
        """Normalize score to 0-100 range"""
        try:
            score_int = int(float(score))
            return max(0, min(100, score_int))
        except (ValueError, TypeError):
            return 50  # Default to neutral score

