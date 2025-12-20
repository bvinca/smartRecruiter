# SmartRecruiter 🚀

An intelligent Applicant Tracking System (ATS) that leverages AI, NLP, and Retrieval-Augmented Generation (RAG) to automate resume analysis, candidate scoring, and recruiter communication.

## ✨ Features

- **AI-Powered Resume Parsing**: Automatically extract skills, experience, education, and contact information from resumes
- **Semantic Matching**: Use embeddings to calculate semantic similarity between candidates and job descriptions
- **Intelligent Scoring**: Multi-dimensional scoring system (match, skills, experience, education)
- **RAG-Powered Insights**: AI-generated summaries, feedback, and interview questions
- **Modern Dashboard**: Beautiful, responsive UI for recruiters and applicants
- **Analytics**: Comprehensive analytics dashboard with visualizations
- **Fairness & Transparency**: Explainable AI with detailed scoring breakdowns

## 🏗️ Architecture

```
SmartRecruiter/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── routers/  # API endpoints
│   │   ├── services/ # Business logic (parsing, scoring, RAG)
│   │   ├── models.py # Database models
│   │   └── schemas.py # Pydantic schemas
│   └── main.py       # FastAPI application
├── frontend/         # React frontend
│   └── src/
│       ├── pages/    # Page components
│       ├── components/ # Reusable components
│       └── api/      # API client
└── docker-compose.yml # Docker orchestration
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- PostgreSQL 15+ (or use Docker)
- OpenAI API key (for RAG features)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smartRecruiter
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your OPENAI_API_KEY
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Make sure PostgreSQL is running
   # Update DATABASE_URL in .env
   # Tables will be created automatically on first run
   ```

6. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `GET /jobs` - List all jobs
- `POST /jobs` - Create a new job
- `GET /applicants` - List all applicants
- `POST /applicants/upload` - Upload and parse a CV
- `POST /applicants/{id}/score` - Calculate scores for an applicant
- `POST /applicants/{id}/summary` - Generate AI summary and feedback

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React 18 | Modern, responsive UI |
| Backend | FastAPI | High-performance API |
| Database | PostgreSQL | Relational data storage |
| Vector Store | ChromaDB | Semantic embeddings storage |
| AI/NLP | LangChain, OpenAI, Sentence Transformers | Resume parsing, embeddings, RAG |
| Deployment | Docker, Docker Compose | Containerized deployment |

## 📊 Evaluation Metrics

- **Accuracy**: Resume-job match precision ≥ 85%
- **Fairness**: Reduced bias in scoring ≥ 30%
- **Efficiency**: Processing time per CV < 2s
- **Usability**: Recruiter satisfaction ≥ 8/10
- **Transparency**: AI explanation clarity ≥ 90%

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/smartrecruiter
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
DEBUG=True
CHROMA_PERSIST_DIR=./chroma_db
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env)**
```env
REACT_APP_API_URL=http://localhost:8000
```

## 📖 Usage Guide

1. **Create a Job Posting**
   - Navigate to Jobs page
   - Click "Create Job"
   - Fill in job details and requirements

2. **Upload a CV**
   - Go to Applicants page
   - Click "Upload CV"
   - Select job and upload resume file (PDF, DOC, DOCX, TXT)

3. **Score Candidates**
   - View applicant list
   - Click "Calculate Score" for each applicant
   - Review match scores and breakdowns

4. **Generate AI Insights**
   - Click "Generate AI Summary" on an applicant
   - Review AI-generated summary, feedback, and interview questions

5. **View Analytics**
   - Navigate to Analytics dashboard
   - View statistics and visualizations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is part of an academic dissertation. Please refer to the project plan for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- LangChain for RAG capabilities
- OpenAI for language models
- React team for the frontend framework

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for fair and transparent recruitment**
