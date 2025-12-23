"""
RAG Pipeline - Combines retrieval + generation
"""
from typing import List, Dict, Any, Optional
from .retriever import RAGRetriever
from .generator import RAGGenerator
from ..llm.question_generator import QuestionGenerator


class RAGPipeline:
    """Complete RAG pipeline combining retrieval and generation"""
    
    def __init__(self):
        self.retriever = RAGRetriever()
        self.generator = RAGGenerator()
        # Lazy-load question generator only when needed
        self._question_generator = None
    
    def generate_summary(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Generate summary with RAG context
        
        Args:
            resume_text: Resume text
            job_description: Job description
        
        Returns:
            Dictionary with summary, strengths, weaknesses, recommendations
        """
        # Retrieve relevant context (if vectorstore is initialized)
        context = self.retriever.retrieve(job_description, k=3)
        
        # Generate summary with context
        return self.generator.generate_summary(resume_text, job_description, context)
    
    def generate_feedback(self, resume_text: str, job_description: str, scores: Dict[str, float]) -> str:
        """
        Generate feedback with RAG context
        
        Args:
            resume_text: Resume text
            job_description: Job description
            scores: Scoring dictionary
        
        Returns:
            Feedback text
        """
        # Retrieve relevant context
        context = self.retriever.retrieve(job_description, k=2)
        
        # Generate feedback with context
        return self.generator.generate_feedback(resume_text, job_description, scores, context)
    
    def generate_interview_questions(self, resume_text: str, job_description: str, num_questions: int = 5) -> List[str]:
        """
        Generate interview questions
        
        Args:
            resume_text: Resume text
            job_description: Job description
            num_questions: Number of questions
            
        Returns:
            List of interview questions
        """
        # Lazy-load question generator only when needed
        if self._question_generator is None:
            self._question_generator = QuestionGenerator()
        
        # Use question generator (doesn't need RAG context)
        parsed_data = {"resume_text": resume_text, "skills": [], "work_experience": []}
        return self._question_generator.generate_interview_questions(
            parsed_data,
            job_description,
            num_questions
        )
    
    def regenerate_questions_with_feedback(
        self,
        resume_text: str,
        current_questions: List[str],
        feedback: str,
        job_description: str,
        num_questions: int = 5
    ) -> List[str]:
        """
        Regenerate interview questions based on recruiter feedback
        
        Args:
            resume_text: Resume text
            current_questions: Current list of questions
            feedback: Recruiter's feedback
            job_description: Job description
            num_questions: Number of questions to generate
            
        Returns:
            List of improved interview questions
        """
        # Lazy-load question generator only when needed
        if self._question_generator is None:
            self._question_generator = QuestionGenerator()
        
        parsed_data = {"resume_text": resume_text, "skills": [], "work_experience": []}
        return self._question_generator.regenerate_questions_with_feedback(
            parsed_data,
            current_questions,
            feedback,
            job_description,
            num_questions
        )

