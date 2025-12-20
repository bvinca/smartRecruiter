from typing import List, Dict, Any, Optional
from app.config import settings
from openai import OpenAI
import os
import re

# Make langchain optional
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatOpenAI = None
    OpenAIEmbeddings = None
    Chroma = None
    RetrievalQA = None
    PromptTemplate = None
    Document = None


class RAGService:
    """Retrieval-Augmented Generation service for AI-powered insights"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.use_langchain = LANGCHAIN_AVAILABLE
        
        if self.use_langchain:
            self.llm = ChatOpenAI(
                model_name="gpt-4o-mini",
                temperature=0.7,
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            # Initialize ChromaDB
            persist_directory = settings.CHROMA_PERSIST_DIR
            os.makedirs(persist_directory, exist_ok=True)
        else:
            self.llm = None
            self.embeddings = None
        
        self.vectorstore = None
        self.qa_chain = None
    
    def initialize_vectorstore(self, documents: List):
        """Initialize vector store with documents"""
        if not self.use_langchain:
            # Vector store not available without langchain
            return
        
        if not documents:
            return
        
        try:
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIR
            )
            
            # Create QA chain
            prompt_template = """Use the following pieces of context to answer the question.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            
            Context: {context}
            
            Question: {question}
            
            Answer:"""
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
        except Exception as e:
            print(f"Warning: Could not initialize vector store: {e}")
    
    def generate_summary(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Generate AI summary for candidate"""
        prompt = f"""Analyze the following resume and job description, then provide:
1. A concise summary of the candidate (2-3 sentences)
2. Key strengths that match the job requirements
3. Potential weaknesses or gaps
4. Recommendations for the recruiter

Resume:
{resume_text[:2000]}

Job Description:
{job_description[:1000]}

Format your response as:
SUMMARY: [summary text]
STRENGTHS: [comma-separated list]
WEAKNESSES: [comma-separated list]
RECOMMENDATIONS: [comma-separated list]
"""
        
        try:
            if self.use_langchain and self.llm:
                response = self.llm.invoke(prompt)
                content = response.content if hasattr(response, 'content') else str(response)
            else:
                # Fallback to direct OpenAI API
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                content = response.choices[0].message.content
            
            # Parse response
            summary_data = self._parse_summary_response(content)
            return summary_data
        except Exception as e:
            return {
                "summary": "Unable to generate AI summary at this time.",
                "strengths": [],
                "weaknesses": [],
                "recommendations": []
            }
    
    def generate_feedback(self, resume_text: str, job_description: str, scores: Dict[str, float]) -> str:
        """Generate detailed feedback for candidate"""
        prompt = f"""Based on the resume, job description, and scoring results, provide constructive feedback:

Resume: {resume_text[:1500]}
Job: {job_description[:800]}
Scores: Match={scores.get('match_score', 0)}, Skills={scores.get('skill_score', 0)}, Experience={scores.get('experience_score', 0)}

Provide 2-3 paragraphs of feedback explaining:
- Why the candidate scored as they did
- What makes them a good or poor fit
- Specific areas for improvement if applicable
"""
        
        try:
            if self.use_langchain and self.llm:
                response = self.llm.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
            else:
                # Fallback to direct OpenAI API
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                return response.choices[0].message.content
        except Exception as e:
            return "Unable to generate feedback at this time."
    
    def generate_interview_questions(self, resume_text: str, job_description: str, num_questions: int = 5) -> List[str]:
        """Generate interview questions based on resume and job"""
        prompt = f"""Generate {num_questions} relevant interview questions for this candidate based on their resume and the job requirements.

Resume: {resume_text[:1500]}
Job Description: {job_description[:800]}

Generate questions that:
- Assess technical skills mentioned in the resume
- Evaluate experience relevant to the role
- Test problem-solving abilities
- Are specific and actionable

Return only the questions, one per line, numbered 1-{num_questions}.
"""
        
        try:
            if self.use_langchain and self.llm:
                response = self.llm.invoke(prompt)
                content = response.content if hasattr(response, 'content') else str(response)
            else:
                # Fallback to direct OpenAI API
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                content = response.choices[0].message.content
            
            # Parse questions
            questions = []
            for line in content.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering
                    question = re.sub(r'^\d+[\.\)]\s*|^-\s*', '', line)
                    if question:
                        questions.append(question)
            
            return questions[:num_questions]
        except Exception as e:
            return [
                "Tell me about your experience with the technologies mentioned in this role.",
                "Describe a challenging project you worked on and how you solved it.",
                "How do you stay updated with industry trends?",
                "What motivates you in your career?",
                "Why are you interested in this position?"
            ]
    
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

