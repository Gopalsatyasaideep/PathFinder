# 🎯 PathFinder AI - Career Guidance Platform
## With NVIDIA-Powered ATS Scoring & Chatbot

A comprehensive career guidance platform that helps job seekers optimize their resumes, find matching jobs, and get AI-powered career advice.

---

## 🚀 New Features (Latest Update)

### ✨ Resume ATS Scoring
- **Upload resume** (PDF/DOCX) → Get instant ATS compatibility score (0-100)
- **Detailed analysis**: Skills match, experience match, education match, formatting
- **Keyword insights**: See matched and missing keywords
- **Actionable recommendations**: Specific tips to improve your ATS score
- **Pass likelihood**: High/Medium/Low assessment

### 🤖 NVIDIA-Powered AI Chatbot
- **Advanced AI**: Uses NVIDIA's Qwen 3 Next 80B model
- **Context-aware**: Provides personalized career guidance based on your resume
- **RAG-based**: Grounded responses using your data
- **Automatic fallback**: Works with multiple AI providers

### 📊 Job Matching with ATS
- **Smart recommendations**: Get jobs that match your skills
- **ATS scoring per job**: See how your resume scores for each position
- **Batch analysis**: Score against multiple jobs at once
- **Prioritized results**: Jobs ranked by match score and ATS compatibility

---

## 📁 Project Structure

```
CURSORFINALYRPROJECT/
├── frontend/                      # React + Vite frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ResumeUpload.jsx  # Resume upload interface
│   │   │   ├── Chatbot.jsx       # AI chatbot interface
│   │   │   └── JobRecommendations.jsx
│   │   └── services/
│   │       └── api.js            # API client
│   └── ...
│
├── backend/                       # FastAPI backend
│   ├── services/
│   │   ├── ats_scorer.py         # ✨ NEW: ATS scoring service
│   │   ├── nvidia_client.py      # ✨ Enhanced: NVIDIA API
│   │   ├── rag_chatbot.py        # ✨ Enhanced: NVIDIA support
│   │   ├── resume_parser.py      # Resume PDF/DOCX extraction
│   │   ├── orchestrator.py       # ✨ Enhanced: ATS integration
│   │   └── ...
│   │
│   ├── routers/
│   │   ├── resume.py             # ✨ Enhanced: ATS endpoints
│   │   ├── chat.py               # Chatbot endpoint
│   │   └── ...
│   │
│   ├── NVIDIA_ATS_CHATBOT_GUIDE.md     # ✨ Comprehensive guide
│   ├── QUICKSTART_ATS_NVIDIA.md        # ✨ Quick start guide
│   ├── test_nvidia_integration.py      # ✨ Integration tests
│   └── requirements.txt                # Updated dependencies
│
└── IMPLEMENTATION_SUMMARY.md      # ✨ Implementation details
```

---

## 🎯 Core Features

### 1. Resume Analysis
- Upload PDF or DOCX resume
- Extract skills, experience, education
- Get structured JSON output
- ATS compatibility scoring

### 2. Job Recommendations
- AI-powered job matching
- Skills-based recommendations
- Experience level filtering
- Domain-specific searches
- ATS scores for each job

### 3. Skill Gap Analysis
- Identify missing skills for target roles
- Get personalized learning paths
- Track skill development
- Compare against industry standards

