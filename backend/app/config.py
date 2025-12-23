from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    # Use SQLite for development (no compilation needed)
    # Or PostgreSQL for production: postgresql://user:password@localhost:5432/smartrecruiter
    DATABASE_URL: str = "sqlite:///./smartrecruiter.db"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Model Selection (use "openai" or "huggingface" or "auto")
    # "auto" will use HuggingFace if OPENAI_API_KEY is not set, otherwise OpenAI
    EMBEDDING_MODEL: str = "auto"  # "openai" | "huggingface" | "auto"
    SUMMARIZATION_MODEL: str = "auto"  # "openai" | "huggingface" | "auto"
    QUESTION_GENERATION_MODEL: str = "auto"  # "openai" | "huggingface" | "auto"
    
    # HuggingFace Model Names
    HUGGINGFACE_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    HUGGINGFACE_SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    HUGGINGFACE_QUESTION_MODEL: str = "t5-small"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Email/SMTP Configuration
    # IMPORTANT: Gmail App Passwords should NOT have spaces - they will be automatically removed
    SMTP_ENABLED: bool = True  # Set to True to enable email sending
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "smartrecruiter878@gmail.com"  # Your email address
    SMTP_PASSWORD: str = "rbab wnmi jacn twvk"  # Gmail App Password (spaces will be auto-removed)
    SMTP_FROM_EMAIL: str = "smartrecruiter878@gmail.com"  # From email address (defaults to SMTP_USER)
    SMTP_FROM_NAME: str = "SmartRecruiter"  # From name
    SMTP_USE_TLS: bool = True
    SMTP_TIMEOUT: int = 10  # Timeout in seconds for SMTP operations
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

