# Frontend Integration Guide for New AI Features

This guide shows you how to integrate the newly implemented AI features into the frontend UI.

## Available AI Features

1. **AI Job Description Enhancer** - Improves job descriptions by removing bias and optimizing keywords
2. **AI Resume Analyzer** - Provides feedback on candidate resumes
3. **AI Fairness Auditor** - Detects bias in recruitment decisions
4. **XAI Explainer** - Explains why candidates scored as they did
5. **Skill Gap Visualizer** - Shows skill alignment between job requirements and candidate skills

## API Clients Already Created

All API clients are ready in:
- `frontend/src/api/enhancement.js`
- `frontend/src/api/fairness.js`
- `frontend/src/api/explanation.js`
- `frontend/src/api/visualization.js`

## Integration Points

### 1. AI Job Description Enhancer

**Location**: `frontend/src/pages/JobDetail.js` (for recruiters)

**When to show**: When a recruiter is viewing/editing a job posting

**How to add**:

```javascript
import { enhancementApi } from '../api/enhancement';
import { Sparkles } from 'lucide-react';

// Add state
const [enhancedDescription, setEnhancedDescription] = useState(null);
const [isEnhancing, setIsEnhancing] = useState(false);

// Add mutation
const enhanceMutation = useMutation({
  mutationFn: () => enhancementApi.enhanceJobDescription(job.description, job.title),
  onSuccess: (response) => {
    setEnhancedDescription(response.data);
    toast.success('Job description enhanced successfully!');
  },
  onError: (error) => {
    toast.error('Failed to enhance job description');
  }
});

// Add button in the job detail view (for recruiters only)
{user?.role === 'recruiter' && (
  <button 
    className="btn btn-secondary" 
    onClick={() => enhanceMutation.mutate()}
    disabled={isEnhancing}
  >
    <Sparkles size={18} />
    Enhance with AI
  </button>
)}

// Show enhanced description in a modal or expandable section
{enhancedDescription && (
  <div className="enhanced-description">
    <h3>AI-Enhanced Description</h3>
    <p>{enhancedDescription.improved_description}</p>
    {enhancedDescription.identified_issues.length > 0 && (
      <div className="issues">
        <h4>Issues Identified:</h4>
        <ul>
          {enhancedDescription.identified_issues.map((issue, idx) => (
            <li key={idx}>{issue}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)}
```

### 2. AI Resume Analyzer

**Location**: `frontend/src/components/ApplicantDetail.js`

**When to show**: When viewing an applicant's resume (for both recruiters and applicants)

**How to add**:

```javascript
import { enhancementApi } from '../api/enhancement';
import { FileText } from 'lucide-react';

// Add state
const [resumeAnalysis, setResumeAnalysis] = useState(null);
const [isAnalyzing, setIsAnalyzing] = useState(false);

// Add mutation
const analyzeResumeMutation = useMutation({
  mutationFn: () => enhancementApi.analyzeResume(
    localApplicant.resume_text || '',
    localApplicant.job?.description || '',
    localApplicant.job?.requirements || ''
  ),
  onSuccess: (response) => {
    setResumeAnalysis(response.data);
    toast.success('Resume analysis complete!');
  },
  onError: (error) => {
    toast.error('Failed to analyze resume');
  }
});

// Add button in ApplicantDetail component
{localApplicant.resume_text && (
  <button 
    className="btn btn-secondary" 
    onClick={() => analyzeResumeMutation.mutate()}
    disabled={isAnalyzing}
  >
    <FileText size={18} />
    Analyze Resume
  </button>
)}

// Show analysis results
{resumeAnalysis && (
  <div className="resume-analysis">
    <h3>Resume Analysis</h3>
    <p>{resumeAnalysis.summary_feedback}</p>
    
    {resumeAnalysis.missing_skills.length > 0 && (
      <div>
        <h4>Missing Skills:</h4>
        <ul>
          {resumeAnalysis.missing_skills.map((skill, idx) => (
            <li key={idx}>{skill}</li>
          ))}
        </ul>
      </div>
    )}
    
    {resumeAnalysis.strengths.length > 0 && (
      <div>
        <h4>Strengths:</h4>
        <ul>
          {resumeAnalysis.strengths.map((strength, idx) => (
            <li key={idx}>{strength}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)}
```

### 3. XAI Explainer (Explain Scoring)

**Location**: `frontend/src/components/ApplicantDetail.js`

**When to show**: When viewing an applicant's scores

**How to add**:

```javascript
import { explanationApi } from '../api/explanation';
import { HelpCircle } from 'lucide-react';

// Add state
const [explanation, setExplanation] = useState(null);
const [isExplaining, setIsExplaining] = useState(false);

// Add mutation
const explainMutation = useMutation({
  mutationFn: () => explanationApi.explainScoring(
    localApplicant.id,
    localApplicant.job_id
  ),
  onSuccess: (response) => {
    setExplanation(response.data);
    toast.success('Scoring explanation generated!');
  },
  onError: (error) => {
    toast.error('Failed to generate explanation');
  }
});

// Add button near the scores section
{localApplicant.overall_score !== null && (
  <button 
    className="btn btn-secondary" 
    onClick={() => explainMutation.mutate()}
    disabled={isExplaining}
  >
    <HelpCircle size={18} />
    Explain Scores
  </button>
)}

// Show explanation
{explanation && (
  <div className="score-explanation">
    <h3>Score Explanation</h3>
    <div className="explanation-breakdown">
      <div>
        <h4>Skills Score: {explanation.skills_score}%</h4>
        <p>{explanation.skills_explanation}</p>
      </div>
      <div>
        <h4>Experience Score: {explanation.experience_score}%</h4>
        <p>{explanation.experience_explanation}</p>
      </div>
    </div>
    <div className="overall-summary">
      <h4>Overall Summary</h4>
      <p>{explanation.summary}</p>
    </div>
  </div>
)}
```

