 🧭 1️⃣ Applicant Action: Upload CV

Frontend (User Experience):

The applicant logs in or signs up.

They navigate to “Apply for Position” or “Upload Resume.”

They upload their .pdf, .docx, or .txt file via a form.

Backend (FastAPI Route: /resume/upload):

The uploaded file is received as a FastAPI UploadFile.

File metadata (name, type, size, applicant_id) is logged.

The file is temporarily saved in /tmp or a local uploads/ folder.

📦 Example:

{
  "applicant_id": 12,
  "filename": "Nikola_Dachevski_CV.pdf",
  "timestamp": "2025-12-18T02:00:00Z"
}

🧠 2️⃣ Text Extraction

Purpose: Convert resume from binary → readable text.

The backend uses PyMuPDF (for .pdf) or python-docx (for .docx).

The text is extracted and cleaned (remove headers, footers, symbols).

It’s stored temporarily in memory as a string for NLP processing.

📄 Example Output:

Nikola Dachevski
Backend Developer
Email: nikola@example.com
Phone: +389 70 123 456
Education: BSc Computer Science - UKIM
Skills: Python, FastAPI, PostgreSQL, NLP, RAG systems
Experience: 2 years backend development at AI Labs

🧩 3️⃣ Resume Parsing (NLP)

Purpose: Identify and extract structured entities.

A spaCy NLP pipeline runs to detect named entities (PERSON, ORG, GPE, etc.).

Regex extracts email and phone.

A custom skills extractor matches known skills.

The system creates a structured dictionary of parsed data.

📊 Output Example:

{
  "name": "Nikola Dachevski",
  "email": "nikola@example.com",
  "phone": "+389 70 123 456",
  "education": ["BSc Computer Science - UKIM"],
  "experience": ["Backend Developer at AI Labs"],
  "skills": ["Python", "FastAPI", "PostgreSQL", "NLP"]
}

🤖 4️⃣ AI Processing (RAG + GPT)

Purpose: Generate intelligent recruiter insights.

Your backend uses OpenAI or LangChain to:

Summarize candidate’s background.

Generate tailored interview questions.

Optionally, compare resume to job descriptions (semantic similarity).

📘 Example Prompts:

“Summarize this candidate’s resume for a recruiter in 3 sentences.”

“Based on this resume, generate 5 interview questions relevant to the applicant’s experience and skills.”

📜 AI Output Example:

{
  "summary": "Nikola is an experienced backend developer with strong skills in FastAPI and NLP systems, having contributed to AI projects involving RAG pipelines.",
  "interview_questions": [
    "Describe your experience building REST APIs with FastAPI.",
    "How do you integrate NLP models into backend systems?",
    "What is your experience with semantic search or vector databases?"
  ]
}

🗄️ 5️⃣ Database Storage

Purpose: Persist parsed and AI-analyzed data.

Your backend creates or updates records in the database:

Table	Purpose
applicants	Applicant user info
resumes	Raw file text + metadata
parsed_data	Extracted JSON (structured info)
resume_analysis	AI-generated summaries and questions

📦 Example SQLAlchemy insert:

new_resume = Resume(
    applicant_id=12,
    filename="Nikola_Dachevski_CV.pdf",
    raw_text=extracted_text,
    parsed_json=parsed_resume_data,
    summary=ai_summary,
    interview_questions=ai_questions
)
db.add(new_resume)
db.commit()

📊 6️⃣ Feedback to the Applicant

Frontend:

The applicant sees a confirmation message like:

“✅ Your resume was successfully uploaded and parsed!”

Recruiter Dashboard:

Recruiters see structured applicant data.

They can view AI summaries and interview questions directly.

📈 7️⃣ Optional: Candidate Ranking (Next Phase)

Once multiple resumes are uploaded:

The system generates embeddings for each parsed resume.

It computes semantic similarity with job descriptions.

Recruiters get a ranked list of applicants.

📘 Example:

Rank	Name	Match %
1	Nikola Dachevski	92%
2	Elena Petrova	84%
3	Marko Stojanov	76%
🔐 8️⃣ Security and Ethics Considerations

All resumes are processed locally (not stored in plaintext).

.env file stores OpenAI key securely.

Sensitive data (e.g., phone, email) is masked when unnecessary.

System logs only metadata for debugging.

Bias detection (optional future extension) can flag gender/age bias in parsing.

🧠 9️⃣ What Recruiters See (End Result)

Recruiters will have access to:

Applicant’s structured resume profile.

AI-generated summaries.

Suggested interview questions.

Ranking score for each job application.

Download links for original resume files.

🧾 Summary of Workflow
Step	Description	Tools
1	Upload resume	FastAPI file upload
2	Extract text	PyMuPDF / python-docx
3	NLP parsing	spaCy + regex
4	AI summarization	OpenAI GPT (via RAG)
5	Store structured data	PostgreSQL (SQLAlchemy)
6	Return confirmation	FastAPI response
7	Display insights	Recruiter dashboard