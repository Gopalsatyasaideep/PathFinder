# 🚀 Enhanced Job Recommendations with RapidAPI JSearch Integration

## Overview

Your job recommendation system now uses **RapidAPI JSearch** to search real job postings from Indeed, LinkedIn, and Glassdoor, providing personalized matches based on your resume.

---

## ✅ What's New

### 1. **RapidAPI JSearch Integration**
- Searches Indeed, LinkedIn, and Glassdoor in one API call
- Returns real, up-to-date job postings
- Includes company logos, salaries, qualifications, and benefits
- Supports remote jobs and location-based searches

### 2. **Resume-Based Job Matching**
- Auto-detects target role from resume
- Scores jobs based on skill match (0-100)
- Shows matched skills and skill match percentage
- Ranks jobs by relevance to your resume

### 3. **Enhanced Job Data**
- Job title and company
- Location (or Remote)
- Salary range (min/max/average)
- Job description and requirements
- Qualifications needed
- Responsibilities
- Benefits
- Apply URL (direct to job posting)
- Company logo
- Posted date

---

## 🔑 API Key Setup

Your API key is already configured:
```
API Key: c0d23f9058msh4d8de44e3f0e86dp15ee2cjsn34acc712be7b
```

To use a different key, set it in your `.env` file:
```bash
RAPIDAPI_KEY=your_key_here
```

Get a free key at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

---

## 📡 New API Endpoint

### `/upload-resume/smart-job-match` (POST)

**Description:** Upload resume and get personalized job matches from Indeed/LinkedIn/Glassdoor

**Request:**
```bash
curl -X POST "http://localhost:8000/upload-resume/smart-job-match" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf" \
  -F "target_role=Full Stack Developer" \
  -F "location=remote" \
  -F "max_results=15" \
  -F "prioritize_india=true"
```

**Parameters:**
- `file` (required): Resume PDF or DOCX
- `target_role` (optional): Desired job title (auto-detected if not provided)
- `location` (default: "remote"): Job location or "remote"
- `max_results` (default: 15): Number of jobs to return
- `prioritize_india` (default: true): Prioritize Indian jobs

**Response:**
```json
{
  "success": true,
  "resume": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "skills": ["Python", "React", "Node.js", "AWS"],
    "experience": [...],
    "education": [...]
  },
  "jobs": [
    {
      "title": "Full Stack Developer",
      "company": "Tech Company Inc",
      "location": "Remote",
      "description": "We are looking for a Full Stack Developer...",
      "url": "https://www.indeed.com/viewjob?jk=xxxxx",
      "salary": 85000,
      "salary_min": 70000,
      "salary_max": 100000,
      "posted_date": "2026-01-20",
      "source": "JSearch (Indeed/LinkedIn/Glassdoor)",
      "job_type": "Full-time",
      "is_remote": true,
      "company_logo": "https://...",
      "qualifications": [
        "3+ years of experience with React",
        "Strong Python skills",
        "Experience with AWS"
      ],
      "responsibilities": [
        "Build scalable web applications",
        "Collaborate with design team",
        "Write clean, maintainable code"
      ],
      "benefits": [
        "Health insurance",
        "401(k) matching",
        "Remote work"
      ],
      "relevance_score": 87.5,
      "matched_skills": 4,
      "skill_match_percentage": 80.0
    }
  ],
  "target_role": "Full Stack Developer",
  "location": "remote",
  "total_jobs": 15,
  "avg_relevance_score": 75.3,
  "message": "Found 15 jobs matching your resume with avg relevance 75.3%"
}
```

---

## 🎯 How It Works

### 1. Resume Parsing
```python
# Extracts from resume:
- Name, email, phone
- Skills (technical and soft skills)
- Experience (years, roles, companies)
- Education
```

### 2. Auto-Detection (if no target role provided)
```python
# Detects role from:
- Most recent job title
- Skills pattern (e.g., React → Frontend Developer)
- Experience level (years of experience)
```

