# 🚀 Quick Start: RapidAPI Job Search Integration

## ✅ What You Have Now

Your backend now has **smart, resume-based job recommendations** using RapidAPI JSearch (Indeed, LinkedIn, Glassdoor).

---

## 🔑 API Key (Already Configured!)

```
Your API Key: c0d23f9058msh4d8de44e3f0e86dp15ee2cjsn34acc712be7b
```

This is already set in the code. No additional setup needed! 🎉

---

## 📡 New Endpoint

### **POST** `/upload-resume/smart-job-match`

Upload a resume and get personalized job matches!

---

## 🧪 Test It Right Now!

### Option 1: Using cURL (Command Line)

```bash
# Navigate to your project folder
cd D:\gopal\mani\CURSORFINALYRPROJECT\backend

# Test the endpoint
curl -X POST "http://localhost:8000/upload-resume/smart-job-match" \
  -F "file=@test_resume.pdf" \
  -F "target_role=Software Engineer" \
  -F "location=remote" \
  -F "max_results=10"
```

### Option 2: Using Python Script

Create `test_job_match.py`:

```python
import requests

# Your backend URL
url = "http://localhost:8000/upload-resume/smart-job-match"

# Upload a resume file
files = {'file': open('test_resume.pdf', 'rb')}

# Parameters
data = {
    'target_role': 'Full Stack Developer',  # Or leave empty for auto-detect
    'location': 'remote',
    'max_results': 15,
    'prioritize_india': True
}

# Make request
response = requests.post(url, files=files, data=data)

# Print results
result = response.json()
print(f"\n✅ Found {result['total_jobs']} jobs!")
print(f"📊 Average Relevance: {result['avg_relevance_score']}%\n")

# Print top 3 jobs
for i, job in enumerate(result['jobs'][:3], 1):
    print(f"{i}. {job['title']} at {job['company']}")
    print(f"   Location: {job['location']}")
    print(f"   Salary: ${job['salary_min']:,} - ${job['salary_max']:,}")
    print(f"   Match: {job['relevance_score']}%")
    print(f"   URL: {job['url']}\n")
```

Run it:
```bash
python test_job_match.py
```

### Option 3: Using Postman

1. Open Postman
2. Create new POST request
3. URL: `http://localhost:8000/upload-resume/smart-job-match`
4. Body → form-data:
   - `file`: Select your resume PDF/DOCX
   - `target_role`: "Software Engineer"
   - `location`: "remote"
   - `max_results`: 15
   - `prioritize_india`: true
5. Click **Send**

---

## 📊 What You'll Get Back

```json
{
  "success": true,
  "resume": {
    "name": "John Doe",
    "skills": ["Python", "React", "Node.js", "AWS"],
    "experience": [...]
  },
  "jobs": [
    {
      "title": "Full Stack Developer",
      "company": "Tech Corp",
      "location": "Remote",
      "salary": 85000,
      "salary_min": 70000,
      "salary_max": 100000,
      "relevance_score": 87.5,
      "skill_match_percentage": 80.0,
      "url": "https://www.indeed.com/viewjob?...",
      "qualifications": ["3+ years React", "Python experience"],
      "benefits": ["Health insurance", "Remote work"]
    }
  ],
  "total_jobs": 15,
  "avg_relevance_score": 75.3
}
```

---

## 🎯 Features

### 1. **Auto-Detect Target Role**
```python
# Don't know what role to search for?
target_role = None  # Leave empty!

# The system will detect from resume:
# - React + Node.js → "Full Stack Developer"
# - Python + ML → "Machine Learning Engineer"
# - AWS + Docker → "DevOps Engineer"
```

### 2. **Relevance Scoring (0-100)**
```
Jobs are scored based on:
- Skill Match (50%): How many skills match
- Experience Level (20%): Junior/Mid/Senior match
- Salary Info (10%): Has salary data
- Remote (10%): Remote job bonus
- Recent (10%): Recently posted
```

### 3. **Rich Job Data**
```
Each job includes:
✅ Title, company, location
✅ Salary range (min/max/avg)
✅ Job description
✅ Qualifications needed
✅ Responsibilities
✅ Benefits
✅ Company logo
✅ Direct apply URL
✅ Relevance score
✅ Skill match percentage
```

---

## 🌍 Location Options

### Remote Jobs
```python
location = "remote"
# Searches only remote positions
```

### India Jobs
```python
location = "Mumbai"
# or
location = "Bangalore"
# or
location = "India"
prioritize_india = True  # Prioritizes Indian jobs
```

### US Jobs
```python
location = "San Francisco"
# or
location = "New York"
prioritize_india = False
```

