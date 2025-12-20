"""
AI Summarizer - Semantic enhancement using OpenAI GPT-4-turbo
"""
from typing import Dict, List, Any, Optional
from openai import OpenAI
from app.config import settings


class Summarizer:
    """Generate AI summaries and interview questions using OpenAI"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Using gpt-4o-mini for cost efficiency, can upgrade to gpt-4-turbo
    
    def summarize_candidate(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate a concise summary of the candidate's experience
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

Resume Text:
{resume_text[:2000]}

Skills: {', '.join(skills[:10])}
Experience: {experience_years} years
Work Experience: {len(work_experience)} positions
Education: {len(education)} degrees

Provide a professional summary:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional recruiter assistant. Provide concise, accurate candidate summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Experienced professional with {experience_years} years of experience in {', '.join(skills[:5])}."
    
    def generate_interview_questions(
        self,
        parsed_data: Dict[str, Any],
        job_description: Optional[str] = None,
        num_questions: int = 5
    ) -> List[str]:
        """
        Generate contextual interview questions based on candidate profile and job description
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional recruiter. Generate relevant, specific interview questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
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
    
    def analyze_candidate_fit(
        self,
        parsed_data: Dict[str, Any],
        job_description: str,
        job_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze how well the candidate fits the job requirements
        """
        resume_text = parsed_data.get("resume_text", "")
        skills = parsed_data.get("skills", [])
        
        prompt = f"""Analyze how well this candidate matches the job requirements. Provide:
1. Match percentage (0-100)
2. Key strengths that align with the role
3. Potential gaps or weaknesses
4. Overall recommendation (Strong Match / Good Match / Moderate Match / Weak Match)

Candidate Resume:
{resume_text[:2000]}

Candidate Skills: {', '.join(skills[:15])}

Job Description:
{job_description[:1000]}

{f'Job Requirements: {job_requirements[:500]}' if job_requirements else ''}

Provide your analysis in this format:
MATCH_SCORE: [0-100]
STRENGTHS: [comma-separated list]
WEAKNESSES: [comma-separated list]
RECOMMENDATION: [Strong Match / Good Match / Moderate Match / Weak Match]"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional recruiter. Analyze candidate-job fit objectively."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_fit_analysis(content)
        except Exception as e:
            print(f"Error analyzing candidate fit: {e}")
            return {
                "match_score": 50,
                "strengths": [],
                "weaknesses": [],
                "recommendation": "Moderate Match"
            }
    
    def _parse_fit_analysis(self, content: str) -> Dict[str, Any]:
        """Parse the fit analysis response"""
        result = {
            "match_score": 50,
            "strengths": [],
            "weaknesses": [],
            "recommendation": "Moderate Match"
        }
        
        lines = content.split('\n')
        for line in lines:
            if 'MATCH_SCORE:' in line:
                try:
                    score = int(re.search(r'\d+', line).group())
                    result["match_score"] = min(100, max(0, score))
                except:
                    pass
            elif 'STRENGTHS:' in line:
                strengths = line.split('STRENGTHS:')[1].strip()
                result["strengths"] = [s.strip() for s in strengths.split(',') if s.strip()]
            elif 'WEAKNESSES:' in line:
                weaknesses = line.split('WEAKNESSES:')[1].strip()
                result["weaknesses"] = [w.strip() for w in weaknesses.split(',') if w.strip()]
            elif 'RECOMMENDATION:' in line:
                recommendation = line.split('RECOMMENDATION:')[1].strip()
                result["recommendation"] = recommendation
        
        return result