### 3. Smart Query Building
```python
# Combines:
- Target role: "Full Stack Developer"
- Top 2-3 skills: "React Node.js"
- Location: "remote" or specific city

# Example query: "Full Stack Developer React Node.js remote"
```

### 4. Job Search (RapidAPI JSearch)
```python
# Searches:
- Indeed
- LinkedIn
- Glassdoor
- Filters by: location, date posted, remote
- Returns: 15+ jobs with full details
```

### 5. Relevance Scoring (0-100)
```python
# Factors:
1. Skill Match (50%):
   - Matches resume skills against job requirements
   - Higher score = more skills matched

2. Experience Level (20%):
   - Entry-level: prefers junior/entry roles
   - Mid-level: prefers mid-level roles
   - Senior: prefers senior/lead roles

3. Salary Info (10%):
   - Bonus if salary is provided

4. Remote Job (10%):
   - Bonus for remote jobs

5. Recent Posting (10%):
   - Bonus for recently posted jobs

# Example:
- 5 out of 8 skills matched: 50 * (5/8) = 31.25
- Mid-level role matches: +20
- Salary provided: +10
- Remote job: +10
- Posted this month: +10
# Total: 81.25/100
```

### 6. Ranking and Return
```python
# Jobs sorted by relevance_score (highest first)
# Returns top N jobs with:
- Full job details
- Relevance score
- Matched skills count
- Skill match percentage
```

---

## 📊 Frontend Integration

### Example Usage in React

```javascript
import { apiService } from './services/api';

async function getPersonalizedJobs(resumeFile) {
  const formData = new FormData();
  formData.append('file', resumeFile);
  formData.append('target_role', 'Full Stack Developer');
  formData.append('location', 'remote');
  formData.append('max_results', '15');
  formData.append('prioritize_india', 'true');
  
  try {
    const response = await fetch('http://localhost:8000/upload-resume/smart-job-match', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    // data.jobs = array of matched jobs
    // data.avg_relevance_score = average match score
    // data.resume = parsed resume data
    
    return data;
  } catch (error) {
    console.error('Error fetching jobs:', error);
  }
}

// Display jobs
function JobCard({ job }) {
  return (
    <div className="job-card">
      <div className="job-header">
        {job.company_logo && <img src={job.company_logo} alt={job.company} />}
        <div>
          <h3>{job.title}</h3>
          <p>{job.company} - {job.location}</p>
        </div>
        <div className="relevance-badge">
          {job.relevance_score}% Match
        </div>
      </div>
      
      <div className="job-details">
        <p>{job.description}</p>
        <p>💰 ${job.salary_min?.toLocaleString()} - ${job.salary_max?.toLocaleString()}</p>
        <p>📅 Posted: {job.posted_date}</p>
        <p>🏢 {job.job_type} {job.is_remote && '• Remote'}</p>
      </div>
      
      <div className="matched-skills">
        <strong>Matched Skills ({job.skill_match_percentage}%):</strong>
        {job.qualifications.map(q => <span key={q}>{q}</span>)}
      </div>
      
      <a href={job.url} target="_blank" className="apply-button">
        Apply Now →
      </a>
    </div>
  );
}
```

---

## 🎨 Job Card Design

Each job card should display:

```
┌─────────────────────────────────────────────┐
│ [Logo] Full Stack Developer     [87% Match] │
│        Tech Company Inc • Remote             │
├─────────────────────────────────────────────┤
│ Description: Build scalable web apps...     │
│ 💰 $70,000 - $100,000                       │
│ 📅 Posted: 2026-01-20                       │
│ 🏢 Full-time • Remote                       │
├─────────────────────────────────────────────┤
│ ✅ Matched Skills (80%):                    │
│ • 3+ years React • Python • AWS             │
├─────────────────────────────────────────────┤
│ 📋 Responsibilities:                        │
│ • Build scalable applications               │
│ • Collaborate with team                     │
├─────────────────────────────────────────────┤
│ 🎁 Benefits:                                │
│ • Health insurance • 401(k) • Remote        │
├─────────────────────────────────────────────┤
│              [Apply Now →]                  │
└─────────────────────────────────────────────┘
```

---