### Any Location
```python
location = "remote"
prioritize_india = False
# Gets jobs from all countries
```

---

## 🎨 Frontend Integration (Next Step)

Add this to your React frontend:

```javascript
// services/api.js
export const getPersonalizedJobs = async (resumeFile, targetRole) => {
  const formData = new FormData();
  formData.append('file', resumeFile);
  formData.append('target_role', targetRole || '');
  formData.append('location', 'remote');
  formData.append('max_results', '15');
  formData.append('prioritize_india', 'true');
  
  const response = await fetch(
    'http://localhost:8000/upload-resume/smart-job-match',
    {
      method: 'POST',
      body: formData
    }
  );
  
  return response.json();
};

// Use in component
const handleResumeUpload = async (file) => {
  setLoading(true);
  try {
    const data = await getPersonalizedJobs(file, 'Software Engineer');
    setJobs(data.jobs);
    setRelevanceScore(data.avg_relevance_score);
  } catch (error) {
    console.error('Error:', error);
  } finally {
    setLoading(false);
  }
};
```

---

## 🎯 Usage Examples

### Example 1: Auto-Detect Role
```python
# Upload resume, let system detect role
POST /upload-resume/smart-job-match
{
  "file": resume.pdf,
  "location": "remote",
  "max_results": 15
}
# System auto-detects: "Full Stack Developer"
```

### Example 2: Specific Role
```python
# Search for specific role
POST /upload-resume/smart-job-match
{
  "file": resume.pdf,
  "target_role": "Machine Learning Engineer",
  "location": "Bangalore",
  "max_results": 10,
  "prioritize_india": true
}
```

### Example 3: Remote Only
```python
# Remote jobs worldwide
POST /upload-resume/smart-job-match
{
  "file": resume.pdf,
  "target_role": "DevOps Engineer",
  "location": "remote",
  "max_results": 20,
  "prioritize_india": false
}
```

---

## 🎊 Benefits

### For Users:
- ✅ Real jobs from Indeed, LinkedIn, Glassdoor
- ✅ Personalized to their resume
- ✅ Relevance scores show best matches
- ✅ Direct apply links
- ✅ Salary information
- ✅ No more fake job listings

### For You (Developer):
- ✅ Easy to integrate
- ✅ Already configured
- ✅ No additional setup
- ✅ Works out of the box
- ✅ Rich data for UI

---

## 📈 Testing Checklist

Test these scenarios:

1. ✅ **Upload resume with Python skills**
   - Expected: Python developer jobs
   
2. ✅ **Upload resume with React skills**
   - Expected: Frontend/Full Stack jobs
   
3. ✅ **Auto-detect role (no target_role)**
   - Expected: Role detected from resume
   
4. ✅ **Remote location**
   - Expected: Only remote jobs
   
5. ✅ **India location**
   - Expected: India-based jobs
   
6. ✅ **Check relevance scores**
   - Expected: Jobs sorted by score (high to low)
   
7. ✅ **Check apply URLs**
   - Expected: Valid Indeed/LinkedIn URLs

---

## 🚨 Troubleshooting

### Issue: No jobs found
**Solution:**
- Broaden search (use "Developer" instead of specific role)
- Try "remote" location
- Check API key is valid

### Issue: Low relevance scores
**Solution:**
- Update resume with more skills
- Try different target role
- Check skill keywords match industry standards

### Issue: API timeout
**Solution:**
- Retry after a few seconds
- Check internet connection
- Verify backend is running

---

## ✅ Files Modified

1. **`services/web_job_scraper.py`**
   - Enhanced JSearch API integration
   - Better error handling
   - More job details

2. **`services/resume_job_matcher.py`** (NEW)
   - Resume-based job matching
   - Relevance scoring
   - Auto role detection

3. **`routers/resume.py`**
   - New `/smart-job-match` endpoint
   - Resume parsing + job matching

4. **Documentation**
   - `RAPIDAPI_JOB_INTEGRATION.md` - Full guide
   - `QUICK_START_RAPIDAPI.md` - This file

---

## 🎉 Ready to Use!

Your job recommendation system is now:
- ✅ Connected to RapidAPI JSearch
- ✅ Matching jobs to resumes
- ✅ Scoring relevance (0-100)
- ✅ Returning real job data
- ✅ Ready for frontend integration

**Test it now with the examples above!** 🚀

---

## 🔗 Next Steps

1. **Test the endpoint** with your resume
2. **Integrate with frontend** (React/Vue/etc)
3. **Design job cards** to display results
4. **Add filtering** (salary, location, etc)
5. **Show skill matches** in UI
6. **Add "Apply" buttons** with job URLs

---

**Everything is ready! Start testing! 🎊**
