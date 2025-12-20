# SmartRecruiter Architecture

## System Overview

SmartRecruiter is a full-stack AI-powered Applicant Tracking System (ATS) that automates resume analysis, candidate scoring, and provides intelligent insights for recruiters. The system uses AI, NLP, and semantic embeddings to match candidates with job positions and generate contextual interview questions.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.14)
- **Database**: PostgreSQL 15 (or SQLite for development)
- **Vector Store**: ChromaDB (optional, for RAG)
- **AI/ML**: 
  - OpenAI GPT-4o-mini for text generation (summaries, interview questions)
  - OpenAI text-embedding-3-large for semantic embeddings
  - LangChain (optional) for RAG workflows
- **NLP**: 
  - Regex-based parsing (spaCy optional, not compatible with Python 3.14)
  - PyMuPDF for PDF text extraction
  - python-docx for DOCX parsing
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose), bcrypt for password hashing
- **API Documentation**: OpenAPI/Swagger (auto-generated)

### Frontend
- **Framework**: React 18
- **State Management**: TanStack Query (React Query) for server state
- **Routing**: React Router v6 with protected routes
- **HTTP Client**: Axios with interceptors
- **UI Components**: Custom CSS with modern design system
- **Icons**: Lucide React
- **Charts**: Recharts for analytics
- **Notifications**: React Hot Toast
- **Date Handling**: date-fns

### DevOps
- **Containerization**: Docker & Docker Compose (configured)
- **CI/CD**: GitHub Actions (configured)
- **Version Control**: Git

## Architecture Layers

### 1. Presentation Layer (Frontend)

```
React Application
├── Pages
│   ├── Authentication (Login, Register)
│   ├── Applicant Pages
│   │   ├── Dashboard
│   │   ├── Profile Management
│   │   ├── Job Browsing
│   │   ├── Job Details & Application
│   │   └── Applications Tracking
│   └── Recruiter Pages
│       ├── Dashboard
│       ├── Job Management
│       ├── Applicants View
│       ├── Analytics
│       └── Interview Scheduling
├── Components
│   ├── ProtectedRoute (role-based access)
│   ├── ApplicantLayout / RecruiterLayout
│   ├── ApplicationSuccess (parsed resume feedback)
│   ├── ApplicantDetail (modal)
│   └── UploadModal
└── API Client (Axios with JWT injection)
```

**Key Features:**
- Role-based routing and layouts
- Real-time updates via React Query
- Toast notifications for user feedback
- Modal-based workflows
- Responsive design
- Application success screen with parsed resume data

### 2. API Layer (Backend)

```
FastAPI Application
├── Routers
│   ├── /auth (authentication)
│   ├── /jobs (job management)
│   ├── /applicants (applicant management)
│   ├── /applications (application workflow)
│   ├── /profile (user profile)
│   ├── /interviews (interview scheduling)
│   ├── /analytics (recruitment analytics)
│   ├── /resume (resume parsing endpoints)
│   └── /ranking (candidate ranking)
├── Services (business logic)
│   ├── Resume Parser
│   ├── Scoring Service
│   ├── Embedding Service
│   ├── RAG Service
│   ├── Skill Extractor
│   ├── Summarizer (AI)
│   └── Auth Service
├── Models (SQLAlchemy ORM)
└── Schemas (Pydantic validation)
```

**API Endpoints:**

#### Authentication (`/auth`)
- `POST /auth/register` - User registration (applicant/recruiter)
- `POST /auth/login` - User login (returns JWT token)
- `GET /auth/me` - Get current user info

#### Jobs (`/jobs`)
- `GET /jobs` - List jobs (role-based: recruiters see their jobs, applicants see active jobs)
- `GET /jobs/{id}` - Get job details
- `POST /jobs` - Create job (recruiter only)
- `PUT /jobs/{id}` - Update job (recruiter only)
- `DELETE /jobs/{id}` - Delete job (recruiter only)

