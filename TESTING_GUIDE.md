# SmartRecruiter Testing Guide

## 🧪 Complete Testing Guide for All Functionality

This guide covers how to test all features of SmartRecruiter, including AI functionality, resume parsing, scoring, and evaluation.

---

## Prerequisites

1. **Backend Running**: `npm run dev` or `cd backend && uvicorn main:app --reload`
2. **Frontend Running**: Should start automatically with `npm run dev`
3. **Database**: PostgreSQL or SQLite configured
4. **OpenAI API Key**: Set in `.env` file (optional, but needed for AI features)

---

## 1. Authentication Testing

### 1.1 Register as Applicant

**Frontend:**
1. Navigate to `http://localhost:3000/register`
2. Fill in:
   - Email: `applicant@test.com`
   - Password: `testpass123`
   - Role: Select "Applicant"
   - First Name: `John`
   - Last Name: `Doe`
3. Click "Register"
4. ✅ Should redirect to Applicant Dashboard

**API (Alternative):**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "applicant@test.com",
    "password": "testpass123",
    "role": "applicant",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 1.2 Register as Recruiter

**Frontend:**
1. Navigate to `http://localhost:3000/register`
2. Fill in:
   - Email: `recruiter@test.com`
   - Password: `testpass123`
   - Role: Select "Recruiter"
   - Company Name: `Tech Corp`
   - First Name: `Jane`
   - Last Name: `Smith`
3. Click "Register"
4. ✅ Should redirect to Recruiter Dashboard

**API:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "recruiter@test.com",
    "password": "testpass123",
    "role": "recruiter",
    "first_name": "Jane",
    "last_name": "Smith",
    "company_name": "Tech Corp"
  }'
```

### 1.3 Login

**Frontend:**
1. Navigate to `http://localhost:3000/login`
2. Enter credentials
3. Click "Login"
4. ✅ Should redirect to appropriate dashboard

**API:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=applicant@test.com&password=testpass123"
```

### 1.4 Get Current User

**API:**
```bash
# Get token from login response, then:
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 2. Job Management Testing (Recruiter)

### 2.1 Create a Job

**Frontend:**
1. Login as recruiter
2. Navigate to Jobs page
3. Click "Create Job"
4. Fill in:
   - Title: `Senior Python Developer`
   - Description: `We are looking for an experienced Python developer with FastAPI experience. Must have 5+ years of experience.`
   - Requirements: `Python, FastAPI, PostgreSQL, Docker, REST APIs`
   - Location: `Remote`
   - Salary Range: `$100k - $150k`
5. Click "Create"
6. ✅ Job should appear in jobs list

**API:**
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer RECRUITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer with FastAPI experience.",
    "requirements": "Python, FastAPI, PostgreSQL, Docker, REST APIs",
    "location": "Remote",
    "salary_range": "$100k - $150k"
  }'
```

### 2.2 List Jobs

**Frontend:**
- Navigate to Jobs page
- ✅ Should see all jobs (recruiters see their jobs, applicants see active jobs)

**API:**
```bash
curl -X GET http://localhost:8000/jobs \
  -H "Authorization: Bearer TOKEN"
```

### 2.3 Get Job Details

**API:**
```bash
curl -X GET http://localhost:8000/jobs/1 \
  -H "Authorization: Bearer TOKEN"
```

---

## 3. Resume Parsing Testing

### 3.1 Create a Test Resume File

Create a file `test_resume.txt`:
```
John Doe
Backend Developer
Email: john.doe@example.com
Phone: +1-555-123-4567

EXPERIENCE
Senior Backend Developer at Tech Corp (2020 - Present)
- Built REST APIs with FastAPI
- Worked with PostgreSQL and Docker
- Implemented CI/CD pipelines

Backend Developer at Startup Inc (2018 - 2020)
- Developed Python applications
- Used Django and Flask

EDUCATION
Bachelor of Science in Computer Science
University of Technology, 2018

SKILLS
Python, FastAPI, PostgreSQL, Docker, REST APIs, Git, Linux, AWS
```

### 3.2 Upload Resume via Application

**Frontend:**
1. Login as applicant
2. Navigate to Jobs
3. Click on a job
4. Click "Upload Resume" and select your test resume file
5. Click "Submit Application"
6. ✅ Should see success screen with:
   - Parsed resume data (name, email, skills)
   - Match score
   - AI summary (if OpenAI configured)
   - Interview questions (if OpenAI configured)

**API:**
```bash
curl -X POST http://localhost:8000/applications/apply/1 \
  -H "Authorization: Bearer APPLICANT_TOKEN" \
  -F "file=@test_resume.txt"
