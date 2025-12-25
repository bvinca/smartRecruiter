# Frontend Features Location Guide

This guide shows you exactly where to find all the newly implemented AI features in the frontend.

## 🎯 Quick Navigation

### For Recruiters:
1. **Recruiter Dashboard** (`/recruiter/dashboard`) - Fairness trends
2. **Applicants Page** (`/recruiter/jobs/:id/applicants`) - Fairness audit, candidate recommendations
3. **Applicant Detail Modal** - All AI features (resume analysis, explanations, skill gap, emails)
4. **Job Detail Page** (`/recruiter/jobs/:id`) - Job description enhancement

### For Applicants:
1. **Applicant Dashboard** (`/applicant/dashboard`) - Job recommendations
2. **Job Detail Page** (`/applicant/jobs/:id`) - Job description enhancement
3. **Application Detail** - Score explanations

---

## 📍 Detailed Feature Locations

### 1. **Adaptive Learning Scoring System** 🤖
**Location**: Automatic (works behind the scenes)

**How to see it**:
- Go to **Applicants Page** (`/recruiter/jobs/:id/applicants`)
- Click on any applicant to open **Applicant Detail Modal**
- Change application status to **"Hired"** or **"Rejected"**
- The system automatically learns from your decision
- View current weights: Check backend logs or use API endpoint `/feedback/weights`

**What it does**: Adjusts scoring weights based on your hiring decisions

---

### 2. **AI Email Communication** 📧
**Location**: Applicant Detail Modal (Recruiters only)

**How to access**:
1. Go to **Applicants Page** (`/recruiter/jobs/:id/applicants`)
2. Click on any applicant to open the **Applicant Detail Modal**
3. Scroll down to **"AI Email Communication"** section
4. Select email type:
   - Acknowledgment
   - Interview Invitation
   - Feedback
   - Rejection
5. Click **"Generate Email"**
6. Review the generated email
7. Click **"Send Email"** to send it
8. Click **"View History"** to see past emails

**Features**:
- Generate personalized emails
- Send emails directly from the app
- View email history

---

### 3. **Fairness Audit & Trends** ⚖️
**Location**: Multiple places

#### A. Applicants Page
1. Go to **Applicants Page** (`/recruiter/jobs/:id/applicants`)
2. Click **"Audit Fairness"** button (top of the page, recruiters only)
3. View fairness dashboard with:
   - Bias detection status
   - Mean Score Difference (MSD)
   - Disparate Impact Ratio (DIR)
   - Group analysis
   - Recommendations

#### B. Recruiter Dashboard
1. Go to **Recruiter Dashboard** (`/recruiter/dashboard`)
2. Scroll down to **"Fairness Analytics"** section
3. View fairness trends chart showing bias reduction over time

**Features**:
- Real-time fairness audit
- Historical trends visualization
- Bias reduction tracking

---

### 4. **Explainability (XAI) Reports** 🔍
**Location**: Applicant Detail Modal

**How to access**:
1. Go to **Applicants Page** (`/recruiter/jobs/:id/applicants`)
2. Click on any applicant to open **Applicant Detail Modal**
3. Click **"Explain Scores"** button
4. View detailed explanation:
   - Skills explanation
   - Experience explanation
   - Education explanation
   - Overall summary
   - Strengths and weaknesses

**What it shows**: Why the candidate scored as they did

---

### 5. **Resume Analysis & Feedback** 📄
**Location**: Applicant Detail Modal

**How to access**:
1. Go to **Applicants Page** (`/recruiter/jobs/:id/applicants`)
2. Click on any applicant to open **Applicant Detail Modal**
3. Click **"Analyze Resume"** button
4. View analysis:
   - Summary
   - Strengths
   - Weaknesses
   - Missing skills
   - Keyword suggestions

**What it shows**: AI-powered feedback on the candidate's resume

---

### 6. **Skill Gap Visualization** 📊
**Location**: Applicant Detail Modal

**How to access**:
1. Go to **Applicants Page** (`/recruiter/jobs/:id/applicants`)
2. Click on any applicant to open **Applicant Detail Modal**
3. Make sure the applicant has a job associated (they should have a job_id)
4. Click **"Analyze Skill Gap"** button
5. View visualizations:
   - Bar chart showing skill alignment
   - Radar chart showing categorized skills
   - Overall alignment percentage
   - Matched skills list