### 4. Skill Gap Visualizer

**Location**: `frontend/src/components/ApplicantDetail.js`

**When to show**: When viewing an applicant's skills vs job requirements

**How to add**:

```javascript
import { visualizationApi } from '../api/visualization';
import { TrendingUp } from 'lucide-react';

// Add state
const [skillGap, setSkillGap] = useState(null);
const [isAnalyzingGap, setIsAnalyzingGap] = useState(false);

// Add mutation
const analyzeSkillGapMutation = useMutation({
  mutationFn: () => visualizationApi.analyzeSkillGap(
    localApplicant.job_id,
    localApplicant.id
  ),
  onSuccess: (response) => {
    setSkillGap(response.data);
    toast.success('Skill gap analysis complete!');
  },
  onError: (error) => {
    toast.error('Failed to analyze skill gap');
  }
});

// Add button
{localApplicant.job_id && localApplicant.skills && (
  <button 
    className="btn btn-secondary" 
    onClick={() => analyzeSkillGapMutation.mutate()}
    disabled={isAnalyzingGap}
  >
    <TrendingUp size={18} />
    Analyze Skill Gap
  </button>
)}

// Show skill gap visualization
{skillGap && (
  <div className="skill-gap-visualization">
    <h3>Skill Gap Analysis</h3>
    <div className="overall-alignment">
      <p>Overall Alignment: {skillGap.overall_alignment}%</p>
      <p>Matched Skills: {skillGap.matched_skills} / {skillGap.total_job_skills}</p>
    </div>
    
    <div className="skill-matches">
      <h4>Skill Matches:</h4>
      {Object.entries(skillGap.skill_matches).map(([skill, score]) => (
        <div key={skill} className="skill-match-item">
          <span>{skill}</span>
          <div className="skill-bar">
            <div 
              className="skill-fill" 
              style={{ width: `${score}%` }}
            />
            <span>{score}%</span>
          </div>
        </div>
      ))}
    </div>
    
    {skillGap.missing_skills.length > 0 && (
      <div className="missing-skills">
        <h4>Missing Skills:</h4>
        <ul>
          {skillGap.missing_skills.map((skill, idx) => (
            <li key={idx}>{skill}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)}
```

### 5. AI Fairness Auditor

**Location**: `frontend/src/pages/Applicants.js`

**When to show**: When viewing applicants for a job (recruiters only)

**How to add**:

```javascript
import { fairnessApi } from '../api/fairness';
import { Shield } from 'lucide-react';

// Add state
const [fairnessAudit, setFairnessAudit] = useState(null);
const [isAuditing, setIsAuditing] = useState(false);

// Add mutation
const auditFairnessMutation = useMutation({
  mutationFn: () => fairnessApi.auditFairness(jobId),
  onSuccess: (response) => {
    setFairnessAudit(response.data);
    toast.success('Fairness audit complete!');
  },
  onError: (error) => {
    toast.error('Failed to audit fairness');
  }
});

// Add button in the applicants page header (for recruiters)
{user?.role === 'recruiter' && jobId && (
  <button 
    className="btn btn-secondary" 
    onClick={() => auditFairnessMutation.mutate()}
    disabled={isAuditing}
  >
    <Shield size={18} />
    Audit Fairness
  </button>
)}

// Show audit results
{fairnessAudit && (
  <div className="fairness-audit">
    <h3>Fairness Audit Results</h3>
    <div className={`audit-status ${fairnessAudit.bias_detected ? 'bias-detected' : 'no-bias'}`}>
      {fairnessAudit.bias_detected ? (
        <p>⚠️ Potential bias detected</p>
      ) : (
        <p>✅ No significant bias detected</p>
      )}
    </div>
    
    <div className="audit-details">
      <p>Bias Magnitude: {fairnessAudit.bias_magnitude}%</p>
      <p>Statistical Significance: {fairnessAudit.statistical_significance}</p>
    </div>
    
    <div className="group-analysis">
      <h4>Group Analysis:</h4>
      {Object.entries(fairnessAudit.group_analysis).map(([group, data]) => (
        <div key={group}>
          <strong>{group}:</strong> Mean Score: {data.mean_score}% 
          (Count: {data.count})
        </div>
      ))}
    </div>
    
    <div className="recommendations">
      <h4>Recommendations:</h4>
      <ul>
        {fairnessAudit.recommendations.map((rec, idx) => (
          <li key={idx}>{rec}</li>
        ))}
      </ul>
    </div>
  </div>
)}
```

## Quick Start

1. **For Job Description Enhancement**: Add the enhancement button to `JobDetail.js` when `user.role === 'recruiter'`

2. **For Resume Analysis, XAI, and Skill Gap**: Add buttons to `ApplicantDetail.js` component

3. **For Fairness Audit**: Add button to `Applicants.js` page header

4. **Styling**: Add CSS classes for the new components in respective CSS files

## Testing

After adding the features:

1. Start the backend: `npm run backend` or `cd backend && venv\Scripts\python.exe -m uvicorn main:app --reload`
2. Start the frontend: `npm run frontend` or `cd frontend && npm start`
3. Log in as a recruiter to test:
   - Job description enhancement
   - Resume analysis
   - Fairness audit
   - XAI explainer
   - Skill gap visualization
4. Log in as an applicant to test:
   - Resume analysis (on their own profile)
   - XAI explainer (on their own applications)

## Notes

- All API endpoints require authentication
- Some features are recruiter-only (fairness audit, job enhancement)
- Some features are available to both (resume analysis, XAI, skill gap)
- Make sure to handle loading states and errors gracefully
- Use toast notifications for user feedback

