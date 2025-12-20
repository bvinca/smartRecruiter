"""
AI Constants - Model names, thresholds, configuration
"""

# OpenAI Models
OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
OPENAI_EMBEDDING_DIM = 3072  # text-embedding-3-large dimension
OPENAI_CHAT_MODEL = "gpt-4o-mini"

# Embedding Settings
MAX_TEXT_LENGTH = 8000  # OpenAI token limit
EMBEDDING_BATCH_SIZE = 100

# Scoring Weights
SCORE_WEIGHTS = {
    "match": 0.35,
    "skill": 0.30,
    "experience": 0.25,
    "education": 0.10
}

# Score Thresholds
SCORE_THRESHOLDS = {
    "excellent": 80,
    "good": 60,
    "moderate": 40,
    "poor": 0
}

# RAG Settings
RAG_TOP_K = 3  # Number of documents to retrieve
RAG_TEMPERATURE = 0.7

# Question Generation
DEFAULT_NUM_QUESTIONS = 5
MAX_QUESTIONS = 10

# Summary Settings
SUMMARY_MAX_TOKENS = 200
SUMMARY_TEMPERATURE = 0.7

# Feedback Settings
FEEDBACK_MAX_TOKENS = 500
FEEDBACK_TEMPERATURE = 0.7