**Features**:
- Visual skill comparison
- Multiple chart types (bar/radar)
- Detailed skill breakdown

---

### 7. **Job Description Enhancement** ✨
**Location**: Job Detail Page & Job Modal

#### A. Job Detail Page (Recruiters)
1. Go to **Job Detail Page** (`/recruiter/jobs/:id`)
2. Click **"Enhance with AI"** button (next to description)
3. View enhanced description with:
   - Identified issues
   - Improvements
   - Enhanced text

#### B. Job Modal (When creating/editing jobs)
1. Click **"Create Job"** or edit an existing job
2. In the description field, click **"Enhance with AI"**
3. Review enhancements
4. Click **"Apply"** to use the enhanced description

**What it does**: Improves job descriptions using AI

---

### 8. **Job Recommendations** (For Applicants) 🎯
**Location**: Applicant Dashboard

**How to access**:
1. Log in as an **Applicant**
2. Go to **Applicant Dashboard** (`/applicant/dashboard`)
3. Scroll to **"Recommended Jobs for You"** section
4. View personalized job recommendations based on your resume
5. Click on any recommendation to view job details

**Features**:
- AI-powered job matching
- Similarity scores
- Personalized recommendations

---

### 9. **Candidate Recommendations** (For Recruiters) 👥
**Location**: Job Detail Page (coming soon) or via API

**How to access**:
- Currently available via API endpoint: `/recommendations/candidates/{job_id}`
- Will be integrated into Job Detail page in future updates

**What it does**: Recommends top candidates for a job

---

## 🗺️ Navigation Map

```
Frontend Routes:
├── /recruiter/dashboard
│   └── Fairness Analytics Section (FairnessTrendsWidget)
│
├── /recruiter/jobs/:id
│   └── "Enhance with AI" button
│
├── /recruiter/jobs/:id/applicants
│   ├── "Audit Fairness" button → FairnessDashboard
│   └── Applicant Detail Modal
│       ├── "Analyze Resume" button
│       ├── "Explain Scores" button
│       ├── "Analyze Skill Gap" button
│       └── "AI Email Communication" section
│
└── /applicant/dashboard
    └── "Recommended Jobs for You" section (RecommendationWidget)
```

---

## 🎨 Visual Indicators

Look for these buttons/icons:
- **✨ "Enhance with AI"** - Job description enhancement
- **📄 "Analyze Resume"** - Resume analysis
- **🔍 "Explain Scores"** - XAI explanations
- **📊 "Analyze Skill Gap"** - Skill visualization
- **📧 "AI Email Communication"** - Email generation
- **⚖️ "Audit Fairness"** - Fairness audit
- **🎯 "Recommended Jobs"** - Job recommendations

---

## 🔑 Access Requirements

- **Recruiters** can see:
  - All AI features
  - Fairness audits
  - Email communication
  - Candidate recommendations

- **Applicants** can see:
  - Job recommendations
  - Score explanations (for their own applications)
  - Job description enhancements

---

## 💡 Tips

1. **Fairness Trends**: Need at least 2 fairness audits to see trends
2. **Skill Gap Analysis**: Requires applicant to have a job associated
3. **Email History**: Click "View History" to see all generated emails
4. **Adaptive Learning**: Works automatically when you make hiring decisions

---

## 🐛 Troubleshooting

If you don't see a feature:
1. **Check your role**: Some features are recruiter-only
2. **Check prerequisites**: Some features need data (e.g., applicants, jobs)
3. **Refresh the page**: Sometimes a refresh helps
4. **Check browser console**: Look for error messages (F12)

---

## 📝 Quick Test Checklist

- [ ] Log in as Recruiter
- [ ] Go to Recruiter Dashboard → See Fairness Analytics
- [ ] Go to Applicants Page → Click "Audit Fairness"
- [ ] Open Applicant Detail → See all AI buttons
- [ ] Try "Analyze Resume"
- [ ] Try "Explain Scores"
- [ ] Try "Analyze Skill Gap"
- [ ] Try "AI Email Communication"
- [ ] Log in as Applicant
- [ ] Go to Applicant Dashboard → See Job Recommendations

