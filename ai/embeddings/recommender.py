"""
Recommendation System - AI-powered similarity matching
Recommends top jobs for applicants and similar candidates for recruiters
"""
from typing import List, Dict, Any, Optional
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ai.embeddings import EmbeddingVectorizer
from ai.embeddings.similarity import SimilarityCalculator
from ai import utils as ai_utils


class Recommender:
    """
    AI-powered recommendation system for jobs and candidates
    Uses semantic similarity to match candidates with jobs
    """
    
    def __init__(self):
        """Initialize the recommender with embedding vectorizer"""
        self.vectorizer = EmbeddingVectorizer()
    
    def recommend_jobs_for_candidate(
        self,
        candidate_resume_text: str,
        available_jobs: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recommend top jobs for a candidate based on resume similarity
        
        Args:
            candidate_resume_text: Candidate's resume text
            available_jobs: List of job dictionaries with:
                - id: Job ID
                - title: Job title
                - description: Job description
                - requirements: Job requirements (optional)
            top_k: Number of top recommendations to return
            
        Returns:
            List of recommended jobs with similarity scores, sorted by relevance
        """
        if not candidate_resume_text or not available_jobs:
            return []
        
        try:
            # Generate embedding for candidate resume
            candidate_embedding = self.vectorizer.generate_embedding(candidate_resume_text)
            
            # Calculate similarity with each job
            job_scores = []
            for job in available_jobs:
                job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('requirements', '')}"
                job_embedding = self.vectorizer.generate_embedding(job_text)
                
                # Calculate similarity score
                similarity = SimilarityCalculator.calculate_match_score(
                    candidate_embedding,
                    job_embedding
                )
                
                job_scores.append({
                    "job_id": job.get("id"),
                    "job_title": job.get("title"),
                    "job_description": job.get("description"),
                    "similarity_score": round(similarity, 2),
                    "match_percentage": round(similarity, 2),
                    "job": job  # Include full job data
                })
            
            # Sort by similarity score (descending)
            job_scores.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Return top K recommendations
            return job_scores[:top_k]
            
        except Exception as e:
            import traceback
            print(f"Recommender: Error recommending jobs: {e}")
            print(f"Recommender: Traceback: {traceback.format_exc()}")
            return []
    
    def recommend_candidates_for_job(
        self,
        job_description: str,
        job_requirements: str,
        available_candidates: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recommend top candidates for a job based on resume similarity
        
        Args:
            job_description: Job description text
            job_requirements: Job requirements text
            available_candidates: List of candidate dictionaries with:
                - id: Candidate ID
                - resume_text: Candidate's resume text
                - name: Candidate name (optional)
                - email: Candidate email (optional)
            top_k: Number of top recommendations to return
            
        Returns:
            List of recommended candidates with similarity scores, sorted by relevance
        """
        if not job_description or not available_candidates:
            return []
        
        try:
            # Combine job description and requirements
            job_text = f"{job_description} {job_requirements or ''}"
            job_embedding = self.vectorizer.generate_embedding(job_text)
            
            # Calculate similarity with each candidate
            candidate_scores = []
            for candidate in available_candidates:
                resume_text = candidate.get("resume_text", "")
                if not resume_text:
                    continue
                
                candidate_embedding = self.vectorizer.generate_embedding(resume_text)
                
                # Calculate similarity score
                similarity = SimilarityCalculator.calculate_match_score(
                    candidate_embedding,
                    job_embedding
                )
                
                candidate_scores.append({
                    "candidate_id": candidate.get("id"),
                    "candidate_name": candidate.get("name", "Unknown"),
                    "candidate_email": candidate.get("email"),
                    "similarity_score": round(similarity, 2),
                    "match_percentage": round(similarity, 2),
                    "candidate": candidate  # Include full candidate data
                })
            
            # Sort by similarity score (descending)
            candidate_scores.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Return top K recommendations
            return candidate_scores[:top_k]
            
        except Exception as e:
            import traceback
            print(f"Recommender: Error recommending candidates: {e}")
            print(f"Recommender: Traceback: {traceback.format_exc()}")
            return []
    
    def find_similar_candidates(
        self,
        reference_candidate_resume: str,
        other_candidates: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find candidates similar to a reference candidate
        Useful for recruiters to find candidates with similar profiles
        
        Args:
            reference_candidate_resume: Reference candidate's resume text
            other_candidates: List of other candidate dictionaries
            top_k: Number of similar candidates to return
            
        Returns:
            List of similar candidates with similarity scores
        """
        if not reference_candidate_resume or not other_candidates:
            return []
        
        try:
            # Generate embedding for reference candidate
            reference_embedding = self.vectorizer.generate_embedding(reference_candidate_resume)
            
            # Calculate similarity with each candidate
            similar_candidates = []
            for candidate in other_candidates:
                resume_text = candidate.get("resume_text", "")
                if not resume_text:
                    continue
                
                candidate_embedding = self.vectorizer.generate_embedding(resume_text)
                
                # Calculate similarity score
                similarity = SimilarityCalculator.calculate_match_score(
                    reference_embedding,
                    candidate_embedding
                )
                
                similar_candidates.append({
                    "candidate_id": candidate.get("id"),
                    "candidate_name": candidate.get("name", "Unknown"),
                    "similarity_score": round(similarity, 2),
                    "match_percentage": round(similarity, 2),
                    "candidate": candidate
                })
            
            # Sort by similarity score (descending)
            similar_candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Return top K similar candidates
            return similar_candidates[:top_k]
            
        except Exception as e:
            import traceback
            print(f"Recommender: Error finding similar candidates: {e}")
            print(f"Recommender: Traceback: {traceback.format_exc()}")
            return []

