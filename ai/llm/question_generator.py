"""
Question Generator - Generate interview questions based on candidate profile
"""
from typing import Dict, Any, List, Optional
import re
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
        QUESTION_GENERATION_MODEL = os.getenv("QUESTION_GENERATION_MODEL", "auto")
        HUGGINGFACE_QUESTION_MODEL = os.getenv("HUGGINGFACE_QUESTION_MODEL", "t5-small")
    settings = Settings()

from .openai_client import OpenAIClient


class QuestionGenerator:
    """Generate contextual interview questions using OpenAI or HuggingFace T5"""
    
    def __init__(self):
        # Determine which model to use
        self.use_openai = False
        self.use_huggingface = False
        self.client = None
        self.t5_model = None
        self.t5_tokenizer = None
        
        # Check model preference
        model_choice = settings.QUESTION_GENERATION_MODEL.lower()
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
                print("QuestionGenerator: Using OpenAI GPT-4o-mini")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}, falling back to HuggingFace")
                model_choice = "huggingface"
        
        if model_choice == "huggingface" or not self.use_openai:
            try:
                from transformers import T5ForConditionalGeneration, T5Tokenizer
                model_name = settings.HUGGINGFACE_QUESTION_MODEL
                print(f"QuestionGenerator: Loading HuggingFace model {model_name}...")
                self.t5_tokenizer = T5Tokenizer.from_pretrained(model_name)
                self.t5_model = T5ForConditionalGeneration.from_pretrained(model_name)
                self.use_huggingface = True
                print(f"QuestionGenerator: Using HuggingFace {model_name}")
            except ImportError:
                raise ValueError("transformers library not installed. Install with: pip install transformers torch")
            except Exception as e:
                print(f"Failed to load HuggingFace model: {e}")
                if not self.use_openai:
                    raise ValueError(f"Could not initialize any question generation model: {e}")
    
    def generate_interview_questions(
        self,
        parsed_data: Dict[str, Any],
        job_description: Optional[str] = None,
        num_questions: int = 5
    ) -> List[str]:
        """
        Generate contextual interview questions based on candidate profile and job description
        
        Args:
            parsed_data: Parsed resume data dictionary
            job_description: Optional job description for context
            num_questions: Number of questions to generate
        
        Returns:
            List of interview questions
        """
        resume_text = parsed_data.get("resume_text", "")
        skills = parsed_data.get("skills", [])
        work_experience = parsed_data.get("work_experience", [])
        
        prompt = f"""Generate {num_questions} relevant interview questions for this candidate based on their resume.
        
Resume Text:
{resume_text[:1500]}

Key Skills: {', '.join(skills[:10])}
Work Experience: {len(work_experience)} positions

{f'Job Description: {job_description[:500]}' if job_description else ''}

Generate {num_questions} specific, actionable interview questions that:
1. Assess technical skills mentioned in the resume
2. Evaluate experience relevant to the role
3. Test problem-solving abilities
4. Are specific and actionable

Return only the questions, one per line, numbered 1-{num_questions}."""
        
        try:
            if self.use_openai and self.client:
                messages = [
                    {"role": "system", "content": "You are a professional recruiter. Generate relevant, specific interview questions."},
                    {"role": "user", "content": prompt}
                ]
                content = self.client.chat_completion(messages, max_tokens=500)
                
                # Parse questions from response
                questions = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        # Remove numbering
                        question = re.sub(r'^\d+[\.\)]\s*|^-\s*', '', line)
                        if question:
                            questions.append(question)
                
                return questions[:num_questions] if questions else self._default_questions()
            elif self.use_huggingface and self.t5_model and self.t5_tokenizer:
                # Use T5 for question generation
                # T5 works best with prefix-style prompts
                # Generate questions one at a time for better quality
                questions = []
                
                # Create context for question generation
                context = f"Resume: {resume_text[:800]} Skills: {', '.join(skills[:10])}"
                if job_description:
                    context += f" Job: {job_description[:400]}"
                
                # Generate questions using T5 with different prefixes
                question_prefixes = [
                    "generate interview question about experience:",
                    "generate interview question about skills:",
                    "generate interview question about problem solving:",
                    "generate interview question about motivation:",
                    "generate interview question about fit:"
                ]
                
                for i, prefix in enumerate(question_prefixes[:num_questions]):
                    try:
                        # T5 format: prefix + input
                        input_text = f"{prefix} {context}"
                        
                        # Tokenize
                        input_ids = self.t5_tokenizer.encode(
                            input_text,
                            max_length=512,
                            truncation=True,
                            return_tensors="pt"
                        )
                        
                        # Generate
                        output_ids = self.t5_model.generate(
                            input_ids,
                            max_length=100,
                            num_beams=3,
                            early_stopping=True,
                            do_sample=True,
                            temperature=0.7,
                            num_return_sequences=1
                        )
                        
                        # Decode
                        question = self.t5_tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
                        
                        # Clean up the question
                        question = re.sub(r'^(question|q):\s*', '', question, flags=re.IGNORECASE)
                        if question and len(question) > 15 and question.endswith('?'):
                            questions.append(question)
                        elif question and len(question) > 15:
                            # Add question mark if missing
                            questions.append(question + "?")
                    except Exception as e:
                        print(f"Error generating question {i+1} with T5: {e}")
                        continue
                
                # If we didn't get enough questions, use template-based approach
                if len(questions) < num_questions:
                    remaining = num_questions - len(questions)
                    for skill in skills[:remaining]:
                        if len(questions) >= num_questions:
                            break
                        # Use a simple template that T5 can complete
                        template = f"generate interview question: What is your experience with {skill}?"
                        try:
                            template_ids = self.t5_tokenizer.encode(template, return_tensors="pt", max_length=100, truncation=True)
                            template_output = self.t5_model.generate(template_ids, max_length=60, num_beams=2, do_sample=True)
                            question = self.t5_tokenizer.decode(template_output[0], skip_special_tokens=True).strip()
                            if question and len(question) > 10:
                                if not question.endswith('?'):
                                    question += "?"
                                questions.append(question)
                        except:
                            pass
                
                return questions[:num_questions] if questions else self._default_questions()
            else:
                # Fallback to default questions
                return self._default_questions()
        except Exception as e:
            print(f"Error generating interview questions: {e}")
            return self._default_questions()
    
    def _default_questions(self) -> List[str]:
        """Default interview questions if AI generation fails"""
        return [
            "Tell me about your experience with the technologies mentioned in this role.",
            "Describe a challenging project you worked on and how you solved it.",
            "How do you stay updated with industry trends?",
            "What motivates you in your career?",
            "Why are you interested in this position?"
        ]