## 🚀 Benefits Over Old System

### Before:
- ❌ Generic job listings
- ❌ No skill matching
- ❌ No relevance scoring
- ❌ Limited data
- ❌ Fake/template jobs

### After:
- ✅ Real jobs from Indeed/LinkedIn/Glassdoor
- ✅ Resume-based matching
- ✅ Relevance scores (0-100)
- ✅ Rich data (qualifications, benefits, salaries)
- ✅ Auto-detect target role
- ✅ Skills match percentage
- ✅ Direct apply URLs

---

## 🔧 Configuration

### Environment Variables

```bash
# Required (or use default)
RAPIDAPI_KEY=c0d23f9058msh4d8de44e3f0e86dp15ee2cjsn34acc712be7b

# Optional: Prioritize specific country
PRIORITIZE_COUNTRY=in  # Default: India

# Optional: Default max results
DEFAULT_MAX_JOBS=15
```

### Custom API Key

If you want to use your own RapidAPI key:
1. Sign up at https://rapidapi.com
2. Subscribe to JSearch API (free tier available)
3. Get your API key
4. Set it in `.env` file:
   ```bash
   RAPIDAPI_KEY=your_new_key_here
   ```

---

## 📈 API Limits (Free Tier)

JSearch Free Plan:
- 100 requests/month
- 10 requests/day
- 1 request/second

If you need more, upgrade to:
- Basic: $9.99/month (1000 requests)
- Pro: $49.99/month (10000 requests)
- Ultra: $199.99/month (100000 requests)

---

## 🧪 Testing

### Test with cURL

```bash
# Upload resume and get matched jobs
curl -X POST "http://localhost:8000/upload-resume/smart-job-match" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/resume.pdf" \
  -F "target_role=Software Engineer" \
  -F "location=remote" \
  -F "max_results=10"
```

### Test with Python

```python
import requests

url = "http://localhost:8000/upload-resume/smart-job-match"
files = {'file': open('resume.pdf', 'rb')}
data = {
    'target_role': 'Full Stack Developer',
    'location': 'remote',
    'max_results': 15,
    'prioritize_india': True
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

---

## 🎯 Example Queries

### Remote Jobs
```python
location = "remote"
# Searches for remote positions only
```

### Location-Specific
```python
location = "Mumbai"
# or
location = "Bangalore, India"
# or
location = "San Francisco"
```

### Auto-Detect Role
```python
target_role = None  # Will detect from resume
# Examples of auto-detected roles:
# - React + Node.js → "Full Stack Developer"
# - Python + ML → "Machine Learning Engineer"
# - AWS + Docker → "DevOps Engineer"
```

---

## 🐛 Troubleshooting

### No Jobs Found
**Cause:** Query too specific or API rate limit
**Solution:** 
- Broaden target role (e.g., "Developer" instead of "Senior React Native Developer")
- Check API key is valid
- Try different location

### Low Relevance Scores
**Cause:** Resume skills don't match job requirements
**Solution:**
- Update resume with more relevant skills
- Try different target role
- Broaden location search

### API Timeout
**Cause:** RapidAPI is slow or unavailable
**Solution:**
- Retry after a few seconds
- Check API status: https://rapidapi.com/status
- Use fallback to other job sources

---

## 📚 Additional Resources

- **RapidAPI JSearch Docs**: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
- **Job Search Best Practices**: https://www.indeed.com/career-advice/finding-a-job
- **Resume Optimization**: https://www.indeed.com/career-advice/resumes-cover-letters

---

## ✅ Summary

Your job recommendation system now:
1. ✅ Uses real job data from Indeed/LinkedIn/Glassdoor via RapidAPI
2. ✅ Matches jobs to your resume skills (0-100 relevance score)
3. ✅ Auto-detects target role from resume
4. ✅ Provides rich job data (salary, benefits, qualifications)
5. ✅ Returns direct apply URLs
6. ✅ Works with remote and location-based searches
7. ✅ Prioritizes Indian jobs when requested

**Start using the `/upload-resume/smart-job-match` endpoint today!** 🚀
