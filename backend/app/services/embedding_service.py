from openai import OpenAI
from typing import List, Optional
from app.config import settings

# Make numpy optional
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


class EmbeddingService:
    """Service for generating semantic embeddings using OpenAI or HuggingFace"""
    
    def __init__(self):
        # Determine which model to use
        model_choice = getattr(settings, 'EMBEDDING_MODEL', 'auto').lower()
        if model_choice == "auto":
            # Use HuggingFace if OpenAI key is not set, otherwise use OpenAI
            if settings.OPENAI_API_KEY:
                model_choice = "openai"
            else:
                model_choice = "huggingface"
        
        self.use_openai = False
        self.client = None
        self.model = None
        self.embedding_dim = None
        
        if model_choice == "openai" and settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.model = "text-embedding-3-small"
                self.embedding_dim = 1536
                self.use_openai = True
                print("EmbeddingService: Using OpenAI text-embedding-3-small")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}, falling back to HuggingFace")
                model_choice = "huggingface"
        
        if model_choice == "huggingface" or not self.use_openai:
            try:
                from sentence_transformers import SentenceTransformer
                model_name = getattr(settings, 'HUGGINGFACE_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
                print(f"EmbeddingService: Loading HuggingFace model {model_name}...")
                self.model = SentenceTransformer(model_name)
                self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
                self.use_openai = False
                print(f"EmbeddingService: Using HuggingFace {model_name}")
            except ImportError:
                raise ValueError("sentence-transformers not available. Install with: pip install sentence-transformers")
            except Exception as e:
                print(f"Failed to load HuggingFace model: {e}")
                if not self.use_openai:
                    raise ValueError(f"Could not initialize any embedding model: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            return [0.0] * self.embedding_dim
        
        if self.use_openai:
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text[:8000]  # OpenAI has token limits
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"Error generating embedding: {e}")
                return [0.0] * self.embedding_dim
        else:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t if t and t.strip() else " " for t in texts]
        
        if self.use_openai:
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=valid_texts
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                print(f"Error generating batch embeddings: {e}")
                return [[0.0] * self.embedding_dim for _ in valid_texts]
        else:
            embeddings = self.model.encode(valid_texts, normalize_embeddings=True)
            return embeddings.tolist()
    
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
    
    def calculate_match_score(self, resume_embedding: List[float], job_embedding: List[float]) -> float:
        """Calculate match score between resume and job description"""
        similarity = self.cosine_similarity(resume_embedding, job_embedding)
        # Convert similarity (-1 to 1) to score (0 to 100)
        return float((similarity + 1) * 50)

