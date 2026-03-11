# 🌐 Web Job Search Setup Guide

This guide will help you set up and use the real job search functionality in PathFinder AI.

---

## 🚀 **Quick Start**

The web job search feature works **immediately** without any configuration! It uses free APIs that don't require keys.

### **Test It Now**

```bash
# 1. Make sure backend is running
cd backend
python main.py

# 2. In another terminal, test the endpoint
curl "http://localhost:8000/web-jobs/search?query=Software%20Engineer&location=remote&max_results=5"
```

You should see real job listings from The Muse and RemoteOK!

---

## 📊 **Available Endpoints**

### **1. Search Jobs**
Search for jobs by keyword and location.

```http
GET /web-jobs/search

Parameters:
- query (required): Job title or keywords (e.g., "Data Analyst")
- location (optional): Location or "remote" (default: "remote")
- skills (optional): Comma-separated skills (e.g., "Python,SQL,AWS")
- experience_level (optional): Experience level (default: "Mid-level")
- max_results (optional): Max results (default: 10, max: 50)
```

**Example:**
```bash
curl "http://localhost:8000/web-jobs/search?query=Frontend%20Developer&location=remote&skills=React,JavaScript&max_results=10"
```

### **2. Get Personalized Recommendations**
Get job recommendations based on your profile.

```http
GET /web-jobs/recommended

Parameters:
- target_role (required): Target job role
- location (optional): Preferred location (default: "remote")
- skills (optional): Your skills (comma-separated)
- experience_level (optional): Your experience level
- top_n (optional): Number of results (default: 10)
```

**Example:**
```bash
curl "http://localhost:8000/web-jobs/recommended?target_role=Data%20Scientist&skills=Python,Machine%20Learning,TensorFlow&top_n=10"
```

---

## 🔑 **Optional: Add More Job Sources**

To get even more job listings, you can add the Adzuna API (free tier available).

### **Step 1: Get Adzuna API Key**

1. Go to https://developer.adzuna.com/
2. Click "Sign up for free"
3. Fill in your details
4. You'll receive:
   - `app_id`
   - `app_key`

### **Step 2: Add to Environment**

Create or update `backend/.env`:

```env
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here
```

### **Step 3: Restart Backend**

```bash
cd backend
python main.py
```

Now your searches will include jobs from Adzuna too!

---

## 📝 **Response Format**

All endpoints return JSON in this format:

```json
{
    "query": "Software Engineer",
    "location": "remote",
    "web_jobs": [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Company Inc.",
            "location": "Remote",
            "description": "We are looking for...",
            "url": "https://...",
            "salary": 120000,
            "posted_date": "2026-01-20",
            "source": "The Muse",
            "job_type": "Full-time",
            "match_score": 85.5
        }
    ],
    "recommended_jobs": [
        // AI-recommended jobs from local database
    ],
    "total_results": 15,
    "sources": ["The Muse", "RemoteOK", "Local Database"]
}
```

---

## 🎯 **Match Score Explained**

Each job gets a match score (0-100) based on:

- **Title Match (40 points)**
  - Exact match: 40 points
  - Partial match: 20 points

- **Skill Match (40 points)**
  - Based on how many of your skills appear in the job description

- **Location Bonus (10 points)**
  - Remote jobs get extra points

- **Recency Bonus (10 points)**
  - Recently posted jobs rank higher

---

## 💻 **Frontend Integration Example**

Update your Job Recommendations page:

```javascript
import { apiService } from '../services/api';

// Search for jobs
const searchJobs = async () => {
  const results = await fetch(
    `http://localhost:8000/web-jobs/search?query=${encodeURIComponent(targetRole)}&location=remote&skills=${skills.join(',')}&max_results=10`
  ).then(r => r.json());
  
  setJobs(results.web_jobs);
};

