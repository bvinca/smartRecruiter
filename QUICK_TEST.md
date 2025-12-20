# Quick Test Guide - 5 Minute Test

## Fastest Way to Test SmartRecruiter

### Step 1: Start the Application (1 min)
```bash
npm run dev
```
Wait for both frontend (http://localhost:3000) and backend (http://localhost:8000) to start.

### Step 2: Create Test Accounts (1 min)

**Option A: Use Frontend**
1. Go to http://localhost:3000/register
2. Register as Recruiter: `recruiter@test.com` / `test123`
3. Register as Applicant: `applicant@test.com` / `test123`

**Option B: Use API**
```bash
# Register Recruiter
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"recruiter@test.com","password":"test123","role":"recruiter","company_name":"Test Corp","first_name":"Jane","last_name":"Smith"}'

# Register Applicant
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"applicant@test.com","password":"test123","role":"applicant","first_name":"John","last_name":"Doe"}'
```

### Step 3: Create a Job (30 sec)

1. Login as recruiter at http://localhost:3000/login
2. Go to Jobs page
3. Click "Create Job"
4. Fill in:
   - Title: `Python Developer`
   - Description: `Looking for Python developer with FastAPI experience`
   - Requirements: `Python, FastAPI, PostgreSQL`
   - Location: `Remote`
5. Click "Create"

### Step 4: Apply with Resume (2 min)

1. Logout and login as applicant
2. Go to Jobs page
3. Click on the job you created
4. Create a test resume file `test.txt`:
   ```
   John Doe
   Python Developer
   Email: john@test.com
   
   Experience: 5 years Python development
   Skills: Python, FastAPI, PostgreSQL, Docker
   ```
5. Upload the file and click "Submit Application"
6. ✅ You should see:
   - Parsed resume data
   - Match score
   - AI summary (if OpenAI configured)
   - Interview questions

### Step 5: View as Recruiter (30 sec)

1. Logout and login as recruiter
2. Go to Applicants page
3. ✅ You should see:
   - Applicant with parsed data
   - Scores
   - AI summary
   - Interview questions
4. Click "Show Ranking" (if filtered by job)
5. ✅ Candidates should be ranked by match score

## ✅ Success Criteria

If you see:
- ✅ Parsed resume data (name, email, skills)
- ✅ Match score (0-100)
- ✅ AI summary (or fallback message)
- ✅ Interview questions (or fallback)
- ✅ Ranked candidates list

**Then everything is working!** 🎉

## 🐛 If Something Doesn't Work

1. **Check backend logs** - Look for errors in terminal
2. **Check browser console** - F12 → Console tab
3. **Check API docs** - http://localhost:8000/docs
4. **Verify .env file** - Should have `OPENAI_API_KEY` (optional)

## 📝 Test Resume Template

Save as `test_resume.txt`:
```
Your Name
Your Title
Email: your@email.com
Phone: +1-555-123-4567

EXPERIENCE
Your Job Title at Company (2020 - Present)
- Description of work
- Technologies used

SKILLS
Python, FastAPI, PostgreSQL, Docker, Git
```

---

**Total Time: ~5 minutes**

For detailed testing, see `TESTING_GUIDE.md`

