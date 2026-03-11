# NVIDIA API Integration Guide
## ATS Scoring & Chatbot Implementation

This guide explains how to use the new NVIDIA API integration for resume ATS scoring and enhanced chatbot functionality.

---

## Features Implemented

### 1. PDF Resume Extraction & Parsing
- Extracts text from PDF and DOCX files using `pdfplumber` and `PyPDF2`
- Identifies skills, experience, education, and contact information
- Provides structured JSON output

### 2. ATS (Applicant Tracking System) Scoring
- Uses NVIDIA's Qwen 3 Next 80B model for intelligent resume analysis
- Scores resumes against job descriptions (0-100 scale)
- Provides detailed breakdown:
  - Skills match score
  - Experience match score
  - Education match score
  - Formatting score
- Identifies matched and missing keywords
- Offers actionable recommendations for improvement

### 3. Enhanced Chatbot with NVIDIA API
- Supports both NVIDIA and OpenRouter APIs
- Provides career guidance based on resume data
- Uses RAG (Retrieval-Augmented Generation) for grounded responses
- Automatically falls back to alternative providers if one fails

---

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `PyPDF2>=3.0.0` - Additional PDF parsing support
- NVIDIA API client (via `openai>=1.0.0`)

### 2. Configure NVIDIA API Key

Set your NVIDIA API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:NVIDIA_API_KEY="nvapi-xxxxx"
```

**Windows (Command Prompt):**
```cmd
set NVIDIA_API_KEY=nvapi-xxxxx
```

**Linux/Mac:**
```bash
export NVIDIA_API_KEY="nvapi-xxxxx"
```

Or create a `.env` file in the backend directory:
```
NVIDIA_API_KEY=nvapi-xxxxx
```

### 3. Get Your NVIDIA API Key

1. Visit [https://build.nvidia.com/](https://build.nvidia.com/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key (starts with `nvapi-`)

---

## API Endpoints

### 1. Upload & Parse Resume
**Endpoint:** `POST /upload-resume`

**Description:** Upload a PDF or DOCX resume and extract structured data.

**Request:**
```bash
curl -X POST "http://localhost:8000/upload-resume" \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "name": "John Doe",
  "skills": ["Python", "React", "SQL", "Docker"],
  "experience_summary": "3 years of software development experience...",
  "education": [
    {
      "degree": "Bachelor",
      "field": "Computer Science",
      "institution": "University XYZ"
    }
  ],
  "contact": {
    "email": "john@example.com",
    "phone": "+1234567890"
  }
}
```

---

### 2. Get ATS Score
**Endpoint:** `POST /upload-resume/ats-score`

**Description:** Upload resume and get comprehensive ATS compatibility score.

**Request:**
```bash
curl -X POST "http://localhost:8000/upload-resume/ats-score" \
  -F "file=@resume.pdf" \
  -F "job_description=Software Engineer position requiring Python, React, SQL..."
```

**Response:**
```json
{
  "name": "John Doe",
  "skills": ["Python", "React", "SQL"],
  "ats_score": {
    "overall_score": 85,
    "category_scores": {
      "skills_match": 90,
      "experience_match": 85,
      "education_match": 80,
      "formatting": 85
    },
    "keyword_matches": {
      "matched_keywords": ["Python", "React", "SQL", "Agile"],
      "missing_keywords": ["Kubernetes", "CI/CD"],
      "match_percentage": 85
    },
    "strengths": [
      "Strong technical skills alignment",
      "Clear work experience documentation",
      "Well-structured resume format"
    ],
    "improvement_areas": [
      "Add cloud platform experience",
      "Include more quantified achievements",
      "Mention CI/CD pipeline experience"
    ],
    "ats_recommendations": [
      "Include keywords: Kubernetes, CI/CD, Cloud",
      "Add metrics to achievements (e.g., 'improved performance by 30%')",
      "Use standard section headings: Experience, Education, Skills"
    ],
    "pass_likelihood": "high",
    "summary": "Resume shows strong alignment with job requirements. Score: 85/100 with high likelihood of passing ATS screening."
  }
}
```

---

### 3. Complete Resume Analysis with Jobs
**Endpoint:** `POST /upload-resume/analyze-with-jobs`

**Description:** Upload resume, get job recommendations, and ATS scores for each job.

**Request:**
```bash
curl -X POST "http://localhost:8000/upload-resume/analyze-with-jobs" \
  -F "file=@resume.pdf" \
  -F "target_role=Software Engineer" \
  -F "include_ats_scores=true"
