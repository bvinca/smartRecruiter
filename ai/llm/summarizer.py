"""
Summarizer - Generate AI summaries of candidate profiles
"""
from typing import Dict, Any, Optional
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
        SUMMARIZATION_MODEL = os.getenv("SUMMARIZATION_MODEL", "auto")
        HUGGINGFACE_SUMMARIZATION_MODEL = os.getenv("HUGGINGFACE_SUMMARIZATION_MODEL", "facebook/bart-large-cnn")
    settings = Settings()

from .openai_client import OpenAIClient


class Summarizer:
    """Generate AI summaries using OpenAI or HuggingFace BART"""
    
    def __init__(self):
        # Determine which model to use
        self.use_openai = False
        self.use_huggingface = False
        self.client = None
        self.bart_model = None
        self.bart_tokenizer = None
        
        # Check model preference
        model_choice = settings.SUMMARIZATION_MODEL.lower()
        if model_choice == "auto":
            # Use HuggingFace if OpenAI key is not set, otherwise use OpenAI
            if settings.OPENAI_API_KEY:
                model_choice = "openai"
            else:
                model_choice = "huggingface"
        
        if model_choice == "openai" and settings.OPENAI_API_KEY:
            try:
                self.client = OpenAIClient()
                self.use_openai = True
                print("Summarizer: Using OpenAI GPT-4o-mini")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}, falling back to HuggingFace")
                model_choice = "huggingface"
        
        if model_choice == "huggingface" or not self.use_openai:
            try:
                from transformers import pipeline
                model_name = settings.HUGGINGFACE_SUMMARIZATION_MODEL
                print(f"Summarizer: Loading HuggingFace model {model_name}...")
                self.summarizer_pipeline = pipeline("summarization", model=model_name, device=-1)  # device=-1 for CPU
                self.use_huggingface = True
                print(f"Summarizer: Using HuggingFace {model_name}")
            except ImportError:
                raise ValueError("transformers library not installed. Install with: pip install transformers torch")
            except Exception as e:
                print(f"Failed to load HuggingFace model: {e}")
                if not self.use_openai:
                    raise ValueError(f"Could not initialize any summarization model: {e}")
    
    def summarize_candidate(self, parsed_data: Dict[str, Any], job_description: str = None) -> str:
        """
        Generate a concise summary of the candidate's experience
        
        Args:
            parsed_data: Parsed resume data dictionary
            job_description: Optional job description for context
        
        Returns:
            Summary text (2-3 sentences)
        """
        resume_text = parsed_data.get("resume_text", "")
        skills = parsed_data.get("skills", [])
        experience_years = parsed_data.get("experience_years", 0)
        work_experience = parsed_data.get("work_experience", [])
        education = parsed_data.get("education", [])
        
        prompt = f"""Summarize this candidate's profile in one concise paragraph (2-3 sentences). Focus on:
- Years of experience
- Key technical skills
- Notable work experience
- Education background
"""
        
        if job_description:
            prompt += f"\nConsider this job description for context:\n{job_description[:500]}"
        
        prompt += f"""
Resume Text:
{resume_text[:2000]}

Skills: {', '.join(skills[:10])}
Experience: {experience_years} years
Work Experience: {len(work_experience)} positions
Education: {len(education)} degrees

Provide a professional summary:"""
        
        try:
            if self.use_openai and self.client:
                messages = [
                    {"role": "system", "content": "You are a professional recruiter assistant. Provide concise, accurate candidate summaries."},
                    {"role": "user", "content": prompt}
                ]
                return self.client.chat_completion(messages, max_tokens=200)
            elif self.use_huggingface and hasattr(self, 'summarizer_pipeline'):
                # Use BART for summarization
                # Prepare text for BART (combine resume text and context)
                text_to_summarize = f"""
                Skills: {', '.join(skills[:10])}
                Experience: {experience_years} years
                Work Experience: {len(work_experience)} positions
                Education: {len(education)} degrees
                
                {resume_text[:2000]}
                """
                if job_description:
                    text_to_summarize += f"\n\nJob Context: {job_description[:500]}"
                
                # BART has token limits, truncate if needed
                max_length = min(len(text_to_summarize.split()), 1024)
                summary = self.summarizer_pipeline(
                    text_to_summarize,
                    max_length=max_length,
                    min_length=30,
                    do_sample=False
                )
                return summary[0]['summary_text'] if isinstance(summary, list) and len(summary) > 0 else str(summary)
            else:
                # Fallback
                return f"Experienced professional with {experience_years} years of experience in {', '.join(skills[:5])}."
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Experienced professional with {experience_years} years of experience in {', '.join(skills[:5])}."

