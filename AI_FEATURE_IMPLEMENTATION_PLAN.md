# AI_FEATURE_IMPLEMENTATION_PLAN.md
**Project:** SmartRecruiter – AI-Enhanced Application Tracking System  
**Author:** Bora Vinca  
**Date:** [Insert Date]  
**Advisor:** [Insert Name]  

---

## 🧠 Overview

This document outlines the detailed plan for implementing **two high-impact AI modules** that will strengthen *SmartRecruiter* both technically and academically:

1. **Adaptive AI Scoring System** – enables the ATS to learn from recruiter behavior and adjust weights dynamically.  
2. **AI Fairness Auditor & Heatmap Visualization** – quantifies and visualizes potential bias in candidate scoring.  

These additions are designed to enhance the system’s intelligence, transparency, and ethical integrity, key pillars of an AI-driven recruitment platform.

---

## ⚙️ 1. Adaptive AI Scoring System

### 🎯 Objective
Create a self-learning scoring model that dynamically adapts its weight distribution based on recruiter hiring behavior and system feedback.  
This feature transforms SmartRecruiter from a static rule-based scorer into a **learning AI system**.

---

### 🧩 a. Conceptual Design

#### Inputs
- `job_description`  
- `resume_text`  
- `skills_extracted`, `experience_years`, `education_level`  
- `recruiter_feedback` or `hire_decision` (binary)

#### Outputs
- Updated model weights for:
  - `skill_weight`
  - `experience_weight`
  - `education_weight`
  - `semantic_similarity_weight`

#### Learning Process
1. Start with base weights (defined in `scoring_service.py`).
2. After each hiring cycle:
   - Compare recruiter’s final decision vs. AI ranking.
   - Adjust weights using a **gradient-based update** (simple linear regression or reinforcement-like rule).
3. Store updated weights in the database for future scoring.

---

### 🧩 b. Architecture Integration

**Files to Modify / Create:**
backend/
├── app/
│ ├── services/
│ │ ├── scoring_service.py ← Extend with adaptive model
│ │ └── learning_service.py ← New: manages feedback loop
│ ├── models/
│ │ └── scoring_weights.py ← New SQLAlchemy model for storing weights
│ ├── routers/
│ │ └── feedback_router.py ← New: recruiter feedback API endpoint

yaml
Copy code

---

### 💻 c. Implementation Steps