```

**Response:**
```json
{
  "resume": {
    "name": "John Doe",
    "skills": ["Python", "React", "SQL"],
    "experience_summary": "..."
  },
  "job_recommendations": [
    {
      "title": "Full Stack Developer",
      "company_type": "Tech Startup",
      "description": "...",
      "required_skills": ["Python", "React", "PostgreSQL"],
      "match_score": 88,
      "ats_score": {
        "overall_score": 88,
        "pass_likelihood": "high",
        "keyword_matches": {...},
        "recommendations": [...]
      }
    }
  ],
  "target_role": "Software Engineer",
  "message": "Found 5 job recommendations with ATS scores"
}
```

---

### 4. Chat with AI Assistant (NVIDIA-Powered)
**Endpoint:** `POST /chat`

**Description:** Ask career-related questions with context-aware responses.

**Request:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What skills should I focus on to become a senior engineer?",
    "resume_json": {
      "skills": ["Python", "React"],
      "experience_summary": "3 years experience"
    }
  }'
```

**Response:**
```json
{
  "question": "What skills should I focus on to become a senior engineer?",
  "answer": "Based on your current profile with Python and React experience, I recommend focusing on: 1) System Design and Architecture - Learn to design scalable systems, 2) Leadership Skills - Mentoring junior developers, 3) Advanced Backend Technologies - Microservices, Kubernetes, 4) Cloud Platforms - AWS or Azure certification, 5) Performance Optimization - Profiling and optimization techniques. Start with system design as it's crucial for senior roles.",
  "sources": [
    {
      "content": "Senior engineers need strong system design skills...",
      "doc_id": "career_path_senior_engineer",
      "similarity": 0.89
    }
  ],
  "confidence": 0.85
}
```

---

## Code Usage Examples

### Python Client Example

```python
import requests

# 1. Upload and parse resume
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-resume',
        files={'file': f}
    )
    resume_data = response.json()
    print(f"Skills found: {resume_data['skills']}")

# 2. Get ATS score
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-resume/ats-score',
        files={'file': f},
        data={'job_description': 'Python developer with React experience'}
    )
    result = response.json()
    ats_score = result['ats_score']
    print(f"ATS Score: {ats_score['overall_score']}/100")
    print(f"Pass Likelihood: {ats_score['pass_likelihood']}")

# 3. Get complete analysis with job recommendations
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-resume/analyze-with-jobs',
        files={'file': f},
        data={
            'target_role': 'Software Engineer',
            'include_ats_scores': True
        }
    )
    analysis = response.json()
    print(f"Found {len(analysis['job_recommendations'])} jobs")
    for job in analysis['job_recommendations']:
        print(f"- {job['title']}: ATS Score {job['ats_score']['overall_score']}/100")

# 4. Chat with AI assistant
response = requests.post(
    'http://localhost:8000/chat',
    json={
        'question': 'How can I improve my resume for software engineering roles?',
        'resume_json': resume_data
    }
)
chat_response = response.json()
print(chat_response['answer'])
```

---

## Frontend Integration

### JavaScript/React Example

```javascript
// 1. Upload resume and get ATS score
async function uploadResumeWithATS(file, jobDescription) {
  const formData = new FormData();
  formData.append('file', file);
  if (jobDescription) {
    formData.append('job_description', jobDescription);
  }
  
  const response = await fetch('http://localhost:8000/upload-resume/ats-score', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data;
}

// 2. Get complete analysis with jobs
async function analyzeResumeWithJobs(file, targetRole) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('target_role', targetRole);
  formData.append('include_ats_scores', 'true');
  
  const response = await fetch('http://localhost:8000/upload-resume/analyze-with-jobs', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// 3. Chat with AI
async function chatWithAI(question, resumeData) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      resume_json: resumeData
    })
  });
  
  return await response.json();
}

// Usage example
async function handleResumeUpload(event) {
  const file = event.target.files[0];
  
  // Get ATS score
  const result = await uploadResumeWithATS(file, 
    "Looking for Python developer with React experience"
  );
  
  console.log(`ATS Score: ${result.ats_score.overall_score}/100`);
  console.log(`Recommendations:`, result.ats_score.ats_recommendations);
  
  // Get job recommendations with scores
  const analysis = await analyzeResumeWithJobs(file, "Software Engineer");
  console.log(`Found ${analysis.job_recommendations.length} matching jobs`);
  
  // Ask AI for advice
  const chatResponse = await chatWithAI(
    "How can I improve my ATS score?",
    result
  );
  console.log(chatResponse.answer);
}
```

---

## Service Architecture

### ATS Scorer Service
Located in: `backend/services/ats_scorer.py`

