"""
RAG Generator - Generate context-aware responses
"""
from typing import List, Dict, Any, Optional
import sys
import os
import re

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Make langchain optional
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatOpenAI = None
    PromptTemplate = None

from app.config import settings
from ..llm.openai_client import OpenAIClient


class RAGGenerator:
    """Generate context-aware responses using RAG"""
    
    def __init__(self):
        # Validate API key first - check for empty string too
        api_key = settings.OPENAI_API_KEY
        if not api_key or not api_key.strip():
            raise ValueError("OPENAI_API_KEY not set in environment or is empty")
        
        print(f"RAGGenerator: Initializing with API key (length: {len(api_key)})...")
        self.use_langchain = LANGCHAIN_AVAILABLE
        
        try:
            self.client = OpenAIClient()
            print("RAGGenerator: Successfully initialized OpenAIClient")
        except Exception as e:
            import traceback
            print(f"RAGGenerator: Failed to initialize OpenAIClient: {e}")
            print(f"RAGGenerator: Traceback: {traceback.format_exc()}")
            raise
        
        if self.use_langchain:
            try:
                # Try both parameter names for compatibility
                try:
                    self.llm = ChatOpenAI(
                        model="gpt-4o-mini",
                        temperature=0.7,
                        api_key=settings.OPENAI_API_KEY
                    )
                except TypeError:
                    # Fallback to older parameter name
                    self.llm = ChatOpenAI(
                        model_name="gpt-4o-mini",
                        temperature=0.7,
                        openai_api_key=settings.OPENAI_API_KEY
                    )
            except Exception as e:
                print(f"Warning: Could not initialize LangChain LLM: {e}")
                self.use_langchain = False
                self.llm = None
    
    def generate_summary(self, resume_text: str, job_description: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate AI summary for candidate with optional context
        
        Args:
            resume_text: Resume text
            job_description: Job description
            context: Optional retrieved context from RAG
        
        Returns:
            Dictionary with summary, strengths, weaknesses, recommendations
        """
        prompt = f"""Analyze the following resume and job description, then provide:
1. A concise summary of the candidate (2-3 sentences)
2. Key strengths that match the job requirements
3. Potential weaknesses or gaps
4. Recommendations for the recruiter

Resume:
{resume_text[:2000]}

Job Description:
{job_description[:1000]}
"""
        
        if context:
            prompt += f"\nAdditional Context:\n" + "\n".join(context[:3])
        
        prompt += "\n\nFormat your response as:\nSUMMARY: [summary text]\nSTRENGTHS: [comma-separated list]\nWEAKNESSES: [comma-separated list]\nRECOMMENDATIONS: [comma-separated list]"
        
        try:
            print(f"RAGGenerator: Generating summary with OpenAI. Resume length: {len(resume_text)}, Job desc length: {len(job_description)}")
            if self.use_langchain and self.llm:
                print("RAGGenerator: Using LangChain LLM")
                response = self.llm.invoke(prompt)
                content = response.content if hasattr(response, 'content') else str(response)
            else:
                print("RAGGenerator: Using OpenAIClient directly")
                if not self.client:
                    raise ValueError("OpenAIClient not initialized")
                messages = [{"role": "user", "content": prompt}]
                content = self.client.chat_completion(messages, temperature=0.7)
            
            print(f"RAGGenerator: Received response from OpenAI, length: {len(content)}")
            if not content or len(content.strip()) == 0:
                raise ValueError("Empty response from OpenAI")
            return self._parse_summary_response(content)
        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"Error generating summary: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            
            # Provide more specific error messages
            if "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower() or "429" in error_msg:
                error_detail = "OpenAI API quota exceeded. Please check your billing and add credits to your OpenAI account."
            elif "invalid" in error_msg.lower() and "api key" in error_msg.lower():
                error_detail = "Invalid OpenAI API key. Please check your API key in the .env file."
            elif "rate limit" in error_msg.lower():
                error_detail = "OpenAI API rate limit exceeded. Please wait a moment and try again."
            else:
                error_detail = f"OpenAI API error: {error_msg}"
            
            return {
                "summary": f"Unable to generate AI summary: {error_detail}",
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "error": error_detail
            }
    
    def generate_feedback(self, resume_text: str, job_description: str, scores: Dict[str, float], context: Optional[List[str]] = None) -> str:
        """
        Generate detailed feedback for candidate
        
        Args:
            resume_text: Resume text
            job_description: Job description
            scores: Scoring dictionary
            context: Optional retrieved context
        
        Returns:
            Feedback text
        """
        prompt = f"""Based on the resume, job description, and scoring results, provide constructive feedback:

Resume: {resume_text[:1500]}
Job: {job_description[:800]}
Scores: Match={scores.get('match_score', 0)}, Skills={scores.get('skill_score', 0)}, Experience={scores.get('experience_score', 0)}
"""
        
        if context:
            prompt += f"\nAdditional Context:\n" + "\n".join(context[:2])
        
        prompt += "\n\nProvide 2-3 paragraphs of feedback explaining:\n- Why the candidate scored as they did\n- What makes them a good or poor fit\n- Specific areas for improvement if applicable"
        
        try:
            if self.use_langchain and self.llm:
                response = self.llm.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
            else:
                messages = [{"role": "user", "content": prompt}]
                return self.client.chat_completion(messages, temperature=0.7)
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return "Unable to generate feedback at this time."
    
    def _parse_summary_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        summary = ""
        strengths = []
        weaknesses = []
        recommendations = []
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('SUMMARY:'):
                current_section = 'summary'
                summary = line.replace('SUMMARY:', '').strip()
            elif line.startswith('STRENGTHS:'):
                current_section = 'strengths'
                strengths_str = line.replace('STRENGTHS:', '').strip()
                strengths = [s.strip() for s in strengths_str.split(',') if s.strip()]
            elif line.startswith('WEAKNESSES:'):
                current_section = 'weaknesses'
                weaknesses_str = line.replace('WEAKNESSES:', '').strip()
                weaknesses = [w.strip() for w in weaknesses_str.split(',') if w.strip()]
            elif line.startswith('RECOMMENDATIONS:'):
                current_section = 'recommendations'
                rec_str = line.replace('RECOMMENDATIONS:', '').strip()
                recommendations = [r.strip() for r in rec_str.split(',') if r.strip()]
            elif current_section == 'summary' and line:
                summary += " " + line
            elif current_section == 'strengths' and line:
                strengths.extend([s.strip() for s in line.split(',') if s.strip()])
            elif current_section == 'weaknesses' and line:
                weaknesses.extend([w.strip() for w in line.split(',') if w.strip()])
            elif current_section == 'recommendations' and line:
                recommendations.extend([r.strip() for r in line.split(',') if r.strip()])
        
        return {
            "summary": summary or "Summary not available",
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5],
            "recommendations": recommendations[:5]
        }

