# SmartRecruiter Resume Parsing & AI Analysis — Implementation Plan

## 1️⃣ Overview

This document defines the full technical plan for implementing the **AI Resume Parsing & Analysis** subsystem within the SmartRecruiter project.  
The goal is to automatically extract, interpret, and analyze information from applicant resumes (PDF, DOCX, TXT) and provide structured candidate data, AI-generated summaries, and contextual interview question suggestions.

This subsystem is a core feature of the SmartRecruiter Application Tracking System (ATS).

---

## 2️⃣ System Goals

- Automate the reading and interpretation of resumes.
- Convert unstructured resume text into structured data (name, contact info, skills, experience, education, etc.).
- Apply NLP and AI models to summarize candidates’ profiles.
- Match candidate profiles to job descriptions using semantic similarity.
- Provide recruiters with context-aware insights (summaries, interview questions).

---

## 3️⃣ Functional Flow

### Step 1: File Upload
- Applicant uploads a resume through the frontend UI.
- File types supported: `.pdf`, `.docx`, `.txt`.
- File is sent to the FastAPI backend via a POST request.

### Step 2: Text Extraction
- Backend reads and extracts raw text using:
  - `PyMuPDF` (for PDF parsing)
  - `python-docx` (for DOCX)
- The extracted text is normalized (removed newlines, special symbols).

### Step 3: Entity Detection (NLP)
- Use `spaCy` for entity extraction:
  - Entities: PERSON, ORG, GPE, DATE, EDUCATION, SKILL (custom).
- Supplemented with regex for emails and phone numbers.
- Store entities as a structured JSON object.

### Step 4: Skill Extraction
- Maintain a custom keyword list for known technical and soft skills.
- Scan text for matches.
- Example: ["Python", "FastAPI", "SQL", "AWS", "Communication", "Leadership"]

### Step 5: Semantic Enhancement (AI)
- Pass the parsed JSON to an **OpenAI GPT-4-turbo** model via API.
- Prompt examples:
  - “Summarize this candidate’s experience in one paragraph.”
  - “List 5 interview questions for this candidate based on their background.”
- Output is stored and displayed to recruiters in the admin dashboard.

### Step 6: Job Matching
- Compare parsed resume embeddings against job description embeddings using:
  - `text-embedding-3-large`
- Rank candidates by cosine similarity score.

### Step 7: Storage
- Save parsed resume data and AI results to PostgreSQL.
- Tables: `applicants`, `resumes`, `skills`, `resume_analysis`.

---

## 4️⃣ File Architecture

/backend
│
├── main.py # FastAPI entry point
├── database.py # DB connection + models base
├── models/
│ ├── user.py
│ ├── job.py
│ ├── application.py
│ └── resume.py
│
├── routes/
│ ├── resume.py # Resume upload + parse endpoint
│ └── ai_analysis.py # AI summarization & question generation
│
├── parsers/
│ ├── init.py
│ ├── resume_parser.py # PDF/DOCX text extraction + NLP entity parsing
│ ├── skill_extractor.py # Keyword-based skill detection
│ └── summarizer.py # AI model-based summarization & ranking
│
├── utils/
│ ├── embeddings.py # Semantic similarity functions
│ └── file_helpers.py # Temporary file handling utilities
│
└── .env # OPENAI_API_KEY, DATABASE_URL

yaml
Copy code

---

## 5️⃣ Required Libraries

```bash
pip install fastapi uvicorn psycopg2-binary sqlalchemy spacy pymupdf python-docx openai langchain numpy scikit-learn python-dotenv
python -m spacy download en_core_web_sm

6️⃣ Data Flow Summary
Stage	Input	Output	Tools
Upload	File	Temporary file	FastAPI
Text Extraction	PDF/DOCX	Plain text	PyMuPDF, python-docx
NLP Parsing	Text	Entities (JSON)	spaCy, regex
Skill Extraction	Text	Skills list	Keyword matching
Summarization	Parsed JSON	AI summary	OpenAI GPT
Ranking	Embeddings	Score	LangChain, OpenAI
Storage	JSON	Database record	PostgreSQL
7️⃣ API Endpoints
POST /resume/upload

Upload a resume file and extract structured data.

Request:

form-data containing file

Response:

{
  "parsed_resume": {
    "name": "Nikola Dachevski",
    "email": "nikola@example.com",
    "skills": ["Python", "FastAPI", "SQL"],
    "education": ["University of Skopje"],
    "experience": "2 years backend development"
  }
}

POST /resume/analyze

Send structured resume data for AI summarization and interview question generation.

Response:

{
  "summary": "Nikola is an experienced backend developer specializing in AI-powered web systems.",
  "interview_questions": [
    "Describe your experience with NLP systems.",
    "How would you deploy a FastAPI app with PostgreSQL?"
  ]
}

8️⃣ AI Prompts
Resume Summarization
You are an HR assistant. Summarize this candidate’s resume concisely, highlighting experience, education, and technical skills.

Interview Question Generation
Given the following candidate resume data, generate 5 relevant technical and behavioral interview questions suitable for their profile.

Job Matching
Compare this candidate’s profile with the following job description and provide a compatibility score (0–100) based on semantic similarity.

9️⃣ Database Schema
Table	Fields	Description
applicants	id, name, email, phone	Basic applicant info
resumes	id, applicant_id, raw_text, parsed_json	Resume data
skills	id, resume_id, skill_name	Extracted skills
resume_analysis	id, resume_id, ai_summary, ai_questions	AI-generated output
🔐 10️⃣ Environment Variables (.env)
DATABASE_URL=postgresql://smartrecruiter:smartrecruiter@localhost:5432/smartrecruiter
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

✅ 11️⃣ Expected Outcomes

Fully functional API endpoints for resume parsing and summarization.

Structured resume data stored in PostgreSQL.

Integration with OpenAI GPT for summarization and question generation.

Ready-to-showcase feature for dissertation demonstration.

Scalability for adding ranking, bias analysis, and fairness modules later.

🧠 12️⃣ Future Enhancements

Multi-language resume parsing (via HuggingFace models).

Bias detection in candidate summaries.

Integration with front-end dashboards (React/Next.js).

Vector database for semantic job–candidate matching (e.g., FAISS or Pinecone).

Prepared for SmartRecruiter Dissertation Project — 2025