**Key Methods:**
- `score_resume()` - Score resume against job description
- `score_against_job_recommendation()` - Score against specific job
- `batch_score_jobs()` - Score against multiple jobs

### NVIDIA Client
Located in: `backend/services/nvidia_client.py`

**Key Methods:**
- `generate_text()` - Generate text with NVIDIA API
- `generate_ats_score()` - Generate ATS analysis
- `generate_job_recommendations()` - Generate job matches
- `generate_resume_analysis()` - Comprehensive resume review

### RAG Chatbot with NVIDIA
Located in: `backend/services/rag_chatbot.py`

**Supported Generators:**
1. `NVIDIAGenerator` - NVIDIA API (primary)
2. `OpenRouterGenerator` - OpenRouter API (fallback)
3. `FlanT5Generator` - Local model (fallback)
4. `SimpleTextGenerator` - Basic fallback

---

## Configuration Options

### Environment Variables

```bash
# Required for NVIDIA features
NVIDIA_API_KEY=nvapi-xxxxx

# Optional - for OpenRouter fallback
OPENROUTER_API_KEY=sk-or-xxxxx

# Optional - choose chatbot provider
USE_NVIDIA_CHAT=true  # Use NVIDIA for chatbot (default: OpenRouter)
```

### Chatbot Configuration

To use NVIDIA API for chatbot, update in `orchestrator.py`:

```python
self._chat_assistant = RagCareerAssistant(
    store=self.store,
    use_nvidia=True  # Enable NVIDIA API
)
```

---

## Testing

### Test NVIDIA API Integration

```bash
cd backend
python -m services.nvidia_client
```

### Test ATS Scorer

```python
from services.ats_scorer import get_ats_scorer
from services.resume_parser import ResumeParser

# Parse resume
parser = ResumeParser()
resume_data = parser.parse_resume('path/to/resume.pdf', 'pdf')

# Get ATS score
scorer = get_ats_scorer()
score = scorer.score_resume(
    resume_data=resume_data,
    job_description="Python developer with 3+ years experience"
)

print(f"ATS Score: {score['overall_score']}/100")
print(f"Recommendations: {score['ats_recommendations']}")
```

---

## Troubleshooting

### Issue: NVIDIA API Key Not Found
**Solution:** Ensure `NVIDIA_API_KEY` environment variable is set:
```bash
echo $env:NVIDIA_API_KEY  # Windows PowerShell
```

### Issue: ATS Scoring Fails
**Possible causes:**
1. NVIDIA API key invalid or expired
2. API rate limit exceeded
3. Network connectivity issues

**Solution:** Check API key and try with a fallback:
```python
# The system automatically falls back to basic scoring if API fails
```

### Issue: Chatbot Not Using NVIDIA
**Solution:** The chatbot tries providers in this order:
1. NVIDIA (if `use_nvidia=True`)
2. OpenRouter (default)
3. Local FLAN-T5
4. Simple fallback

Check logs to see which provider is active.

---

## Performance Considerations

### PDF Extraction
- Large PDFs (>5MB) are rejected for performance
- Complex layouts may not parse perfectly
- Use well-formatted resumes for best results

### ATS Scoring
- Each score request calls NVIDIA API (~1-3 seconds)
- Batch scoring is optimized for multiple jobs
- Consider caching scores for identical resume-job pairs

### Chatbot
- NVIDIA API: ~1-3 seconds per response
- OpenRouter: ~2-5 seconds per response
- Local models: Variable (CPU/GPU dependent)

---

## Best Practices

### Resume Upload
1. Use PDF format for best extraction
2. Ensure text is selectable (not scanned images)
3. Use standard section headings (Experience, Education, Skills)
4. Keep file size under 5MB

### ATS Optimization
1. Include keywords from job description
2. Quantify achievements with metrics
3. Use standard resume formatting
4. Avoid headers/footers with important information

### Chatbot Usage
1. Provide resume context for personalized advice
2. Ask specific questions for better responses
3. Include target role information when relevant

---

## Future Enhancements

Planned features:
- [ ] Resume template suggestions
- [ ] Real-time ATS optimization
- [ ] Cover letter generation
- [ ] Interview preparation guidance
- [ ] Salary negotiation advice

---

## Support

For issues or questions:
1. Check logs in `backend/` directory
2. Verify API keys are configured
3. Ensure all dependencies are installed
4. Check NVIDIA API status at [https://build.nvidia.com/](https://build.nvidia.com/)

---

## License & Credits

- NVIDIA API: [https://build.nvidia.com/](https://build.nvidia.com/)
- Qwen Model: Alibaba Cloud
- PDF Extraction: pdfplumber, PyPDF2
- Vector Store: FAISS
