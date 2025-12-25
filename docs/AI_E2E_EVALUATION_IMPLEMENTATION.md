# 🧩 End-to-End (E2E) AI Evaluation System — SmartRecruiter

## 1. Overview
This document outlines the **design, purpose, and implementation steps** of the End-to-End Evaluation (E2E) testing module for the SmartRecruiter system.

While existing tests validate individual AI components (NLP parser, scoring, fairness, explainability), this E2E module tests the **entire intelligent hiring workflow** — from CV parsing and scoring to explanation, fairness validation, and visualization generation.

By automating this process, we can ensure the SmartRecruiter AI system performs **accurately, consistently, and ethically** across different candidate profiles and job descriptions.

---

## 2. Objectives

| Goal | Description |
|------|--------------|
| ✅ **Integration Validation** | Ensure that NLP, scoring, fairness, and explainability modules work together correctly. |
| 🧠 **Performance Assessment** | Measure candidate-job matching accuracy and system efficiency in real-world conditions. |
| ⚖️ **Fairness Evaluation** | Verify that scoring is unbiased across different groups. |
| 🔍 **Explainability Testing** | Ensure AI reasoning and decision justification are generated correctly. |
| 📊 **Visualization Consistency** | Check whether skill-gap and scoring visualizations match calculated metrics. |

---

## 3. Pipeline Flow

The E2E pipeline simulates a **real candidate application** and measures how well the system processes and explains its decision.

CV Upload
│
▼
[1] NLP Resume Parsing (ai/nlp/parser.py)
│
▼
[2] AI Scoring Service (backend/app/services/scoring_service.py)
│
▼
[3] Explainable AI (ai/explanation/xai_explainer.py)
│
▼
[4] Fairness Auditor (ai/evaluation/fairness_checker.py)
│
▼
[5] Visualization Layer (ai/visualization/skill_gap_visualizer.py)
│
▼
JSON Output (score, fairness, explanation, skill gaps)

yaml
Copy code

---

## 4. Test Data Requirements

To run E2E evaluation tests, place data under:

ai/test_data/
│
├── jobs/
│ ├── job_junior_python.txt
│ ├── job_mid_python.txt
│ └── job_senior_python.txt
│
├── resumes/
│ ├── emily_watson_cv.txt
│ ├── oliver_clarke_cv.txt
│ ├── sophia_reed_cv.txt
│ └── lucas_james_cv.txt
│
└── fairness/
└── candidates_bias_test.csv

python
Copy code

Each resume and job file should contain **natural text**, not structured JSON, so the NLP module can process it semantically.

---

## 5. Implementation Plan

### Step 1️⃣ — Create the E2E Test Script

File: `ai/tests/e2e/test_ai_pipeline_e2e.py`

```python
import json
import os
import pytest

from ai.nlp.parser import ResumeParser
from backend.app.services.scoring_service import ScoringService
from ai.explanation.xai_explainer import XAIExplainer
from ai.evaluation.fairness_checker import FairnessChecker
from ai.visualization.skill_gap_visualizer import SkillGapVisualizer

@pytest.mark.parametrize("cv_file, job_file", [
    ("ai/test_data/resumes/emily_watson_cv.txt", "ai/test_data/jobs/job_junior_python.txt"),
    ("ai/test_data/resumes/oliver_clarke_cv.txt", "ai/test_data/jobs/job_mid_python.txt"),
    ("ai/test_data/resumes/sophia_reed_cv.txt", "ai/test_data/jobs/job_senior_python.txt")
])
def test_end_to_end_pipeline(cv_file, job_file):
    # Load test data
    with open(cv_file, encoding="utf-8") as f:
        cv_text = f.read()
    with open(job_file, encoding="utf-8") as f:
        job_text = f.read()

    # Step 1: Parse Resume
    parser = ResumeParser()
    parsed_resume = parser.parse_file(cv_text.encode("utf-8"), "resume.txt", use_ai=False)

    # Step 2: Score Candidate
    scoring_service = ScoringService()
    scores = scoring_service.calculate_scores(
        resume_text=cv_text,
        job_description=job_text,
        applicant_skills=parsed_resume.get("skills", []),
        applicant_experience_years=parsed_resume.get("experience_years", 0),
        applicant_education=parsed_resume.get("education", []),
        applicant_work_experience=parsed_resume.get("work_experience", [])
    )

    # Step 3: Explainable AI
    explainer = XAIExplainer()
    explanation = explainer.generate_explanation(cv_text, job_text, scores)

    # Step 4: Fairness Audit
    fairness_checker = FairnessChecker()
    fairness_result = fairness_checker.evaluate(scores, group="test_group")

    # Step 5: Visualization
    visualizer = SkillGapVisualizer()
    visualization = visualizer.generate_visual(scores, parsed_resume.get("skills", []))

    # Step 6: Export results
    result = {
        "cv_file": os.path.basename(cv_file),
        "job_file": os.path.basename(job_file),
        "scores": scores,
        "explanation": explanation,
        "fairness": fairness_result,
        "visualization": visualization
    }

    output_path = "ai/test_results/e2e_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(result, out, indent=4)

    print(json.dumps(result, indent=4))
    assert 0 <= scores["overall_score"] <= 100