#### Applicants (`/applicants`)
- `GET /applicants` - List applicants (role-based access)
- `GET /applicants/{id}` - Get applicant details
- `POST /applicants/upload` - Upload and parse CV
- `POST /applicants/{id}/score` - Calculate scores
- `POST /applicants/{id}/summary` - Generate AI summary
- `PUT /applicants/{id}` - Update applicant
- `GET /applicants/{id}/download` - Download resume file (recruiter only)

#### Applications (`/applications`)
- `POST /applications/apply/{job_id}` - Apply to job with resume (applicant only)
- `GET /applications` - List applications (role-based)
- `GET /applications/{id}` - Get application details
- `PUT /applications/{id}` - Update application status (recruiter only)

#### Profile (`/profile`)
- `GET /profile` - Get user profile
- `PUT /profile` - Update profile
- `POST /profile/resume` - Upload resume to profile (applicant only)
- `DELETE /profile` - Deactivate account

#### Interviews (`/interviews`)
- `POST /interviews` - Schedule interview (recruiter only)
- `GET /interviews` - List interviews (role-based)
- `GET /interviews/{id}` - Get interview details
- `PUT /interviews/{id}` - Update interview (recruiter only)

#### Analytics (`/analytics`)
- `GET /analytics` - Get recruitment analytics (recruiter only)
  - Total jobs, active jobs
  - Application counts by status
  - Average scores
  - Top skills
  - Applications by job

#### Resume (`/resume`)
- `POST /resume/upload` - Upload and parse resume (general)
- `POST /resume/analyze` - Analyze structured resume data for AI insights

#### Ranking (`/ranking`)
- `GET /ranking/job/{job_id}` - Get ranked candidates for a job (recruiter only)

### 3. Business Logic Layer

#### Resume Parser Service
**Location**: `backend/app/services/resume_parser.py`

**Capabilities:**
- Extracts text from PDF (PyMuPDF with PyPDF2 fallback), DOCX, TXT
- Parses structured data using regex patterns:
  - Contact information (email, phone)
  - Name extraction (first line or regex patterns)
  - Skills (keyword-based matching)
  - Work experience (pattern matching)
  - Education (keyword and pattern matching)
  - Years of experience (regex and estimation)
- Text normalization (removes excessive newlines, special symbols)
- **Note**: spaCy not used (incompatible with Python 3.14), regex fallbacks work effectively

**Output Structure:**
```python
{
    "first_name": str,
    "last_name": str,
    "email": str,
    "phone": str,
    "skills": List[str],
    "technical_skills": List[str],
    "soft_skills": List[str],
    "experience_years": float,
    "education": List[Dict],
    "work_experience": List[Dict],
    "resume_text": str,
    "entities": Dict  # Empty if spaCy not available
}
```

#### Skill Extractor Service
**Location**: `backend/app/services/skill_extractor.py`

**Capabilities:**
- Comprehensive keyword lists for technical and soft skills
- Case-insensitive matching with word boundaries
- Returns unique, sorted skill lists
- Separate methods for technical vs soft skills

#### Embedding Service
**Location**: `backend/app/utils/embeddings.py`

**Capabilities:**
- Generates semantic embeddings using OpenAI `text-embedding-3-large`
- Calculates cosine similarity between embeddings
- Converts similarity to match scores (0-100)
- Pure Python fallback if numpy unavailable
- Batch embedding generation

#### Scoring Service
**Location**: `backend/app/services/scoring_service.py`

**Multi-dimensional Scoring:**
- **Match Score (35%)**: Semantic similarity between resume and job description
- **Skill Score (30%)**: Overlap of required vs applicant skills
- **Experience Score (25%)**: Years of experience and relevance
- **Education Score (10%)**: Degree relevance to job requirements
- **Overall Score**: Weighted combination

**Output:**
```python
{
    "match_score": float,
    "skill_score": float,
    "experience_score": float,
    "education_score": float,
    "overall_score": float,
    "explanation": str,
    "resume_embedding": List[float]  # Optional
}
```

#### RAG Service
**Location**: `backend/app/services/rag_service.py`

