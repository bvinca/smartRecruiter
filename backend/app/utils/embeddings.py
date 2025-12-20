"""
Semantic similarity functions for job-candidate matching
Uses OpenAI text-embedding-3-large for embeddings
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.config import settings

# Make numpy optional
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


class EmbeddingService:
    """Service for generating embeddings and calculating semantic similarity"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-large"  # As specified in plan
        self.embedding_dim = 3072  # text-embedding-3-large dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            return [0.0] * self.embedding_dim
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text[:8000]  # OpenAI has token limits
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * self.embedding_dim
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t if t and t.strip() else " " for t in texts]
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=valid_texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            return [[0.0] * self.embedding_dim for _ in valid_texts]
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not NUMPY_AVAILABLE:
            # Fallback calculation without numpy
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = sum(a * a for a in embedding1) ** 0.5
            norm2 = sum(b * b for b in embedding2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def calculate_match_score(
        self,
        resume_embedding: List[float],
        job_embedding: List[float]
    ) -> float:
        """
        Calculate match score between resume and job description
        Returns score from 0-100
        """
        similarity = self.cosine_similarity(resume_embedding, job_embedding)
        # Convert similarity (-1 to 1) to score (0 to 100)
        return float((similarity + 1) * 50)
    
    def rank_candidates(
        self,
        resume_embeddings: List[List[float]],
        job_embedding: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Rank candidates by semantic similarity to job description
        Returns list of candidates with scores, sorted by score descending
        """
        candidates_with_scores = []
        
        for idx, resume_emb in enumerate(resume_embeddings):
            score = self.calculate_match_score(resume_emb, job_embedding)
            candidates_with_scores.append({
                "candidate_index": idx,
                "match_score": score,
                "similarity": self.cosine_similarity(resume_emb, job_embedding)
            })
        
        # Sort by score descending
        candidates_with_scores.sort(key=lambda x: x["match_score"], reverse=True)
        
        return candidates_with_scores

