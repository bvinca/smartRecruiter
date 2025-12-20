# SmartRecruiter AI Module

This directory contains all AI-related functionality for the SmartRecruiter application.

## Structure

```
ai/
├── nlp/                    # Natural Language Processing
│   ├── parser.py          # Resume parsing and text extraction
│   ├── skill_extraction.py # Skill detection from text
│   └── preprocess.py      # Text normalization and cleaning
│
├── embeddings/            # Semantic embeddings
│   ├── vectorizer.py      # Convert text to embeddings
│   ├── similarity.py      # Calculate similarity scores
│   └── vector_store.py    # Optional vector DB wrapper (future)
│
├── llm/                   # Large Language Model interactions
│   ├── openai_client.py   # OpenAI API client with retries
│   ├── summarizer.py      # Generate candidate summaries
│   └── question_generator.py # Generate interview questions
│
├── rag/                   # Retrieval-Augmented Generation
│   ├── retriever.py       # Retrieve context from database
│   ├── generator.py       # Generate context-aware responses
│   └── rag_pipeline.py   # Complete RAG pipeline
│
├── evaluation/            # AI evaluation and metrics (future)
│   ├── fairness_checker.py
│   ├── ranking_metrics.py
│   └── performance_eval.py
│
└── ai_utils/             # Common utilities
    ├── prompts.py         # Prompt templates
    ├── helpers.py         # Helper functions
    └── constants.py       # Configuration constants
```

## Usage

### NLP - Resume Parsing

```python
from ai.nlp import ResumeParser, SkillExtractor

parser = ResumeParser()
parsed_data = parser.parse_file(file_content, "resume.pdf")

# Extract skills
skill_extractor = SkillExtractor()
skills = skill_extractor.extract_skills(parsed_data["resume_text"])
```

### Embeddings - Semantic Matching

```python
from ai.embeddings import EmbeddingVectorizer, SimilarityCalculator

vectorizer = EmbeddingVectorizer()
resume_embedding = vectorizer.generate_embedding(resume_text)
job_embedding = vectorizer.generate_embedding(job_description)

# Calculate similarity
similarity = SimilarityCalculator.cosine_similarity(resume_embedding, job_embedding)
match_score = SimilarityCalculator.calculate_match_score(resume_embedding, job_embedding)
```

### LLM - Summaries and Questions

```python
from ai.llm import Summarizer, QuestionGenerator

summarizer = Summarizer()
summary = summarizer.summarize_candidate(parsed_data, job_description)

question_gen = QuestionGenerator()
questions = question_gen.generate_interview_questions(parsed_data, job_description, num_questions=5)
```

### RAG - Context-Aware Generation

```python
from ai.rag import RAGPipeline

rag = RAGPipeline()
summary_data = rag.generate_summary(resume_text, job_description)
feedback = rag.generate_feedback(resume_text, job_description, scores)
questions = rag.generate_interview_questions(resume_text, job_description)
```

## Dependencies

- **OpenAI API**: Required for embeddings and LLM features
- **PyMuPDF**: Preferred for PDF parsing (fallback to PyPDF2)
- **python-docx**: For DOCX file parsing
- **spaCy**: Optional (not compatible with Python 3.14+)
- **LangChain**: Optional (for advanced RAG features)
- **ChromaDB**: Optional (for vector storage)

## Configuration

Set environment variables:
- `OPENAI_API_KEY`: Required for AI features
- `CHROMA_PERSIST_DIR`: Optional, for ChromaDB persistence

## Notes

- All modules have graceful fallbacks if dependencies are missing
- spaCy is optional (regex fallbacks work effectively)
- LangChain is optional (direct OpenAI API works)
- ChromaDB is optional (embeddings stored in PostgreSQL)