**Capabilities:**
- Uses OpenAI GPT-4o-mini for text generation
- LangChain optional (falls back to direct OpenAI API)
- Generates:
  - Candidate summaries (context-aware)
  - Interview questions (tailored to candidate and job)
  - Feedback (based on scores and resume)
- Retrieval-augmented generation for context-aware responses
- ChromaDB optional (works without it)

#### Summarizer Service
**Location**: `backend/app/services/summarizer.py`

**Capabilities:**
- Direct OpenAI API integration
- Generates candidate summaries (3-5 sentences)
- Generates interview questions (5 questions)
- Context-aware (considers job description)
- Graceful error handling

#### Auth Service
**Location**: `backend/app/services/auth_service.py`

**Capabilities:**
- Password hashing with bcrypt
- JWT token creation and verification
- User authentication
- Password truncation for bcrypt 72-byte limit
- User creation and management

### 4. Data Layer

#### PostgreSQL (Relational Data)

**Tables:**

**users**
- id (PK)
- email (unique, indexed)
- hashed_password
- role (applicant/recruiter)
- first_name, last_name
- company_name (for recruiters)
- is_active
- created_at, updated_at

**jobs**
- id (PK)
- title, description, requirements
- location, salary_range
- status (active/closed/draft)
- recruiter_id (FK → users.id)
- created_at, updated_at

**applicants**
- id (PK)
- job_id (FK → jobs.id)
- first_name, last_name, email, phone
- resume_text, resume_file_path, resume_file_type
- skills (JSON array)
- experience_years
- education (JSON array)
- work_experience (JSON array)
- match_score, skill_score, experience_score, education_score, overall_score
- ai_summary, ai_feedback
- interview_questions (JSON array)
- status (pending/reviewing/shortlisted/rejected/hired)
- notes
- created_at, updated_at

**applications**
- id (PK)
- user_id (FK → users.id)
- job_id (FK → jobs.id)
- applicant_id (FK → applicants.id, nullable)
- status (pending/reviewing/shortlisted/rejected/hired)
- notes
- created_at, updated_at

**embeddings**
- id (PK)
- applicant_id (FK → applicants.id)
- job_id (FK → jobs.id)
- embedding_vector (JSON array)
- created_at

**interviews**
- id (PK)
- application_id (FK → applications.id)
- scheduled_at
- location, meeting_link
- notes
- status (scheduled/completed/cancelled)
- created_at, updated_at

#### ChromaDB (Vector Store - Optional)
- Stores document embeddings for RAG
- Enables semantic search
- Used for retrieval-augmented generation
- Works without ChromaDB (direct OpenAI API fallback)

## Data Flow

### Complete Resume Parsing & Application Workflow

1. **User Registration/Login**
   - User registers with role (applicant/recruiter)
   - JWT token issued
   - Token stored in frontend (localStorage)

2. **Job Application Flow (Applicant)**
   ```
   Applicant → Browse Jobs → View Job Details → Upload Resume → Submit Application
   ```

3. **Resume Upload & Parsing**
   - File uploaded to `/applications/apply/{job_id}`
   - Resume Parser extracts text (PDF/DOCX/TXT)
   - Text normalized
   - Structured data extracted:
     - Contact info (email, phone via regex)
     - Name (first line extraction)
     - Skills (keyword matching)
     - Education (pattern matching)
     - Work experience (pattern matching)
     - Experience years (regex + estimation)
   - Applicant record created in database
   - File saved to `uploads/` directory

4. **AI Processing (Automatic)**
   - AI Summary generated (OpenAI GPT-4o-mini)
   - Interview questions generated (5 questions, context-aware)
   - Semantic embeddings generated (OpenAI text-embedding-3-large)
   - Embeddings stored in database

5. **Scoring (Automatic)**
   - Multi-dimensional scores calculated:
     - Match score (semantic similarity)
     - Skill score (overlap)
     - Experience score
     - Education score
   - Overall score computed
   - Scores stored in applicant record

