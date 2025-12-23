"""
OpenAI Client - Handles OpenAI API connections and retries
"""
from typing import Optional, Dict, Any, List
from openai import OpenAI
import sys
import os
import time

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


class OpenAIClient:
    """Handles OpenAI API connections with retry logic"""
    
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        if not api_key or not api_key.strip():
            raise ValueError("OPENAI_API_KEY not set in environment or is empty")
        
        # Validate API key format (should start with 'sk-')
        if not api_key.startswith('sk-'):
            raise ValueError(f"Invalid OpenAI API key format. Key should start with 'sk-'. Got: {api_key[:10]}...")
        
        print(f"OpenAIClient: Initializing with API key (length: {len(api_key)}, starts with: {api_key[:7]})")
        self.client = OpenAI(api_key=api_key)
        print("OpenAIClient: Successfully initialized OpenAI client")
        self.default_model = "gpt-4o-mini"
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Make a chat completion request with retry logic
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to gpt-4o-mini)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Generated text content
        """
        model = model or self.default_model
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"OpenAI API error (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"OpenAI API error after {self.max_retries} attempts: {e}")
                    raise
        
        return ""
    
    def embedding(self, text: str, model: str = "text-embedding-3-large") -> List[float]:
        """
        Generate embedding with retry logic
        
        Args:
            text: Text to embed
            model: Embedding model name
        
        Returns:
            Embedding vector
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=model,
                    input=text[:8000]  # Token limit
                )
                return response.data[0].embedding
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"OpenAI embedding error (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying...")
                    time.sleep(wait_time)
                else:
                    print(f"OpenAI embedding error after {self.max_retries} attempts: {e}")
                    raise
        
        return []

