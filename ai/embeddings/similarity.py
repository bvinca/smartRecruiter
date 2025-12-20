"""
Similarity Calculator - Candidate-job matching logic using embeddings
"""
from typing import List, Dict, Any
import math

# Make numpy optional
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


class SimilarityCalculator:
    """Calculate semantic similarity between embeddings"""
    
    @staticmethod
    def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have the same dimension for cosine similarity.")
        
        if NUMPY_AVAILABLE:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
        else:
            # Pure Python fallback
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = math.sqrt(sum(a * a for a in embedding1))
            norm2 = math.sqrt(sum(b * b for b in embedding2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    @staticmethod
    def calculate_match_score(
        resume_embedding: List[float],
        job_embedding: List[float]
    ) -> float:
        """
        Calculate match score between resume and job description
        Returns score from 0-100
        """
        similarity = SimilarityCalculator.cosine_similarity(resume_embedding, job_embedding)
        # Convert similarity (-1 to 1) to score (0 to 100)
        return float((similarity + 1) * 50)
    
    @staticmethod
    def rank_candidates(
        resume_embeddings: List[List[float]],
        job_embedding: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Rank candidates by semantic similarity to job description
        Returns list of candidates with scores, sorted by score descending
        """
        candidates_with_scores = []
        
        for idx, resume_emb in enumerate(resume_embeddings):
            score = SimilarityCalculator.calculate_match_score(resume_emb, job_embedding)
            candidates_with_scores.append({
                "candidate_index": idx,
                "match_score": score,
                "similarity": SimilarityCalculator.cosine_similarity(resume_emb, job_embedding)
            })
        
        # Sort by score descending
        candidates_with_scores.sort(key=lambda x: x["match_score"], reverse=True)
        
        return candidates_with_scores