```

### 3.3 Test Resume Parsing Directly

**API:**
```bash
curl -X POST http://localhost:8000/resume/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@test_resume.txt"
```

**Expected Response:**
```json
{
  "message": "Resume uploaded and parsed successfully",
  "parsed_resume": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-123-4567",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "experience_years": 6.0,
    "education": [...],
    "work_experience": [...]
  }
}
```

### 3.4 Test PDF Resume

1. Create or download a PDF resume
2. Upload via frontend or API
3. ✅ Should parse correctly

### 3.5 Test DOCX Resume

1. Create a Word document resume
2. Upload via frontend or API
3. ✅ Should parse correctly

---

## 4. AI Features Testing

### 4.1 Test AI Summary Generation

**API:**
```bash
curl -X POST http://localhost:8000/resume/analyze \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "John Doe is a backend developer with 5 years of experience in Python and FastAPI...",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "experience_years": 5.0,
    "job_description": "We are looking for a Python developer..."
  }'
```

**Expected Response:**
```json
{
  "summary": "John is an experienced backend developer...",
  "interview_questions": [
    "Describe your experience with FastAPI...",
    "How do you handle database migrations...",
    ...
  ]
}
```

### 4.2 Test Interview Question Generation

The questions are automatically generated when applying. Check:
1. Application success screen
2. Applicant detail view (recruiter)
3. ✅ Should see 5 relevant questions

### 4.3 Test Without OpenAI (Fallback)

1. Remove or invalidate `OPENAI_API_KEY` in `.env`
2. Upload resume
3. ✅ Should still parse resume (text extraction, skills)
4. ⚠️ AI summary and questions will show fallback messages

---

## 5. Scoring System Testing

### 5.1 Automatic Scoring on Application

When an applicant applies with a resume:
1. Scores are automatically calculated
2. Check application response or applicant record
3. ✅ Should see:
   - `match_score`: 0-100
   - `skill_score`: 0-100
   - `experience_score`: 0-100
   - `education_score`: 0-100
   - `overall_score`: 0-100

### 5.2 Manual Score Calculation

**API (Recruiter):**
```bash
curl -X POST http://localhost:8000/applicants/1/score \
  -H "Authorization: Bearer RECRUITER_TOKEN"
```

**Expected Response:**
```json
{
  "applicant_id": 1,
  "job_id": 1,
  "match_score": 85.5,
  "skill_score": 90.0,
  "experience_score": 80.0,
  "education_score": 75.0,
  "overall_score": 84.5,
  "explanation": "Strong match with required skills..."
}
```

### 5.3 Verify Score Calculation

**Test Case 1: Perfect Match**
- Resume: Python, FastAPI, PostgreSQL
- Job: Requires Python, FastAPI, PostgreSQL
- ✅ `skill_score` should be high (80-100)

**Test Case 2: Partial Match**
- Resume: Python, Django
- Job: Requires Python, FastAPI
- ✅ `skill_score` should be moderate (40-60)

**Test Case 3: Experience Match**
- Resume: 5 years experience
- Job: Requires 3+ years
- ✅ `experience_score` should be high

---

## 6. Candidate Ranking Testing

### 6.1 Create Multiple Applications

1. Create 3-5 test resumes with different skill sets
2. Apply all to the same job
3. ✅ All should be parsed and scored

### 6.2 Get Ranked Candidates

**Frontend:**
1. Login as recruiter
2. Navigate to Applicants page
3. Filter by job
4. Click "Show Ranking"
5. ✅ Should see candidates ranked by match score

**API:**
```bash
curl -X GET http://localhost:8000/ranking/job/1 \
  -H "Authorization: Bearer RECRUITER_TOKEN"
```

**Expected Response:**
```json
[
  {
    "rank": 1,
    "applicant_id": 3,
    "name": "John Doe",
    "email": "john@example.com",
    "match_score": 92.5,
    "overall_score": 88.0,
    "skills": ["Python", "FastAPI"],
    "experience_years": 5.0
  },
  {
    "rank": 2,
    "applicant_id": 1,
    "name": "Jane Smith",
    "match_score": 85.0,
    ...
  }
]
```

### 6.3 Verify Ranking Order

1. Check that candidates are sorted by `match_score` descending
2. ✅ Highest score should be rank 1
3. ✅ Lower scores should have higher rank numbers

---

## 7. Analytics Testing (Recruiter)

### 7.1 View Analytics Dashboard

**Frontend:**
1. Login as recruiter
2. Navigate to Analytics page
3. ✅ Should see:
   - Total jobs
   - Active jobs
   - Total applications
   - Applications by status (pending, shortlisted, etc.)
   - Average scores
   - Top skills
   - Applications by job (chart)

**API:**
```bash
curl -X GET http://localhost:8000/analytics \
  -H "Authorization: Bearer RECRUITER_TOKEN"
