# Known Issues and Planned Fixes

## Table of Contents

1. [Critical Issues](#critical-issues)
2. [High Priority Issues](#high-priority-issues)
3. [Medium Priority Issues](#medium-priority-issues)
4. [Low Priority Issues](#low-priority-issues)
5. [Future Enhancements](#future-enhancements)

---

## Critical Issues

### 1. OpenAI API Key Configuration Issues

**Issue:**
- API key works for scoring (embeddings) but was failing for AI summary and question generation
- LangChain's `ChatOpenAI` uses different parameter names (`api_key` vs `openai_api_key`) depending on version
- Inconsistent error handling when API key is missing or invalid

**Impact:**
- AI summary generation fails silently
- Interview question generation fails
- Users see generic error messages

**Root Cause:**
- LangChain version compatibility issues
- Parameter name differences between LangChain versions
- Missing validation before initialization

**Fix Applied:**
- ✅ Updated `ai/rag/generator.py` to try both `api_key` and `openai_api_key` parameters
- ✅ Updated `backend/app/services/rag_service.py` with same compatibility fix
- ✅ Updated `ai/rag/retriever.py` for embeddings compatibility
- ✅ Added API key validation before initialization
- ✅ Improved error messages with specific details

**Status:** ✅ **FIXED**

**Verification:**
- Test summary generation with valid API key
- Test question generation with valid API key
- Test error handling with invalid/missing API key
- Verify both LangChain and direct OpenAI API paths work

---

## High Priority Issues

### 2. spaCy Compatibility with Python 3.14+

**Issue:**
- spaCy 3.7.5 is not compatible with Python 3.14+ due to Pydantic V1 dependency conflicts
- System falls back to regex-based parsing, but this reduces NLP accuracy
- Missing advanced entity recognition capabilities

**Impact:**
- Reduced accuracy in name extraction
- Limited entity recognition (PERSON, ORG, DATE, etc.)
- No advanced NLP features (dependency parsing, named entity recognition)

**Current Workaround:**
- System gracefully falls back to regex-based parsing
- Basic functionality still works
- Error messages indicate fallback is being used

**Planned Fix:**
1. **Option A: Upgrade to spaCy 3.8+** (if available)
   - Check for spaCy updates that support Python 3.14+
   - Update requirements.txt
   - Test compatibility

2. **Option B: Use Alternative NLP Library**
   - Consider NLTK or transformers library
   - Implement entity recognition using HuggingFace models
   - Maintain same API interface

3. **Option C: Downgrade Python Version**
   - Use Python 3.11 or 3.12 for compatibility
   - Update documentation
   - Update Docker images

**Recommended Approach:** Option B - Use HuggingFace transformers for entity recognition
- More modern and actively maintained
- Better Python 3.14+ compatibility
- Can use lightweight models (e.g., `dslim/bert-base-NER`)

**Status:** 🔄 **IN PROGRESS** - Researching alternatives

**Timeline:** 2-3 weeks

---

### 3. Incomplete Evaluation Modules

**Issue:**
- `ai/evaluation/fairness_checker.py` - Only placeholder, no implementation
- `ai/evaluation/performance_eval.py` - Only placeholder, no implementation
- `ai/evaluation/ranking_metrics.py` - Only placeholder, no implementation

**Impact:**
- Cannot measure bias in scoring system
- Cannot evaluate AI model performance
- Cannot calculate ranking quality metrics
- Missing critical evaluation capabilities for dissertation

**Planned Fix:**

#### 3.1 Fairness Checker Implementation

**Features to Implement:**
1. **Demographic Bias Detection**
   - Analyze score distributions by demographic groups (if data available)
   - Statistical tests (t-test, chi-square)
   - Flag potential bias patterns

2. **Score Distribution Analysis**
   - Check for normal distribution
   - Identify outliers
   - Detect skewness

3. **Fairness Metrics**
   - Demographic parity
   - Equalized odds
   - Calibration

**Implementation Plan:**
```python
class FairnessChecker:
    def check_bias(self, scores, candidate_data):
        # 1. Group candidates by demographics (if available)
        # 2. Calculate mean scores per group
        # 3. Statistical significance testing
        # 4. Return bias report
        pass
    
    def calculate_fairness_metrics(self, predictions, ground_truth):
        # Calculate demographic parity, equalized odds, etc.
        pass
```

**Status:** 📋 **PLANNED**

**Timeline:** 4-6 weeks

#### 3.2 Performance Evaluator Implementation

**Features to Implement:**
1. **Classification Metrics**
   - Accuracy, Precision, Recall, F1-Score
   - Confusion matrix
   - ROC-AUC (if applicable)

2. **Regression Metrics** (for scores)
   - MAE, MSE, RMSE
   - R² score
   - Correlation coefficients

3. **Model Comparison**
   - Compare different model configurations
   - A/B testing framework
   - Statistical significance

**Implementation Plan:**
```python
class PerformanceEvaluator:
    def evaluate_model(self, predictions, ground_truth):
        # Calculate accuracy, precision, recall, F1
        # Return comprehensive metrics
        pass
    
    def compare_models(self, model1_results, model2_results):
        # Statistical comparison
        pass
```

**Status:** 📋 **PLANNED**

**Timeline:** 3-4 weeks

#### 3.3 Ranking Metrics Implementation

**Features to Implement:**
1. **NDCG (Normalized Discounted Cumulative Gain)**
   - Measure ranking quality
   - Consider position in ranking
   - Normalize for comparison

2. **Diversity Metrics**
   - Measure diversity in top-k results
   - Prevent over-representation
   - Balance ranking

3. **Ranking Quality Measures**
   - Precision@K
   - Recall@K
   - Mean Reciprocal Rank (MRR)

**Implementation Plan:**
```python
class RankingMetrics:
    def calculate_ndcg(self, ranked_candidates, ground_truth):
        # Calculate NDCG score
        pass
    
    def calculate_diversity(self, ranked_candidates):
        # Measure diversity in ranking
        pass
    
    def precision_at_k(self, ranked_candidates, ground_truth, k):
        # Calculate precision at k
        pass
```

**Status:** 📋 **PLANNED**

**Timeline:** 3-4 weeks

---

### 4. ChromaDB Not Fully Utilized

**Issue:**
- ChromaDB is optional and not fully integrated
- RAG retriever returns empty context if ChromaDB not initialized
- No persistent vector store for historical data
- Embeddings stored in PostgreSQL (less efficient for similarity search)

**Impact:**
- RAG context retrieval doesn't work effectively
- No historical context for better AI responses
- Slower similarity search on large datasets
- Missing RAG benefits

**Planned Fix:**

1. **Initialize ChromaDB on Startup**
   - Create vector store with job descriptions
   - Store historical applicant data
   - Enable semantic search

2. **Populate Vector Store**
   - Index all job descriptions
   - Index successful candidate profiles
   - Update on new data

3. **Improve RAG Retrieval**
   - Use ChromaDB for context retrieval
   - Retrieve top-k similar candidates
   - Retrieve similar job descriptions

4. **Hybrid Storage**
   - Use ChromaDB for similarity search
   - Keep PostgreSQL for structured queries
   - Sync between both systems

**Implementation Steps:**
1. Add ChromaDB initialization in startup
2. Create indexing service for job descriptions
3. Update RAGRetriever to use ChromaDB
4. Add data sync mechanism
5. Add monitoring for vector store health

**Status:** 📋 **PLANNED**

**Timeline:** 2-3 weeks

---

## Medium Priority Issues

### 5. Limited File Format Support

**Issue:**
- Only supports PDF, DOCX, and TXT files
- No support for image-based PDFs (scanned resumes)
- No OCR capabilities
- No support for other formats (ODT, RTF, etc.)

**Impact:**
- Users with scanned resumes cannot use the system
- Limited accessibility
- Missing potential candidates

**Planned Fix:**

1. **Add OCR Support**
   - Integrate Tesseract OCR for scanned PDFs
   - Handle image-based resumes
   - Preprocess images before OCR

2. **Support Additional Formats**
   - ODT (OpenDocument Text)
   - RTF (Rich Text Format)
   - HTML resumes

3. **Improve PDF Handling**
   - Better handling of complex PDF layouts
   - Extract tables and structured data
   - Handle multi-column layouts

**Implementation:**
```python
# Add OCR support
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

def extract_from_scanned_pdf(file_content):
    # Convert PDF to images
    # Run OCR on each page
    # Return extracted text
    pass
```

**Status:** 📋 **PLANNED**

**Timeline:** 3-4 weeks

---

### 6. English-Only Language Support

**Issue:**
- Resume parsing only works for English resumes
- Skill extraction uses English keywords
- No language detection
- No translation capabilities

**Impact:**
- Cannot process resumes in other languages
- Limited international use
- Missing diverse candidate pool

**Planned Fix:**

1. **Language Detection**
   - Use `langdetect` library
   - Detect resume language
   - Route to appropriate parser

2. **Multi-Language Skill Extraction**
   - Expand skill database to multiple languages
   - Use translation for skill matching
   - Language-specific patterns

3. **Translation Support**
   - Translate resumes to English for processing
   - Use Google Translate API or similar
   - Maintain original language data

**Implementation:**
```python
from langdetect import detect

def detect_language(text):
    return detect(text)

def translate_text(text, target_lang='en'):
    # Use translation API
    pass
```

**Status:** 📋 **PLANNED**

**Timeline:** 4-6 weeks

---

### 7. Error Handling and User Feedback

**Issue:**
- Generic error messages for users
- No detailed error logging
- Missing error recovery mechanisms
- No user-friendly error explanations

**Impact:**
- Users don't understand what went wrong
- Difficult to debug issues
- Poor user experience

**Planned Fix:**

1. **Improve Error Messages**
   - Specific error messages for each failure type
   - User-friendly explanations
   - Actionable suggestions

2. **Error Logging**
   - Structured logging (JSON format)
   - Error tracking and monitoring
   - Stack traces for debugging

3. **Error Recovery**
   - Retry mechanisms for transient failures
   - Fallback options
   - Graceful degradation

4. **User Feedback**
   - Toast notifications with clear messages
   - Error codes for support
   - Help documentation links

**Implementation:**
```python
# Structured error responses
{
    "error": {
        "code": "RESUME_PARSE_FAILED",
        "message": "Unable to parse resume. Please ensure the file is not corrupted.",
        "details": "PDF parsing failed: Invalid PDF structure",
        "suggestions": [
            "Try converting to DOCX format",
            "Ensure file is not password protected",
            "Check file size (max 10MB)"
        ]
    }
}
```

**Status:** 📋 **PLANNED**

**Timeline:** 2-3 weeks

---

### 8. Vector Store Placeholder

**Issue:**
- `ai/embeddings/vector_store.py` is just a placeholder
- No actual vector database integration
- Missing FAISS/Pinecone support

**Impact:**
- Cannot use advanced vector search
- Missing scalability for large datasets
- No production-ready vector storage

**Planned Fix:**

1. **Implement Vector Store Interface**
   - Abstract interface for vector operations
   - Support multiple backends (FAISS, Pinecone, ChromaDB)

2. **FAISS Integration**
   - Local vector search
   - Efficient similarity search
   - Index management

3. **Pinecone Integration** (Optional)
   - Cloud-based vector database
   - Scalable solution
   - Managed service

**Status:** 📋 **PLANNED**

**Timeline:** 3-4 weeks

---

## Low Priority Issues

### 9. Limited Analytics Features

**Issue:**
- Basic analytics only
- No predictive analytics
- No trend analysis
- Limited visualizations

**Impact:**
- Recruiters have limited insights
- Cannot predict hiring trends
- Missing advanced reporting

**Planned Fix:**
- Add predictive analytics
- Trend analysis over time
- More chart types
- Export capabilities

**Status:** 📋 **PLANNED**

**Timeline:** 4-6 weeks

---

### 10. No Rate Limiting

**Issue:**
- No API rate limiting
- Vulnerable to abuse
- No quota management
- Could exhaust OpenAI API quota

**Impact:**
- Potential abuse
- High API costs
- Service degradation

**Planned Fix:**
- Implement rate limiting (e.g., slowapi)
- Per-user quotas
- API key management
- Cost monitoring

**Status:** 📋 **PLANNED**

**Timeline:** 2-3 weeks

---

### 11. No Email Notifications

**Issue:**
- No automated emails
- No status update notifications
- No interview reminders
- Manual communication only

**Impact:**
- Poor user experience
- Manual work required
- Missing notifications

**Planned Fix:**
- Email service integration (SendGrid, AWS SES)
- Automated status emails
- Interview reminders
- Application confirmations

**Status:** 📋 **PLANNED**

**Timeline:** 3-4 weeks

---

## Future Enhancements

### 12. Video Resume Support

**Status:** 📋 **PLANNED FOR FUTURE**

**Features:**
- Video upload and processing
- Speech-to-text conversion
- Video summarization
- Facial expression analysis (optional)

---

### 13. Real-Time Features

**Status:** 📋 **PLANNED FOR FUTURE**

**Features:**
- WebSocket support
- Live notifications
- Real-time updates
- Collaborative features

---

### 14. Advanced Search

**Status:** 📋 **PLANNED FOR FUTURE**

**Features:**
- Full-text search
- Semantic search
- Advanced filters
- Saved searches

---

## Summary

### Fixed Issues
- ✅ OpenAI API key configuration for RAGGenerator

### In Progress
- 🔄 spaCy compatibility alternatives

### Planned (High Priority)
- 📋 Evaluation modules implementation
- 📋 ChromaDB integration
- 📋 Error handling improvements

### Planned (Medium Priority)
- 📋 OCR support
- 📋 Multi-language support
- 📋 Vector store implementation

### Planned (Low Priority)
- 📋 Advanced analytics
- 📋 Rate limiting
- 📋 Email notifications

---

## Testing and Verification

For each fix, we will:

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Verify performance improvements
5. **User Acceptance Tests**: Verify user experience improvements

---

**Last Updated:** 2025  
**Document Version:** 1.0

