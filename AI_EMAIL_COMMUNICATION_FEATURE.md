# 🤖 AI Email Communication Feature — SmartRecruiter

## 1. Overview
This document outlines the design and implementation of the **AI-based automated recruiter communication system** for SmartRecruiter.  
The feature allows recruiters to automatically generate personalized and context-aware email responses to candidates based on their application results, interview outcomes, or skill evaluation.  

The communication layer integrates tightly with the AI modules (Scoring, Fairness, Explainable AI) to produce **ethical, data-driven, and human-like messages**.

---

## 2. Objectives

The key goals of this feature are:

- ✅ Automate recruiter–applicant communication while maintaining professionalism.  
- 🧠 Generate personalized messages reflecting actual candidate performance and profile data.  
- ⚖️ Ensure fairness and transparency — messages should be consistent and bias-free.  
- 💬 Support multiple communication contexts (e.g., feedback, shortlisting, rejection, interview scheduling).  
- 🌍 Enable multilingual email generation for international candidates.  

---

## 3. Core Functionality

The system uses **OpenAI’s GPT-based model** through the `openai_client.py` in the AI layer, combined with candidate evaluation results from the backend.

| Type of Message | Trigger | Input Data | Output Example |
|------------------|----------|-------------|----------------|
| **Acknowledgment Email** | When an applicant applies for a job | Applicant name, job title | “Thank you for applying for the Full-Stack AI Engineer role…” |
| **Feedback Email** | After resume scoring or interview | Score breakdown, missing skills | “We were impressed by your Python experience. Improving your React skills could strengthen your fit.” |
| **Rejection Email** | After a low overall score | Overall score, skills gap | “After careful evaluation, we have decided not to move forward at this stage…” |
| **Interview Invitation** | After shortlist threshold | Candidate name, job details | “We’d love to invite you to an interview for the FastAPI Developer position…” |

---

## 4. Architecture

Frontend (Recruiter Dashboard)
│
▼
[Backend: EmailRouter → EmailService]
│
▼
[AI Layer: ai/llm/email_generator.py]
│
▼
[OpenAI API → Generated Email Text]
│
▼
[Backend: Store in DB → Send via SMTP or API]
│
▼
Frontend (Displayed in Recruiter’s Dashboard)

yaml
Copy code

---

## 5. File Structure

smartRecruiter/
│
├── ai/
│ ├── llm/
│ │ ├── email_generator.py # Core AI logic for email creation
│ │ └── openai_client.py # Wrapper for GPT API requests
│ └── templates/
│ └── email_templates.json # Default message templates and tone settings
│
├── backend/
│ ├── app/
│ │ ├── routers/
│ │ │ └── emails.py # FastAPI route for triggering email generation
│ │ └── services/
│ │ └── email_service.py # Calls the AI layer and sends emails
│ └── database/
│ └── models.py # EmailLog model for tracking communications

python
Copy code

---

## 6. Implementation Steps

### Step 1️⃣ — Create AI Email Generator
File: `ai/llm/email_generator.py`

```python
from ai.llm.openai_client import client

class EmailGenerator:
    def __init__(self):
        self.default_tone = "professional, concise, and encouraging"

    def generate_email(self, candidate_name, job_title, score_data, message_type="feedback"):
        prompt = f"""
        You are an HR recruiter writing a {message_type} email to a candidate.
        - Candidate name: {candidate_name}
        - Job title: {job_title}
        - Score summary: {score_data}
        - Tone: {self.default_tone}

        Write a polite, personalized email between 100–150 words.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful HR assistant."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
Step 2️⃣ — Integrate in Backend
File: backend/app/services/email_service.py

python
Copy code
from ai.llm.email_generator import EmailGenerator

class EmailService:
    def __init__(self):
        self.generator = EmailGenerator()

    def send_feedback_email(self, candidate, job, score_data):
        content = self.generator.generate_email(
            candidate_name=candidate.name,
            job_title=job.title,
            score_data=score_data,
            message_type="feedback"
        )
        # Here you can integrate with SendGrid, AWS SES, or just save to DB
        print(f"Generated email for {candidate.name}:\n{content}")
        return content
Step 3️⃣ — Add API Endpoint
File: backend/app/routers/emails.py

python
Copy code
from fastapi import APIRouter, HTTPException
from app.services.email_service import EmailService

router = APIRouter(prefix="/emails", tags=["emails"])
email_service = EmailService()

@router.post("/generate")
async def generate_email(candidate_name: str, job_title: str, score: float):
    try:
        content = email_service.send_feedback_email(
            candidate={"name": candidate_name},
            job={"title": job_title},
            score_data={"overall_score": score}
        )
        return {"success": True, "email": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
7. Integration Points
AI Layer: Uses openai_client for text generation.

Backend: Uses EmailService to handle generation and delivery.

Frontend: New recruiter dashboard tab → “AI-Generated Emails”.

Database (optional): Store generated messages for audit and re-sending.

8. Testing the Feature
✅ Unit Test
File: ai/tests/test_email_generator.py

python
Copy code
from ai.llm.email_generator import EmailGenerator

def test_email_generation():
    generator = EmailGenerator()
    email = generator.generate_email(
        "Alice Brown", "Python Developer", {"overall_score": 78}, "feedback"
    )
    assert "Alice" in email and "Python Developer" in email
✅ Manual Test (via API)
bash
Copy code
curl -X POST "http://127.0.0.1:8000/emails/generate" \
     -H "Content-Type: application/json" \
     -d '{"candidate_name":"Alice Brown","job_title":"Python Developer","score":78}'
9. Future Enhancements
Feature	Description
🗣️ Multilingual Mode	Detect applicant language and generate localized emails
🎯 Tone Control	Allow recruiters to choose tone (“formal”, “friendly”, “brief”)
📅 Interview Scheduling	Integrate with Google Calendar or Outlook API
🧾 Audit Log	Store and visualize communication history per candidate
🧠 Feedback Analytics	Track how email tone or message type affects candidate engagement

10. Academic Impact
This feature adds human–AI interaction and ethical communication capabilities, making the system more than a data processor.
It demonstrates applied Natural Language Generation (NLG), personalization through contextual data, and fairness-driven automation — all relevant topics for academic research in AI-based HR systems.

Author: Bora Vinca
Module: AI Layer — SmartRecruiter
Date: December 2025
Version: 1.0.0

yaml
Copy code