```

**Expected Response:**
```json
{
  "total_jobs": 5,
  "active_jobs": 3,
  "total_applications": 15,
  "pending_applications": 8,
  "shortlisted_applications": 4,
  "rejected_applications": 2,
  "hired_applications": 1,
  "average_score": 75.5,
  "top_skills": [
    {"skill": "Python", "count": 12},
    {"skill": "FastAPI", "count": 10}
  ],
  "applications_by_job": [...]
}
```

---

## 8. Interview Scheduling Testing

### 8.1 Schedule Interview

**Frontend:**
1. Login as recruiter
2. Navigate to Interviews or Applicants
3. Select an application
4. Click "Schedule Interview"
5. Fill in:
   - Date and time
   - Location or meeting link
   - Notes
6. Click "Schedule"
7. ✅ Interview should be created

**API:**
```bash
curl -X POST http://localhost:8000/interviews \
  -H "Authorization: Bearer RECRUITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": 1,
    "scheduled_at": "2025-12-20T10:00:00Z",
    "location": "Conference Room A",
    "meeting_link": "https://meet.google.com/abc-defg-hij",
    "notes": "Technical interview focusing on Python and FastAPI"
  }'
```

### 8.2 View Interviews

**Frontend:**
- Navigate to Interviews page
- ✅ Should see all scheduled interviews

**API:**
```bash
curl -X GET http://localhost:8000/interviews \
  -H "Authorization: Bearer TOKEN"
```

---

## 9. Profile Management Testing

### 9.1 View Profile

**Frontend:**
1. Login
2. Navigate to Profile
3. ✅ Should see user information

**API:**
```bash
curl -X GET http://localhost:8000/profile \
  -H "Authorization: Bearer TOKEN"
```

### 9.2 Update Profile

**Frontend:**
1. Navigate to Profile
2. Update first name, last name
3. Click "Update"
4. ✅ Changes should be saved

**API:**
```bash
curl -X PUT http://localhost:8000/profile \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John Updated",
    "last_name": "Doe Updated"
  }'
```

### 9.3 Upload Resume to Profile (Applicant)

**Frontend:**
1. Login as applicant
2. Navigate to Profile
3. Upload resume file
4. ✅ Resume should be parsed and stored

**API:**
```bash
curl -X POST http://localhost:8000/profile/resume \
  -H "Authorization: Bearer APPLICANT_TOKEN" \
  -F "file=@test_resume.txt"
```

---

## 10. Complete Workflow Testing

### 10.1 End-to-End Applicant Flow

1. ✅ Register as applicant
2. ✅ Browse jobs
3. ✅ View job details
4. ✅ Upload resume and apply
5. ✅ See parsed resume data and match score
6. ✅ View application status
7. ✅ Update profile

### 10.2 End-to-End Recruiter Flow

1. ✅ Register as recruiter
2. ✅ Create job posting
3. ✅ View applicants (after applications submitted)
4. ✅ View parsed resume data
5. ✅ See AI summary and interview questions
6. ✅ View candidate scores
7. ✅ Rank candidates
8. ✅ Schedule interview
9. ✅ Update application status
10. ✅ View analytics

---

## 11. Error Handling Testing

### 11.1 Test Invalid Credentials

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=wrong@email.com&password=wrongpass"
```
✅ Should return 401 Unauthorized

### 11.2 Test Unauthorized Access

```bash
# Try to access recruiter endpoint as applicant
curl -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer APPLICANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test"}'
```
✅ Should return 403 Forbidden

### 11.3 Test Invalid File Upload

```bash
# Upload non-resume file
curl -X POST http://localhost:8000/applications/apply/1 \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@image.jpg"
```
✅ Should return 400 Bad Request