### 4. AI Career Assistant
- Ask career-related questions
- Get personalized advice
- Resume improvement tips
- Interview preparation guidance
- Powered by NVIDIA or OpenRouter

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- NVIDIA API key ([Get one free](https://build.nvidia.com/))

### 1. Backend Setup

```powershell
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Set NVIDIA API key
$env:NVIDIA_API_KEY="nvapi-xxxxx"

# Optional: Set OpenRouter API key for fallback
$env:OPENROUTER_API_KEY="sk-or-xxxxx"

# Test integration
python test_nvidia_integration.py

# Start backend server
uvicorn main:app --reload
```

Backend will run on: http://localhost:8000

### 2. Frontend Setup

```powershell
# Navigate to root
cd ..

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on: http://localhost:5173

---

## 📚 Documentation

### Quick Start Guides
- **[QUICKSTART_ATS_NVIDIA.md](backend/QUICKSTART_ATS_NVIDIA.md)** - Get started in 5 minutes
- **[START_PROJECT.md](START_PROJECT.md)** - General project setup

### Comprehensive Guides
- **[NVIDIA_ATS_CHATBOT_GUIDE.md](backend/NVIDIA_ATS_CHATBOT_GUIDE.md)** - Complete ATS & chatbot documentation
- **[PROJECT_COMPLETE_OVERVIEW.md](PROJECT_COMPLETE_OVERVIEW.md)** - Full project overview

### Reference
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Latest implementation details
- **[IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)** - Verification checklist
- **[ENDPOINT_STATUS.md](backend/ENDPOINT_STATUS.md)** - API endpoint reference

---

## 🔑 API Endpoints

### Resume Processing
- `POST /upload-resume` - Parse resume from PDF/DOCX
- `POST /upload-resume/ats-score` - Get ATS score for resume
- `POST /upload-resume/analyze-with-jobs` - Complete analysis with jobs + ATS

### AI & Recommendations
- `POST /chat` - Chat with AI assistant (NVIDIA-powered)
- `GET /recommendations/jobs` - Get job recommendations
- `GET /recommendations/learning-path` - Get learning path

### Analysis
- `POST /analyze` - Complete profile analysis
- `POST /analysis/skill-gap` - Skill gap analysis

See [ENDPOINT_STATUS.md](backend/ENDPOINT_STATUS.md) for full API documentation.

---

## 💡 Usage Examples

### Upload Resume & Get ATS Score

**Python:**
```python
import requests

with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-resume/ats-score',
        files={'file': f},
        data={'job_description': 'Python developer with React experience'}
    )
    
result = response.json()
print(f"ATS Score: {result['ats_score']['overall_score']}/100")
print(f"Pass Likelihood: {result['ats_score']['pass_likelihood']}")
```

**JavaScript:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('job_description', 'Python developer role');

const response = await fetch('http://localhost:8000/upload-resume/ats-score', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`ATS Score: ${result.ats_score.overall_score}/100`);
```

### Chat with AI Assistant

**Python:**
```python
response = requests.post(
    'http://localhost:8000/chat',
    json={
        'question': 'How can I improve my resume for software engineering?',
        'resume_json': {'skills': ['Python', 'React'], 'experience_summary': '3 years'}
    }
)

print(response.json()['answer'])
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'What skills should I learn for senior roles?',
    resume_json: { skills: ['Python', 'React'] }
  })
});

const chat = await response.json();
console.log(chat.answer);
```

---

## 🧪 Testing

### Run Integration Tests
```powershell
cd backend
python test_nvidia_integration.py
```

Tests verify:
- ✅ PDF extraction
- ✅ NVIDIA API connection
- ✅ ATS scoring functionality
- ✅ Chatbot integration

### Manual Testing
1. Start backend: `uvicorn main:app --reload`
2. Visit API docs: http://localhost:8000/docs
3. Test endpoints interactively

---

## 🛠️ Configuration

### Environment Variables

**Required:**
```bash
NVIDIA_API_KEY=nvapi-xxxxx          # Get from build.nvidia.com
```

**Optional:**
```bash
OPENROUTER_API_KEY=sk-or-xxxxx     # Fallback AI provider
USE_NVIDIA_CHAT=true                # Use NVIDIA for chatbot (default: true)
```

### Configuration Files
- `backend/requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
- `vite.config.js` - Frontend build configuration
- `backend/main.py` - Backend API configuration

---

## 📊 ATS Score Breakdown

Your resume gets scored on:

1. **Skills Match (0-100)**: How well your skills align with job requirements
2. **Experience Match (0-100)**: Relevance of your work experience
3. **Education Match (0-100)**: Educational background alignment
4. **Formatting (0-100)**: Resume structure and ATS-readability

**Overall Score**: Weighted average of all categories

**Pass Likelihood**:
- **High (80-100)**: Strong chance of passing ATS screening
- **Medium (60-79)**: May pass, improvements recommended
- **Low (<60)**: Significant optimization needed

---

## 🎓 Tips for Better ATS Scores

### ✅ Do:
- Include keywords from job description
- Quantify achievements (e.g., "improved performance by 30%")
- Use standard section headings (Experience, Education, Skills)
- Keep formatting simple and clean
- Include relevant certifications

### ❌ Don't:
- Stuff keywords unnaturally
- Use complex tables or graphics
- Put important info in headers/footers
- Use unconventional fonts or formatting
- Include spelling or grammar errors

---

## 🔧 Tech Stack

### Frontend
- React 18
- Vite
- React Router
- Tailwind CSS

### Backend
- FastAPI
- Python 3.8+
- NVIDIA API (Qwen 3 Next 80B)
- OpenRouter API (fallback)
- FAISS (vector store)
- Sentence Transformers
- pdfplumber + PyPDF2

### AI/ML
- NVIDIA NIM APIs
- OpenRouter
- Sentence Transformers (embeddings)
- FAISS (similarity search)
- RAG (Retrieval-Augmented Generation)

---

## 🚀 Deployment

### Local Development
Already covered in Quick Start above.

### Production Deployment
1. Set environment variables securely
2. Use production ASGI server (Gunicorn + Uvicorn)
3. Configure CORS for your domain
4. Set up SSL/HTTPS
5. Monitor API usage and rate limits

---

## 🐛 Troubleshooting

### Common Issues

**"NVIDIA_API_KEY not found"**
- Solution: `$env:NVIDIA_API_KEY="nvapi-xxxxx"`
- Verify: `echo $env:NVIDIA_API_KEY`

**"Failed to initialize ATS scorer"**
- Check API key is valid
- Verify internet connection
- Ensure dependencies are installed
- Check API rate limits

**Low ATS scores**
- Add keywords from job description
- Quantify achievements
- Use standard formatting
- Review recommendations in response

**Chatbot not responding**
- Check API keys (NVIDIA or OpenRouter)
- Review server logs for errors
- Verify question is not empty
- Try simpler questions first

See [NVIDIA_ATS_CHATBOT_GUIDE.md](backend/NVIDIA_ATS_CHATBOT_GUIDE.md) for detailed troubleshooting.

---

## 📈 Performance

- **Resume Parsing**: <2 seconds
- **ATS Scoring**: 1-3 seconds (NVIDIA API)
- **Job Matching**: 2-5 seconds
- **Chatbot Response**: 1-5 seconds
- **Max File Size**: 5MB

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

---

## 📝 License

This project is open source and available for educational purposes.

---

## 🙏 Acknowledgments

- **NVIDIA** - For providing AI API access
- **OpenRouter** - For fallback AI services
- **FastAPI** - For the excellent web framework
- **React** - For the frontend framework
- **Vite** - For blazing fast development

---

## 📞 Support

### Documentation
- [Quick Start](backend/QUICKSTART_ATS_NVIDIA.md)
- [Complete Guide](backend/NVIDIA_ATS_CHATBOT_GUIDE.md)
- [API Reference](backend/ENDPOINT_STATUS.md)

### Testing
```powershell
python backend/test_nvidia_integration.py
```

### Resources
- [NVIDIA Build Platform](https://build.nvidia.com/)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## ✨ What's New

### January 2026 - Major Update
- ✅ **ATS Scoring System** - Complete resume compatibility analysis
- ✅ **NVIDIA Integration** - Enterprise-grade AI (Qwen 3 Next 80B)
- ✅ **Enhanced Chatbot** - NVIDIA-powered career guidance
- ✅ **Batch Job Scoring** - Score resume against multiple jobs
- ✅ **PDF Extraction** - Enhanced resume parsing with PyPDF2
- ✅ **Comprehensive Docs** - 3 new documentation files
- ✅ **Integration Tests** - Automated testing suite

---

## 🎯 Next Steps

1. **Upload your resume** → Get instant feedback
2. **Review ATS score** → See what to improve
3. **Get job matches** → Find relevant positions
4. **Chat with AI** → Get personalized guidance
5. **Optimize & repeat** → Improve your score

**Start now:** `python backend/test_nvidia_integration.py`

---

**Built with ❤️ for job seekers worldwide**

Good luck with your job search! 🚀
