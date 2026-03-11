# Quick Start Guide: Resume ATS Scoring & NVIDIA Chatbot

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

### Step 2: Set NVIDIA API Key
Get your free API key from [https://build.nvidia.com/](https://build.nvidia.com/)

```powershell
$env:NVIDIA_API_KEY="nvapi-xxxxx"
```

### Step 3: Test the Integration
```powershell
python test_nvidia_integration.py
```

### Step 4: Start the Backend
```powershell
uvicorn main:app --reload
```

---

## 📝 Quick Examples

### Upload Resume & Get ATS Score

**Using curl:**
```bash
curl -X POST "http://localhost:8000/upload-resume/ats-score" \
  -F "file=@resume.pdf" \
  -F "job_description=Python developer with React experience"
```

**Using Python:**
```python
import requests

with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-resume/ats-score',
        files={'file': f},
        data={'job_description': 'Python developer role'}
    )
    result = response.json()
    print(f"ATS Score: {result['ats_score']['overall_score']}/100")
```

**Using JavaScript:**
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

---

### Get Job Recommendations with ATS Scores

```python
import requests

with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-resume/analyze-with-jobs',
        files={'file': f},
        data={
            'target_role': 'Software Engineer',
            'include_ats_scores': True
        }
    )
    
result = response.json()

# Display results
for job in result['job_recommendations']:
    print(f"\n{job['title']}")
    print(f"  Match: {job['match_score']}/100")
    print(f"  ATS: {job['ats_score']['overall_score']}/100")
    print(f"  Likelihood: {job['ats_score']['pass_likelihood']}")
```

---

### Chat with NVIDIA-Powered AI

```python
import requests

response = requests.post(
    'http://localhost:8000/chat',
    json={
        'question': 'How can I improve my resume for software engineering?',
        'resume_json': {
            'skills': ['Python', 'React'],
            'experience_summary': '3 years experience'
        }
    }
)

chat = response.json()
print(chat['answer'])
```

---

## 🎯 Key Features

### 1. PDF Resume Extraction
- ✅ Extracts text from PDF and DOCX
- ✅ Identifies skills, experience, education
- ✅ Returns structured JSON

### 2. ATS Scoring
- ✅ 0-100 score with detailed breakdown
- ✅ Keyword match analysis
- ✅ Actionable recommendations
- ✅ Pass likelihood (high/medium/low)

### 3. NVIDIA-Powered Chatbot
- ✅ Context-aware responses
- ✅ Career guidance
- ✅ Resume improvement tips
- ✅ RAG-based (grounded in your data)

---

## 📊 Understanding ATS Scores

### Score Breakdown:
```json
{
  "overall_score": 85,          // 0-100, higher is better
  "category_scores": {
    "skills_match": 90,         // How well skills match
    "experience_match": 85,     // Experience relevance
    "education_match": 80,      // Education alignment
    "formatting": 85            // Resume format quality
  },
  "pass_likelihood": "high"     // high/medium/low
}
```

### Pass Likelihood:
- **High (80-100):** Strong chance of passing ATS
- **Medium (60-79):** May pass with improvements
- **Low (<60):** Needs significant optimization

---

## 🔧 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload-resume` | POST | Parse resume only |
| `/upload-resume/ats-score` | POST | Parse + ATS score |
| `/upload-resume/analyze-with-jobs` | POST | Parse + Jobs + ATS |
| `/chat` | POST | AI career assistant |

---

## 🐛 Troubleshooting

### Issue: "NVIDIA_API_KEY not found"
```powershell
# Set the environment variable
$env:NVIDIA_API_KEY="nvapi-xxxxx"

# Verify it's set
echo $env:NVIDIA_API_KEY
```

### Issue: "Failed to initialize ATS scorer"
1. Check API key is valid
2. Test with: `python test_nvidia_integration.py`
3. Check internet connection

### Issue: Low ATS Score
Common fixes:
- Add keywords from job description
- Quantify achievements with metrics
- Use standard section headings
- Remove graphics/tables from resume

---

## 📈 Improving Your ATS Score

### Do:
✅ Use keywords from job description  
✅ Quantify achievements (e.g., "improved by 30%")  
✅ Standard headings (Experience, Education, Skills)  
✅ Simple formatting (no complex tables/graphics)  
✅ Include relevant certifications  

### Don't:
❌ Keyword stuffing  
❌ Complex formatting  
❌ Graphics or images  
❌ Headers/footers with key info  
❌ Misspellings or typos  

---

## 💡 Pro Tips

1. **Test Multiple Versions:** Upload different resume versions to compare scores
2. **Use Job Description:** Always provide the actual job description for accurate scoring
3. **Iterate:** Use recommendations to improve, then re-score
4. **Ask the Chatbot:** Get specific advice for your situation
5. **Check All Jobs:** Different jobs may score your resume differently

---

## 🔗 Resources

- [NVIDIA API Documentation](https://build.nvidia.com/)
- [Full Integration Guide](NVIDIA_ATS_CHATBOT_GUIDE.md)
- [API Reference](ENDPOINT_STATUS.md)

---

## 📞 Support

Need help?
1. Run tests: `python test_nvidia_integration.py`
2. Check logs in terminal
3. Verify API key: `echo $env:NVIDIA_API_KEY`
4. Review full guide: `NVIDIA_ATS_CHATBOT_GUIDE.md`

---

## ✨ Next Steps

1. **Upload your resume** → Get instant ATS score
2. **Review recommendations** → See what to improve
3. **Chat with AI** → Get personalized advice
4. **Apply optimizations** → Improve your score
5. **Re-test** → Verify improvements

Good luck with your job search! 🎉