### 11.4 Test Missing Required Fields

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer RECRUITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test"}'
```
✅ Should return 422 Validation Error

---

## 12. Performance Testing

### 12.1 Test Resume Parsing Speed

1. Upload a large resume (10+ pages)
2. Measure time to parse
3. ✅ Should complete in < 5 seconds

### 12.2 Test Batch Operations

1. Create 10+ applications
2. Request ranking
3. ✅ Should complete in reasonable time

### 12.3 Test API Response Times

Use browser DevTools Network tab:
- ✅ API calls should complete in < 1 second (except AI calls)
- ✅ AI calls (summaries, questions) may take 2-5 seconds

---

## 13. AI Evaluation Testing

### 13.1 Test AI Summary Quality

1. Upload resume with clear experience
2. Check AI summary
3. ✅ Should be:
   - Concise (2-3 sentences)
   - Relevant to resume content
   - Professional tone

### 13.2 Test Interview Questions Quality

1. Upload resume
2. Check generated questions
3. ✅ Should be:
   - Relevant to candidate's experience
   - Specific and actionable
   - Related to job requirements (if job description provided)

### 13.3 Test Semantic Matching

1. Create job: "Python Developer with FastAPI"
2. Apply with resume: "5 years Python, FastAPI, PostgreSQL"
3. Apply with resume: "Java Developer with Spring Boot"
4. Check ranking
5. ✅ Python/FastAPI candidate should rank higher

### 13.4 Test Score Accuracy

**Test Case:**
- Job requires: Python, FastAPI, 3+ years
- Candidate 1: Python, FastAPI, 5 years → Should score 85-95
- Candidate 2: Python, Django, 2 years → Should score 50-70
- Candidate 3: Java, Spring, 5 years → Should score 20-40

✅ Scores should reflect actual match quality

---

## 14. Database Testing

### 14.1 Verify Data Persistence

1. Create application
2. Restart backend
3. Check database
4. ✅ Data should persist

### 14.2 Verify Relationships

1. Create job
2. Create application
3. Check database
4. ✅ Foreign keys should be correct

---

## 15. Frontend Testing

### 15.1 Test Responsive Design

1. Open in different screen sizes
2. ✅ Layout should adapt

### 15.2 Test Navigation

1. Navigate between pages
2. ✅ Should work smoothly
3. ✅ Protected routes should redirect if not logged in

### 15.3 Test Forms

1. Fill forms
2. Submit
3. ✅ Validation should work
4. ✅ Success/error messages should appear

---

## 16. Quick Test Checklist

### Basic Functionality
- [ ] Register applicant
- [ ] Register recruiter
- [ ] Login
- [ ] Create job (recruiter)
- [ ] Browse jobs (applicant)
- [ ] Upload resume and apply
- [ ] View parsed resume data
- [ ] View scores
- [ ] View AI summary
- [ ] View interview questions
- [ ] Rank candidates (recruiter)
- [ ] Schedule interview (recruiter)
- [ ] View analytics (recruiter)

### AI Features
- [ ] Resume parsing (PDF, DOCX, TXT)
- [ ] Skill extraction
- [ ] AI summary generation
- [ ] Interview question generation
- [ ] Semantic embeddings
- [ ] Candidate ranking

### Error Cases
- [ ] Invalid login
- [ ] Unauthorized access
- [ ] Invalid file upload
- [ ] Missing required fields

---

## 17. Using FastAPI Docs for Testing

The easiest way to test API endpoints:

1. **Start backend**: `cd backend && uvicorn main:app --reload`
2. **Open**: `http://localhost:8000/docs`
3. **Authenticate**:
   - Click "Authorize" button
   - Use `/auth/login` endpoint to get token
   - Paste token in "Authorize" dialog
4. **Test endpoints**: Click "Try it out" on any endpoint

---

## 18. Sample Test Data

### Sample Resume (test_resume.txt)
```
John Doe
Senior Backend Developer
Email: john.doe@example.com
Phone: +1-555-123-4567

PROFESSIONAL EXPERIENCE

Senior Backend Developer
Tech Corp, San Francisco, CA
2020 - Present
- Designed and implemented REST APIs using FastAPI
- Managed PostgreSQL databases and optimized queries
- Deployed applications using Docker and Kubernetes
- Implemented CI/CD pipelines with GitHub Actions

Backend Developer
Startup Inc, Remote
2018 - 2020
- Developed Python applications using Django and Flask
- Worked with MongoDB and Redis
- Collaborated with frontend team on API design

EDUCATION

Bachelor of Science in Computer Science
University of Technology, 2018
GPA: 3.8/4.0

SKILLS
Python, FastAPI, Django, Flask, PostgreSQL, MongoDB, Redis, Docker, Kubernetes, AWS, Git, REST APIs, Microservices
```

### Sample Job Description
```
We are looking for an experienced Python backend developer to join our team.

Requirements:
- 5+ years of Python development experience
- Strong experience with FastAPI or similar frameworks
- PostgreSQL database experience
- Docker and containerization knowledge
- REST API design and implementation
- Git version control

Nice to have:
- Kubernetes experience
- AWS cloud services
- Microservices architecture
```

---

## 19. Troubleshooting

### AI Features Not Working
- Check `OPENAI_API_KEY` in `.env`
- Check API quota/billing
- Check console for error messages

### Resume Not Parsing
- Check file format (PDF, DOCX, TXT)
- Check file size (should be < 10MB)
- Check console for parsing errors

### Scores Not Calculating
- Check if resume was parsed successfully
- Check if job description exists
- Check console for scoring errors

### Ranking Not Working
- Check if embeddings were generated
- Check if multiple applicants exist for job
- Check console for errors

---

## 20. Automated Testing (Future)

For automated testing, consider:
- **pytest** for backend unit tests
- **pytest-asyncio** for async endpoint tests
- **React Testing Library** for frontend tests
- **Playwright** or **Cypress** for E2E tests

---

This guide covers all major functionality. Start with basic authentication, then move through each feature systematically.

