"""
AI Email Generator - Generates personalized emails for candidate communication
Uses OpenAI GPT models to create context-aware, professional emails
"""
from typing import Dict, Any, Optional, List
import json
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.config import settings
except ImportError:
    class Settings:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    settings = Settings()

from .openai_client import OpenAIClient


class EmailGenerator:
    """
    Generates personalized emails for candidate communication
    Supports multiple message types: acknowledgment, feedback, rejection, interview_invitation
    """
    
    def __init__(self):
        """Initialize the email generator with OpenAI client"""
        self.client = None
        self.use_llm = False
        self.default_tone = "professional, concise, and encouraging"
        
        api_key = settings.OPENAI_API_KEY
        if api_key and api_key.strip():
            try:
                self.client = OpenAIClient()
                self.use_llm = True
                print("EmailGenerator: Using OpenAI GPT-4o-mini")
            except Exception as e:
                print(f"EmailGenerator: Failed to initialize OpenAI client: {e}")
                self.use_llm = False
        else:
            print("EmailGenerator: OpenAI API key not configured")
    
    def generate_email(
        self,
        candidate_name: str,
        job_title: str,
        message_type: str = "feedback",
        score_data: Optional[Dict[str, Any]] = None,
        additional_context: Optional[Dict[str, Any]] = None,
        tone: Optional[str] = None
    ) -> str:
        """
        Generate a personalized email for a candidate
        
        Args:
            candidate_name: Full name of the candidate
            job_title: Title of the job position
            message_type: Type of email (acknowledgment, feedback, rejection, interview_invitation)
            score_data: Dictionary with scoring information (overall_score, skill_score, etc.)
            additional_context: Additional context (missing_skills, strengths, etc.)
            tone: Email tone override (defaults to self.default_tone)
        
        Returns:
            Generated email content as string
        """
        if not self.use_llm:
            return self._generate_fallback_email(candidate_name, job_title, message_type, score_data)
        
        tone = tone or self.default_tone
        
        # Build context string from score data
        score_context = ""
        if score_data:
            score_parts = []
            if "overall_score" in score_data:
                score_parts.append(f"Overall match score: {score_data['overall_score']:.1f}%")
            if "skill_score" in score_data:
                score_parts.append(f"Skills score: {score_data['skill_score']:.1f}%")
            if "experience_score" in score_data:
                score_parts.append(f"Experience score: {score_data['experience_score']:.1f}%")
            if "education_score" in score_data:
                score_parts.append(f"Education score: {score_data['education_score']:.1f}%")
            score_context = "\n".join(score_parts)
        
        # Build additional context string
        context_str = ""
        if additional_context:
            context_parts = []
            if "missing_skills" in additional_context and additional_context["missing_skills"]:
                skills = ", ".join(additional_context["missing_skills"][:5])  # Limit to 5
                context_parts.append(f"Missing skills: {skills}")
            if "strengths" in additional_context and additional_context["strengths"]:
                strengths = ", ".join(additional_context["strengths"][:3])  # Limit to 3
                context_parts.append(f"Key strengths: {strengths}")
            if "weaknesses" in additional_context and additional_context["weaknesses"]:
                weaknesses = ", ".join(additional_context["weaknesses"][:3])  # Limit to 3
                context_parts.append(f"Areas for improvement: {weaknesses}")
            context_str = "\n".join(context_parts)
        
        # Build prompt based on message type
        system_prompt = "You are a professional HR recruiter writing emails to candidates. Write clear, respectful, and personalized messages."
        
        user_prompt = self._build_prompt(
            candidate_name, job_title, message_type, score_context, context_str, tone
        )
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            email_content = self.client.chat_completion(
                messages=messages,
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=500
            )
            
            return email_content.strip()
        except Exception as e:
            print(f"EmailGenerator: Error generating email: {e}")
            return self._generate_fallback_email(candidate_name, job_title, message_type, score_data)
    
    def _build_prompt(
        self,
        candidate_name: str,
        job_title: str,
        message_type: str,
        score_context: str,
        context_str: str,
        tone: str
    ) -> str:
        """Build the prompt for email generation based on message type"""
        
        base_info = f"""
Candidate name: {candidate_name}
Job title: {job_title}
Tone: {tone}
"""
        
        if message_type == "acknowledgment":
            return f"""{base_info}
Write an acknowledgment email thanking the candidate for applying to the {job_title} position.
Keep it brief (80-120 words), professional, and welcoming.
Include:
- Thank you for applying
- Confirmation that their application was received
- Next steps (e.g., "We will review your application and get back to you")
- Professional closing
"""
        
        elif message_type == "feedback":
            feedback_info = f"""
{base_info}
{score_context}
{context_str}
"""
            return f"""{feedback_info}
Write a constructive feedback email to the candidate about their application for {job_title}.
Keep it encouraging and professional (100-150 words).
Include:
- Acknowledgment of their application
- Positive feedback on their strengths
- Constructive suggestions for areas of improvement (if applicable)
- Encouragement for future opportunities
- Professional closing
"""
        
        elif message_type == "rejection":
            rejection_info = f"""
{base_info}
{score_context}
{context_str}
"""
            return f"""{rejection_info}
Write a respectful rejection email to the candidate for the {job_title} position.
Be empathetic and professional (80-120 words).
Include:
- Thank you for their interest and time
- Acknowledge that this was a difficult decision
- Keep it brief and avoid overly detailed explanations
- Encourage them for future opportunities
- Professional closing
"""
        
        elif message_type == "interview_invitation":
            return f"""{base_info}
Write an interview invitation email to the candidate for the {job_title} position.
Be enthusiastic and clear (100-150 words).
Include:
- Congratulations on being shortlisted
- Excitement about their candidacy
- Request to schedule an interview
- Next steps (they can expect a follow-up to schedule)
- Professional closing
"""
        
        else:
            # Generic email
            return f"""{base_info}
{score_context}
{context_str}

Write a professional email to the candidate about the {job_title} position.
Keep it concise (100-150 words) and maintain a {tone} tone.
"""
    
    def _generate_fallback_email(
        self,
        candidate_name: str,
        job_title: str,
        message_type: str,
        score_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a simple fallback email when LLM is not available"""
        
        if message_type == "acknowledgment":
            return f"""Dear {candidate_name},

Thank you for your interest in the {job_title} position. We have received your application and will review it carefully.

We will be in touch soon regarding the next steps in our hiring process.

Best regards,
Recruitment Team"""
        
        elif message_type == "feedback":
            score_text = ""
            if score_data and "overall_score" in score_data:
                score_text = f" Your application received a match score of {score_data['overall_score']:.1f}%."
            return f"""Dear {candidate_name},

Thank you for applying to the {job_title} position.{score_text}

We appreciate your interest and will keep your application on file for future opportunities.

Best regards,
Recruitment Team"""
        
        elif message_type == "rejection":
            return f"""Dear {candidate_name},

Thank you for your interest in the {job_title} position. After careful consideration, we have decided not to move forward with your application at this time.

We appreciate the time you invested in the application process and wish you the best in your career search.

Best regards,
Recruitment Team"""
        
        elif message_type == "interview_invitation":
            return f"""Dear {candidate_name},

Congratulations! We were impressed with your application for the {job_title} position and would like to invite you for an interview.

We will contact you shortly to schedule a convenient time.

We look forward to speaking with you.

Best regards,
Recruitment Team"""
        
        else:
            return f"""Dear {candidate_name},

Thank you for your interest in the {job_title} position.

We will be in touch regarding next steps.

Best regards,
Recruitment Team"""

