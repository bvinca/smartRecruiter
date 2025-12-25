# SmartRecruiter: Project Scope and Feature Plan

## 1. Overview

**SmartRecruiter** is an AI-powered Applicant Tracking System (ATS) designed to automate and enhance recruitment workflows through **embedded AI**, **Natural Language Processing (NLP)**, and **Retrieval-Augmented Generation (RAG)**.  
The system supports both **recruiters** and **applicants**, focusing on intelligent resume parsing, fair candidate evaluation, and automated decision support.

This document defines the project scope, feature plan, and academic justification for each module.  
It ensures the project remains focused on its dissertation goal:  
> *“To design and develop a smart, explainable, and fair AI-based recruitment system that automates the evaluation and communication process.”*

---

## 2. Project Architecture Summary

### Directory Structure

smartRecruiter/
├── ai/ → Core AI logic and intelligent processing
│ ├── nlp/ → Resume parsing and text extraction
│ ├── embeddings/ → Semantic embeddings and similarity scoring
│ ├── rag/ → Retrieval-Augmented Generation pipeline
│ ├── evaluation/ → Candidate scoring and fairness modules
│ ├── explanation/ → Explainable AI reasoning layer
│ ├── visualization/ → Skill and bias visualization tools
│ ├── enhancement/ → Contextual job enhancement (optional)
│ └── tests/ → AI unit and integration tests
│
├── backend/ → FastAPI application and core business logic
│ ├── app/ → Routers, models, and services
│ └── main.py → Entry point for backend API
│
├── frontend/ → React-based user interface
│ ├── src/ → Recruiter and applicant dashboards
│ ├── public/ → Static assets
│ └── package.json → Frontend configuration
│
└── docs/ → Documentation and project reports

yaml
Copy code

---

## 3. In-Scope Features (Core)

These features define the **core research and development focus** of SmartRecruiter.  
They are essential for demonstrating the system’s AI intelligence, automation, and academic value.

| Feature | Description | AI/Academic Justification |
|----------|--------------|---------------------------|
| **1. Resume Parsing (NLP)** | Extracts structured data (skills, experience, education) from CVs using spaCy / transformer models. | Demonstrates NLP pipeline implementation and text-to-structure transformation. |
| **2. Semantic Scoring Engine** | Uses embeddings to calculate similarity between candidate profiles and job descriptions. | Applies semantic vector similarity and cosine scoring — core of AI-driven evaluation. |
| **3. AI Fairness and Bias Evaluation** | Audits scores to ensure no bias based on gender, age, or education background. | Addresses explainability and ethics, aligning with modern AI research standards. |
| **4. RAG Reasoning Layer** | Uses Retrieval-Augmented Generation to provide reasoning behind AI scores. | Incorporates LLM reasoning and retrieval — novel, high-impact academic contribution. |
| **5. Explainable AI (XAI)** | Generates textual explanations of candidate evaluation. | Makes the system transparent and interpretable — key dissertation focus. |
| **6. Email Communication Automation** | Generates polite and personalized candidate messages for interview invites, rejections, or feedback. | Demonstrates practical application of LLM text generation. |
| **7. Applicant Tracking Workflow** | Automates candidate progress: *Applied → Shortlisted → Interviewed → Hired*. | Defines the operational layer of the ATS — connects AI results to workflow. |
| **8. Multi-Role System (Recruiter & Applicant)** | Recruiter manages postings and candidate evaluations; applicant tracks submission and feedback. | Ensures a real-world, end-to-end demonstration. |

---

## 4. Near-Scope / Optional Enhancements

These are **advanced but optional** features that improve usability and intelligence without expanding beyond the ATS domain.

| Feature | Description | Purpose |
|----------|--------------|----------|
| **1. Skill Gap Visualization** | Displays missing or matched skills in a visual chart. | Improves recruiter insight and transparency. |
| **2. Candidate Summary Generator** | Creates short AI-generated summaries of applicants for recruiter dashboards. | Saves recruiter time; enhances interpretability. |
| **3. Adaptive Scoring Thresholds** | Dynamically adjusts shortlisting score thresholds based on candidate pool. | Adds self-optimization logic to the AI system. |
| **4. Bias Visualization Dashboard** | Visual comparison of average scores across candidate demographics. | Supports ethical AI reporting. |
| **5. Self-Evaluation Feedback for Applicants** | AI-generated feedback highlighting skills to improve. | Enhances fairness and user engagement. |

---

## 5. Out-of-Scope Features (Future Work)

These features, while valuable, extend beyond the defined dissertation scope and should be considered **future research directions**.

| Feature | Description | Reason for Exclusion |
|----------|--------------|----------------------|
| **Job Recommendation System** | Recommends positions to applicants based on profiles. | Shifts focus from ATS to recommender systems. |
| **Interview Scheduling Calendar** | Syncs availability and sets appointments. | Operational HR tool, not AI-focused. |
| **Chat-Based Recruiter Assistant** | Interactive chatbot for recruitment queries. | Adds complexity; limited academic value for current phase. |
| **Organization-Level Analytics Dashboard** | Metrics and KPIs for HR management. | Moves into HRMS (Human Resource Management System) scope. |

---

## 6. Evaluation Plan

To validate the system and ensure dissertation quality, the following evaluation plan will be implemented:

| Test Type | Description | Purpose |
|------------|--------------|----------|
| **Unit Testing (AI Modules)** | Validate NLP parsing, embedding scoring, and fairness models. | Ensures core logic correctness. |
| **Integration Testing** | Test end-to-end resume upload → scoring → explanation → dashboard display. | Confirms functional pipeline. |
| **Fairness Evaluation** | Compare AI scoring outcomes across multiple synthetic candidate groups. | Tests bias mitigation. |
| **User Experience Testing** | Recruiter and applicant dashboards tested for usability. | Demonstrates real-world viability. |

---

## 7. Technical Stack Summary

| Layer | Technologies | Purpose |
|--------|---------------|----------|
| **Frontend** | React.js, TailwindCSS | Applicant and recruiter dashboards |
| **Backend** | FastAPI, SQLAlchemy, PostgreSQL | Core business logic and API layer |
| **AI Layer** | Python, spaCy, HuggingFace, OpenAI API, LangChain | Resume parsing, RAG, scoring, reasoning |
| **Database** | PostgreSQL | Persistent storage for users, jobs, and applications |
| **Testing** | Pytest, JSON test data | Unit and E2E verification |
| **Deployment** | Uvicorn, GitHub Actions | Local and remote environment setup |

---

## 8. Summary

SmartRecruiter focuses on creating a **next-generation AI-driven recruitment system** that improves fairness, explainability, and recruiter efficiency.  
By combining **NLP, embeddings, RAG, and explainable AI**, the system sets itself apart from traditional Applicant Tracking Systems.

The project strikes the right balance between **academic rigor and practical implementation**, ensuring it remains achievable within the bachelor dissertation timeline while demonstrating strong AI integration and ethical design principles.

---

**Author:** Bora Vincass  
**Project Title:** *SmartRecruiter: AI-Enhanced Application Tracking System*  
**Advisor:** [Name Placeholder]  
**University:** [Your Institution Name]  
**Date:** [Insert Date]