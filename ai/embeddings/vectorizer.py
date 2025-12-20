"""
Embedding Vectorizer - Converts text into embeddings
Uses OpenAI text-embedding-3-large
"""
from typing import List
from openai import OpenAI
import sys
import os

# Add backend to path to import config
backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.config import settings
except ImportError:
    # Fallback if config not available
    class Settings:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    settings = Settings()


class EmbeddingVectorizer:
    """Service for generating semantic embeddings using OpenAI"""
    
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