6. **Feedback to Applicant**
   - Application response includes:
     - Parsed resume data
     - Match score
     - AI summary
     - Interview questions
   - Frontend displays ApplicationSuccess component

7. **Recruiter View**
   - Recruiters see applicants for their jobs
   - Can view:
     - Parsed resume data
     - Scores (match, skill, experience, education, overall)
     - AI summary
     - Interview questions
     - Download resume file
   - Can rank candidates by semantic similarity
   - Can schedule interviews
   - Can update application status

8. **Candidate Ranking**
   - Recruiter requests ranking for a job
   - System generates/retrieves embeddings
   - Calculates semantic similarity with job description
   - Returns ranked list with match scores

### Authentication Flow

1. User registers → Password hashed (bcrypt) → User created → JWT token issued
2. User logs in → Password verified → JWT token issued
3. Protected endpoints → JWT verified → Role checked → Access granted/denied

### Role-Based Access Control

**Applicants can:**
- View active jobs
- Apply to jobs (with resume upload)
- View their own applications
- Manage their profile
- Upload resume to profile

**Recruiters can:**
- Create, update, delete jobs
- View applicants for their jobs
- Score applicants
- Generate AI summaries
- Rank candidates
- Schedule interviews
- View analytics
- Download resume files
- Update application statuses

## Security Considerations

1. **Authentication**: JWT tokens with expiration
2. **Password Security**: bcrypt hashing (with 72-byte truncation for compatibility)
3. **Input Validation**: Pydantic schemas validate all inputs
4. **File Upload**: Type checking, size limits, secure storage
5. **CORS**: Configured for specific origins
6. **Environment Variables**: Sensitive data (API keys, secrets) in .env files
7. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
8. **Role-Based Access**: Endpoints protected by role dependencies
9. **File Access**: Resume downloads restricted to recruiters for their jobs

## Performance Optimizations

1. **Database Indexing**: Primary keys, foreign keys, email indexed
2. **Connection Pooling**: SQLAlchemy connection pool
3. **Caching**: React Query caches API responses
4. **Lazy Loading**: Components loaded on demand
5. **Embedding Caching**: Store embeddings to avoid recalculation
6. **Batch Operations**: Batch embedding generation when possible
7. **Error Handling**: Graceful fallbacks (spaCy, LangChain, ChromaDB all optional)

## Scalability

### Horizontal Scaling
- Stateless API design allows multiple instances
- Database connection pooling
- Load balancer ready
- JWT tokens enable stateless authentication

### Vertical Scaling
- Optimize embedding generation (batch processing)
- Database query optimization
- Frontend code splitting
- Lazy loading of components

## Current Implementation Status

### ✅ Fully Implemented

1. **Authentication & Authorization**
   - User registration (applicant/recruiter)
   - JWT-based authentication
   - Role-based access control
   - Protected routes (frontend & backend)

2. **Resume Parsing**
   - PDF, DOCX, TXT support
   - Text extraction (PyMuPDF, python-docx)
   - Structured data extraction (regex-based)
   - Skill extraction (keyword matching)
   - Education & work experience parsing
   - Text normalization

3. **AI Features**
   - AI-generated summaries (OpenAI GPT-4o-mini)
   - Interview question generation (context-aware)
   - Semantic embeddings (OpenAI text-embedding-3-large)
   - Semantic similarity calculation
   - Candidate ranking by match score

4. **Job Management**
   - Create, read, update, delete jobs
   - Job status management
   - Role-based job visibility

5. **Application Management**
   - Apply to jobs with resume
   - Track applications
   - Update application status (recruiter)
   - Automatic parsing and scoring on application

6. **Scoring System**
   - Multi-dimensional scoring
   - Match score (semantic)
   - Skill score
   - Experience score
   - Education score
   - Overall weighted score

7. **Analytics**
   - Job statistics
   - Application counts by status
   - Average scores
   - Top skills
   - Applications by job

8. **Interview Scheduling**
   - Schedule interviews
   - Interview management
   - Status tracking