#### Step 1 – Extend `scoring_service.py`
Add base scoring weight configuration:
```python
DEFAULT_WEIGHTS = {
    "skills": 0.4,
    "experience": 0.3,
    "education": 0.1,
    "semantic_similarity": 0.2
}
Use these in the scoring function:

python
Copy code
def calculate_dynamic_score(resume, job, weights=None):
    w = weights or DEFAULT_WEIGHTS
    return (
        w["skills"] * skill_score(resume, job)
        + w["experience"] * experience_score(resume)
        + w["education"] * education_score(resume)
        + w["semantic_similarity"] * similarity_score(resume, job)
    )
Step 2 – Create learning_service.py
Implements adaptive weight tuning:

python
Copy code
class AdaptiveWeightLearner:
    def __init__(self, db_session):
        self.db = db_session

    def update_weights(self, feedback_data):
        """
        feedback_data = [{'ai_score': 78, 'hired': 1}, ...]
        """
        import numpy as np
        from sklearn.linear_model import LinearRegression

        X = np.array([d['ai_score'] for d in feedback_data]).reshape(-1, 1)
        y = np.array([d['hired'] for d in feedback_data])
        model = LinearRegression().fit(X, y)
        new_skill_weight = model.coef_[0]
        self.db.save_weights({"skills": new_skill_weight})
Step 3 – Feedback API
Allow recruiters to submit outcomes:

python
Copy code
@router.post("/feedback/")
def submit_feedback(feedback: FeedbackModel):
    learner = AdaptiveWeightLearner(db)
    learner.update_weights(feedback.data)
    return {"message": "Model weights updated successfully"}
🧮 d. Evaluation Plan
Metric	Description	Target
Model Stability	Weight convergence across 10 iterations	±5% change
Accuracy Improvement	Increase in recruiter-AI alignment	+10%
Response Time	Real-time update under 1s	✅ Maintain responsiveness

⚖️ 2. AI Fairness Auditor & Heatmap Visualization
🎯 Objective
Quantitatively assess the fairness of AI scoring decisions and visualize disparities across demographic or experience groups.

🧩 a. Conceptual Design
Inputs
Candidate metadata (age, gender, education)

Candidate scores (AI-generated)

Job position details

Outputs
Bias metrics (Mean Score Difference, Disparate Impact Ratio)

Heatmap visualization of score distribution

🧩 b. Architecture Integration
Files to Modify / Create:

sql
Copy code
ai/
 ├── evaluation/
 │   ├── fairness_checker.py     ← New: compute fairness metrics
 │   └── bias_visualizer.py      ← New: generates heatmap
frontend/
 ├── src/components/
 │   └── FairnessDashboard.jsx   ← New React component for visualization
💻 c. Implementation Steps
Step 1 – Create fairness_checker.py
python
Copy code
import pandas as pd

class FairnessChecker:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def mean_score_difference(self, group_col: str, score_col: str):
        group_means = self.data.groupby(group_col)[score_col].mean()
        return group_means.max() - group_means.min()

    def disparate_impact_ratio(self, group_col: str, threshold: float = 70):
        rates = self.data.groupby(group_col)['score'].apply(lambda x: (x >= threshold).mean())
        return rates.min() / rates.max()
Step 2 – Create bias_visualizer.py
python
Copy code
import seaborn as sns
import matplotlib.pyplot as plt

def plot_bias_heatmap(df, group_col, score_col):
    pivot = df.pivot_table(values=score_col, index=group_col, aggfunc='mean')
    sns.heatmap(pivot, annot=True, cmap='coolwarm')
    plt.title('AI Fairness Heatmap by Group')
    plt.savefig('ai/reports/fairness_heatmap.png')
Step 3 – Frontend Integration
Create FairnessDashboard.jsx:

jsx
Copy code
import React, { useEffect, useState } from "react";
import axios from "axios";

export default function FairnessDashboard() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("/api/fairness/metrics").then(res => setData(res.data));
  }, []);

  return (
    <div>
      <h2>AI Fairness Audit</h2>
      <p>Disparate Impact Ratio: {data.dir}</p>
      <img src="/fairness_heatmap.png" alt="Fairness Heatmap" />
    </div>
  );
}
📊 d. Evaluation Plan
Metric	Description	Target
Mean Score Difference (MSD)	Avg score gap between groups	< 10 points
Disparate Impact Ratio (DIR)	Ratio of pass rates	0.8 ≤ DIR ≤ 1.2
Heatmap Clarity	Visual interpretability	Clear labeling & color balance

🧩 3. Integration Testing Plan
Test	Description	Expected Result
test_adaptive_learning.py	Simulate recruiter feedback and weight updates	Updated weights saved correctly
test_fairness_metrics.py	Evaluate fairness calculations on mock dataset	Metrics computed accurately
test_visualization.py	Ensure fairness heatmap generated and displayed	File created & accessible from dashboard
test_end_to_end.py	Run full ATS workflow with updated AI layer	Consistent scoring, fairness reporting

🧠 Academic Justification
Feature	Academic Contribution
Adaptive Scoring System	Demonstrates learning-based personalization and dynamic AI reasoning — beyond traditional ATS filtering.
Fairness Auditor & Visualization	Adds quantitative bias detection and interpretability — aligns with explainable and ethical AI standards.
Combined System	Represents an AI ecosystem that learns, audits itself, and explains its behavior — a novel approach for HR tech.

🏁 Deliverables
learning_service.py – adaptive scoring module

fairness_checker.py and bias_visualizer.py – fairness analysis modules

Updated scoring_service.py – integrated weight handling

FairnessDashboard.jsx – frontend visualization

Evaluation dataset & test reports

Updated documentation in /docs/AI_FEATURE_IMPLEMENTATION_PLAN.md

✅ Expected Outcome
By implementing these features, SmartRecruiter evolves from a static AI-enabled ATS into a self-improving, fair, and explainable recruitment intelligence system.
This elevates its academic credibility and ensures strong marks in innovation, evaluation, and ethics — the key pillars of a top-tier dissertation.

“A transparent, adaptive, and fair AI recruitment system that learns from decisions and explains its reasoning — bridging automation and accountability.”

Prepared by:
👤 Bora Vinca
📅 [Insert Date]
🎓 SmartRecruiter: AI-Enhanced Applicant Tracking System

yaml
Copy code

---