// Display jobs
{jobs.map(job => (
  <div key={job.url}>
    <h3>{job.title} at {job.company}</h3>
    <p>Match: {job.match_score}%</p>
    <p>{job.location} • {job.job_type}</p>
    <a href={job.url} target="_blank">Apply Now</a>
  </div>
))}
```

---

## 🔍 **Job Sources**

### **1. The Muse** (Free, no key needed)
- High-quality tech and creative jobs
- Detailed company information
- Focus on culture fit
- API Limit: ~100 requests/day

### **2. RemoteOK** (Free, no key needed)
- Exclusively remote positions
- Tech-focused
- Global companies
- API Limit: No official limit, but rate-limit friendly

### **3. Adzuna** (Optional, free tier)
- Global job listings
- Multiple industries
- Salary data included
- Free Tier: 500 calls/month

---

## 🐛 **Troubleshooting**

### **No Jobs Returned**

**Problem:** API returns empty list

**Solutions:**
1. Try broader search terms:
   - ❌ "Senior React Developer with 5 years experience"
   - ✅ "React Developer"

2. Check if services are accessible:
   ```bash
   curl https://www.themuse.com/api/public/jobs
   curl https://remoteok.com/api
   ```

3. Try different locations:
   - "remote"
   - "New York"
   - "London"

### **Rate Limit Errors**

**Problem:** Too many requests

**Solution:** Add delays between requests:

```python
import time
time.sleep(1)  # Wait 1 second between requests
```

### **Connection Timeout**

**Problem:** API takes too long to respond

**Solutions:**
1. Increase timeout in `web_job_scraper.py`:
   ```python
   response = self.session.get(url, timeout=30)  # 30 seconds
   ```

2. Handle timeouts gracefully:
   ```python
   try:
       jobs = scraper.search_jobs(...)
   except requests.Timeout:
       return {"error": "Search timed out, try again"}
   ```

---

## 📊 **Testing Different Searches**

### **Tech Roles**
```bash
# Software Engineering
curl "http://localhost:8000/web-jobs/search?query=Software%20Engineer&location=remote"

# Data Science
curl "http://localhost:8000/web-jobs/search?query=Data%20Scientist&skills=Python,ML"

# DevOps
curl "http://localhost:8000/web-jobs/search?query=DevOps%20Engineer&skills=AWS,Docker,Kubernetes"
```

### **Non-Tech Roles**
```bash
# Product Management
curl "http://localhost:8000/web-jobs/search?query=Product%20Manager&location=San%20Francisco"

# Marketing
curl "http://localhost:8000/web-jobs/search?query=Digital%20Marketing"

# Design
curl "http://localhost:8000/web-jobs/search?query=UX%20Designer&location=remote"
```

---

## 🎨 **Customization**

### **Add Custom Job Source**

Edit `backend/services/web_job_scraper.py`:

```python
def _search_custom_api(self, query, location, country, max_results):
    """Search your custom job API."""
    url = "https://your-api.com/jobs"
    response = self.session.get(url, params={
        'q': query,
        'location': location,
        'limit': max_results
    })
    
    jobs = []
    for item in response.json():
        jobs.append({
            'title': item['title'],
            'company': item['company_name'],
            'location': item['location'],
            'description': item['description'][:500] + '...',
            'url': item['apply_url'],
            'salary': item.get('salary', 0),
            'posted_date': item['posted_at'],
            'source': 'Custom API',
            'job_type': item.get('type', 'Full-time'),
        })
    return jobs
```

Then add to sources list:
```python
sources = [
    ("The Muse", self._search_muse),
    ("RemoteOK", self._search_remoteok),
    ("Custom API", self._search_custom_api),  # Add here
]
```

---

## 📈 **Performance Tips**

1. **Cache Results**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def search_jobs_cached(query, location):
       return scraper.search_jobs(query, location)
   ```

2. **Parallel Requests**
   ```python
   import asyncio
   import aiohttp
   
   async def search_all_sources():
       tasks = [
           search_muse_async(),
           search_remoteok_async(),
           search_adzuna_async(),
       ]
       return await asyncio.gather(*tasks)
   ```

3. **Database Caching**
   - Store results in MongoDB/Redis
   - Refresh every 24 hours
   - Serve from cache if available

---

## 🎯 **Best Practices**

1. **Respectful Scraping**
   - Add delays between requests
   - Follow robots.txt
   - Don't overwhelm APIs

2. **Error Handling**
   - Always have fallbacks
   - Return partial results if some sources fail
   - Log errors for debugging

3. **User Experience**
   - Show loading indicators
   - Display which sources succeeded/failed
   - Provide filtering options

---

## 📞 **Support**

Having issues? Check:

1. **Backend Logs**
   ```bash
   tail -f backend/logs/app.log
   ```

2. **Test Directly**
   ```bash
   cd backend
   python services/web_job_scraper.py
   ```

3. **Check API Status**
   - The Muse: https://www.themuse.com/developers/api/v2
   - RemoteOK: https://remoteok.com/api
   - Adzuna: https://developer.adzuna.com/docs/api_intro

---

## 🎉 **You're All Set!**

Your PathFinder AI now searches **real, live job postings** from multiple sources!

**Next Steps:**
1. Test the endpoints
2. Integrate into your frontend
3. Customize match scoring
4. Add more job sources
5. Implement caching for better performance

Happy job hunting! 🚀