9. **Profile Management**
   - User profile CRUD
   - Resume upload to profile
   - Account deactivation

10. **Frontend Pages**
    - Login/Register
    - Applicant Dashboard
    - Applicant Profile
    - Applicant Jobs (browse)
    - Job Details (with application)
    - Applicant Applications (tracking)
    - Recruiter Dashboard
    - Job Management
    - Applicants View (with ranking)
    - Analytics Dashboard
    - Interview Management

### ⚠️ Optional/Not Used

1. **spaCy**: Not compatible with Python 3.14 (Pydantic V1 issue)
   - Regex fallbacks work effectively
   - No impact on core functionality

2. **LangChain**: Optional (direct OpenAI API works)
   - RAG service has LangChain fallback
   - Works without LangChain

3. **ChromaDB**: Optional (embeddings stored in PostgreSQL)
   - RAG works without ChromaDB
   - Direct OpenAI API used

## Monitoring & Logging

- FastAPI automatic request logging
- Error handling with proper HTTP status codes
- Frontend error boundaries
- Console logging for debugging
- Graceful error messages for users

## API Design Principles

1. **RESTful**: Follow REST conventions
2. **Versioning**: Ready for API versioning
3. **Documentation**: Auto-generated OpenAPI docs at `/docs`
4. **Error Handling**: Consistent error responses
5. **Pagination**: Support for large datasets (skip/limit)
6. **Role-Based**: Endpoints protected by role dependencies

## Error Handling Strategy

1. **Validation Errors**: 422 with detailed Pydantic messages
2. **Not Found**: 404 with resource identifier
3. **Unauthorized**: 401 for missing/invalid JWT
4. **Forbidden**: 403 for role-based access violations
5. **Server Errors**: 500 with generic message (detailed in logs)
6. **Client Errors**: 400 with explanation
7. **Service Unavailable**: 503 for missing dependencies (e.g., OpenAI not configured)

## Testing Strategy

1. **Unit Tests**: Service layer functions (recommended)
2. **Integration Tests**: API endpoints (recommended)
3. **E2E Tests**: Frontend workflows (recommended)
4. **Performance Tests**: Load testing for scoring (recommended)

## Deployment Architecture

### Development
```
Local Machine
├── Frontend (React Dev Server on :3000)
├── Backend (Uvicorn on :8000)
└── PostgreSQL (Docker or Local)
```

### Production (Docker Compose)
```
Docker Compose
├── Frontend Container (Nginx)
├── Backend Container (Uvicorn + Gunicorn)
├── PostgreSQL Container
└── ChromaDB (Optional, Persistent Volume)
```

### CI/CD Pipeline (GitHub Actions)
```
GitHub Actions
├── Backend Tests (recommended)
├── Frontend Tests (recommended)
├── Docker Build
└── Deployment (optional)
```

## Key Design Decisions

1. **Python 3.14**: Using latest Python, spaCy not required
2. **OpenAI for AI**: Direct API integration, no heavy ML dependencies
3. **Regex Parsing**: Effective fallback when spaCy unavailable
4. **PostgreSQL for Embeddings**: Storing embeddings as JSON, ChromaDB optional
5. **JWT Authentication**: Stateless, scalable
6. **Role-Based Access**: Enforced at both API and frontend levels
7. **Graceful Degradation**: All optional dependencies have fallbacks

## Future Enhancements

1. **Real-time Updates**: WebSocket support for live notifications
2. **Advanced Analytics**: ML-based predictions, trend analysis
3. **Bias Detection**: Fairness metrics dashboard
4. **Multi-language**: Support for multiple languages in resumes
5. **Video Resumes**: Video analysis capabilities
6. **Email Notifications**: Automated emails for status changes
7. **Export Features**: Export applicant data, reports
8. **Advanced Search**: Full-text search, filtering
9. **Bulk Operations**: Bulk applicant processing
10. **API Rate Limiting**: Protect against abuse

---

This architecture supports the project's goals of transparency, fairness, and efficiency in recruitment through AI-powered automation and intelligent candidate matching.
