# Adaptive Learning Implementation

## Purpose

The Adaptive Learning Scoring System enables SmartRecruiter to learn dynamically from recruiter feedback, adjusting how candidate scores are calculated based on acceptance/rejection decisions. This creates a self-improving AI scoring model that demonstrates continuous learning capabilities.

## Technical Implementation Details

### Architecture

The adaptive learning system consists of three main components:

1. **Database Model** (`ScoringWeights`)
   - Stores adaptive weights per recruiter/job
   - Tracks iteration count and update history
   - Supports global, recruiter-specific, and job-specific weights

2. **Learning Service** (`AdaptiveWeightLearner`)
   - Implements ML-based weight adjustment using LinearRegression
   - Falls back to rule-based updates if ML libraries unavailable
   - Collects feedback data from hiring decisions

3. **Scoring Service Integration**
   - Automatically uses adaptive weights when available
   - Falls back to default weights if no adaptive weights exist
   - Supports personalized scoring per recruiter

### Implementation Files

- `backend/app/models.py` - `ScoringWeights` model
- `backend/app/services/learning_service.py` - Core learning logic
- `backend/app/services/scoring_service.py` - Integration with scoring
- `backend/app/routers/feedback.py` - API endpoints for feedback

### Learning Algorithm

The system uses a simple linear regression model to adjust weights:

```python
# Train model on feedback data
X = [ai_scores]
y = [hiring_decisions]
model = LinearRegression().fit(X, y)

# Adjust weights based on model coefficient
adjustment = model.coef_[0] * learning_rate
new_weight = current_weight + adjustment
```

### Weight Update Process

1. Recruiter makes hiring decision (Hired/Rejected)
2. System records: AI score, decision, component scores
3. After 2+ decisions, system updates weights
4. Future scoring uses updated weights
5. Weights are personalized per recruiter

## Evaluation Method

### Metrics

- **Weight Convergence**: Track weight changes across iterations
- **Accuracy Improvement**: Measure recruiter-AI alignment over time
- **Response Time**: Ensure real-time updates (< 1s)

### Target Performance

- Model Stability: Weight convergence within ±5% across 10 iterations
- Accuracy Improvement: +10% increase in recruiter-AI alignment
- Response Time: Real-time update under 1s

## Results Interpretation

The adaptive learning system improves scoring accuracy by:

1. **Personalization**: Each recruiter's preferences are learned
2. **Context Awareness**: Job-specific weights for specialized roles
3. **Continuous Improvement**: System gets better with more feedback
4. **Transparency**: All weight changes are logged and trackable

## Usage

### For Recruiters

1. Make hiring decisions (Hired/Rejected) on candidates
2. System automatically learns from decisions
3. View current weights: `GET /feedback/weights`
4. Submit manual feedback: `POST /feedback/submit`

### For Developers

```python
from app.services.learning_service import AdaptiveWeightLearner

learner = AdaptiveWeightLearner(db)
weights = learner.get_weights(recruiter_id=1, job_id=5)
updated = learner.update_weights(
    feedback_data=[{'ai_score': 78, 'hired': 1}, ...],
    recruiter_id=1,
    job_id=5
)
```

## Academic Contribution

This implementation demonstrates:

- **Continuous Learning**: AI system that improves over time
- **Personalization**: Adaptive to individual recruiter preferences
- **Explainability**: Transparent weight adjustment process
- **Ethical AI**: Fairness considerations in weight distribution

