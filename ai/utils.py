"""
AI Utilities - Hybrid Scoring, Normalization, and Ranking
Implements the weighted hybrid scoring approach from AI_LAYER_DESIGN.md
"""
from typing import List, Dict, Any, Tuple
import numpy as np


def combine_scores(semantic_score: float, llm_score: float, semantic_weight: float = 0.5) -> float:
    """
    Combine semantic similarity score with LLM reasoning score using weighted average
    
    Formula: final_score = (semantic_weight * semantic_score) + ((1 - semantic_weight) * llm_score)
    
    Args:
        semantic_score: Semantic similarity score (0-100)
        llm_score: LLM evaluation score (0-100)
        semantic_weight: Weight for semantic score (default 0.5 for 50/50 split)
    
    Returns:
        Combined score (0-100)
    """
    llm_weight = 1.0 - semantic_weight
    combined = (semantic_weight * semantic_score) + (llm_weight * llm_score)
    return round(combined, 2)


def normalize_scores(scores: List[float], min_score: float = 0.0, max_score: float = 100.0) -> List[float]:
    """
    Normalize scores to 0-100 range relative to min/max in the dataset
    
    This ensures candidates are ranked relative to each other for a specific job posting.
    
    Args:
        scores: List of scores to normalize
        min_score: Minimum score in dataset (default 0.0)
        max_score: Maximum score in dataset (default 100.0)
    
    Returns:
        List of normalized scores (0-100)
    """
    if not scores:
        return []
    
    # If all scores are the same, return them as-is
    if len(set(scores)) == 1:
        return scores
    
    # Find actual min and max
    actual_min = min(scores)
    actual_max = max(scores)
    
    # Avoid division by zero
    if actual_max == actual_min:
        return [50.0] * len(scores)  # Return neutral scores
    
    # Normalize to 0-100 range
    normalized = []
    for score in scores:
        normalized_score = ((score - actual_min) / (actual_max - actual_min)) * 100.0
        normalized.append(round(normalized_score, 2))
    
    return normalized


def rank_candidates(
    candidates: List[Dict[str, Any]],
    score_key: str = "overall_score",
    ascending: bool = False
) -> List[Dict[str, Any]]:
    """
    Rank candidates by their scores
    
    Args:
        candidates: List of candidate dictionaries with scores
        score_key: Key in candidate dict that contains the score
        ascending: If True, rank ascending (lowest first), else descending (highest first)
    
    Returns:
        Sorted list of candidates
    """
    return sorted(candidates, key=lambda x: x.get(score_key, 0), reverse=not ascending)


def calculate_hybrid_scores(
    semantic_scores: Dict[str, float],
    llm_scores: Dict[str, float],
    semantic_weight: float = 0.5
) -> Dict[str, float]:
    """
    Calculate hybrid scores for multiple dimensions
    
    Args:
        semantic_scores: Dictionary with semantic scores (e.g., {"overall": 75, "skill": 80})
        llm_scores: Dictionary with LLM scores (e.g., {"overall": 87, "skill": 91})
        semantic_weight: Weight for semantic scores (default 0.5)
    
    Returns:
        Dictionary with combined hybrid scores
    """
    hybrid_scores = {}
    
    # Combine scores for each dimension
    for key in semantic_scores.keys():
        semantic = semantic_scores.get(key, 50.0)
        llm = llm_scores.get(key, 50.0)
        hybrid_scores[key] = combine_scores(semantic, llm, semantic_weight)
    
    return hybrid_scores


def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector
        vec2: Second vector
    
    Returns:
        Cosine similarity score (-1 to 1)
    """
    try:
        # Use numpy if available
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    except ImportError:
        # Fallback to pure Python if numpy not available
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)


def similarity_to_score(similarity: float, min_sim: float = -1.0, max_sim: float = 1.0) -> float:
    """
    Convert cosine similarity (-1 to 1) to score (0 to 100)
    
    Args:
        similarity: Cosine similarity value
        min_sim: Minimum possible similarity (default -1.0)
        max_sim: Maximum possible similarity (default 1.0)
    
    Returns:
        Score from 0 to 100
    """
    if max_sim == min_sim:
        return 50.0
    
    # Normalize to 0-100 range
    normalized = ((similarity - min_sim) / (max_sim - min_sim)) * 100.0
    return round(max(0.0, min(100.0, normalized)), 2)


def get_score_breakdown(
    semantic_score: float,
    llm_score: float,
    semantic_weight: float = 0.5
) -> Dict[str, Any]:
    """
    Get detailed breakdown of hybrid scoring
    
    Args:
        semantic_score: Semantic similarity score
        llm_score: LLM evaluation score
        semantic_weight: Weight for semantic score
    
    Returns:
        Dictionary with score breakdown
    """
    llm_weight = 1.0 - semantic_weight
    combined = combine_scores(semantic_score, llm_score, semantic_weight)
    
    return {
        "semantic_score": semantic_score,
        "llm_score": llm_score,
        "semantic_weight": semantic_weight,
        "llm_weight": llm_weight,
        "semantic_contribution": round(semantic_score * semantic_weight, 2),
        "llm_contribution": round(llm_score * llm_weight, 2),
        "combined_score": combined
    }

