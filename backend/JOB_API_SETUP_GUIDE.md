# Job Search API Setup Guide

## Overview
PathFinder now integrates with **7+ job search APIs** to fetch real-time job postings from Indeed, LinkedIn, Glassdoor, and more. This ensures you get **10+ quality job results** for every search.

---

## Free APIs (No Key Required)

### 1. **The Muse** ✅
- **Status**: Already working
- **Coverage**: Remote jobs, tech roles
- **Free**: Yes
- **Setup**: None needed

### 2. **RemoteOK** ✅
- **Status**: Already working
- **Coverage**: Remote tech jobs worldwide
- **Free**: Yes
- **Setup**: None needed

### 3. **Arbeitnow** ✅
- **Status**: Already working
- **Coverage**: European remote jobs
- **Free**: Yes
- **Setup**: None needed

---

## Recommended APIs (Free Tier Available)

### 4. **RapidAPI JSearch** ⭐ BEST
Aggregates jobs from Indeed, LinkedIn, Glassdoor, ZipRecruiter, and more.

**Free Tier**: 2,500 requests/month

**Setup Steps**:
1. Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
2. Click "Sign Up Free"
3. Subscribe to the **Basic Plan (Free)**
4. Copy your API key from the dashboard
5. Add to your `.env` file:
   ```env
   RAPIDAPI_KEY=your_api_key_here
   ```

---

### 5. **Adzuna**
Multi-country job search API

**Free Tier**: 250 calls/month

**Setup Steps**:
1. Go to https://developer.adzuna.com/
2. Click "Get your API keys"
3. Create a free account
4. Copy your App ID and App Key
5. Add to your `.env` file:
   ```env
   ADZUNA_APP_ID=your_app_id
   ADZUNA_APP_KEY=your_app_key
   ```

---

### 6. **Reed UK**
UK-focused job search

**Free Tier**: 1,000 calls/month

**Setup Steps**:
1. Go to https://www.reed.co.uk/developers
2. Register for an API key
3. Add to your `.env` file:
   ```env
   REED_API_KEY=your_api_key
   ```

---

### 7. **USAJobs**
US Government jobs

**Free**: Unlimited

**Setup Steps**:
1. Go to https://developer.usajobs.gov/
2. Request an API key
3. Add to your `.env` file:
   ```env
   USAJOBS_API_KEY=your_api_key
   USAJOBS_USER_AGENT=PathFinderApp/1.0
   ```

---

## Quick Start (Recommended)

### Minimum Setup for 10+ Jobs:
1. **Already Working**: The Muse, RemoteOK, Arbeitnow (3 APIs)
2. **Add RapidAPI JSearch** (⭐ BEST - 5 minutes setup)

This gives you **4+ data sources** ensuring **10-15 jobs per search**.

### Full Setup for Maximum Jobs:
Add all 7 APIs above to get **20-30 jobs per search** from all major sources.

---

## Testing Your Setup

1. **Check which APIs are active**:
   ```bash
   cd backend
   python services/web_job_scraper.py
   ```

2. **Test API endpoint**:
   ```bash
   curl "http://localhost:8000/web-jobs/search?query=Software%20Engineer&location=remote&max_results=15"
   ```

3. **Expected Output**:
   - Without API keys: 5-8 jobs (from free APIs)
   - With RapidAPI JSearch: 10-15 jobs
   - With all APIs: 20-30 jobs

---

## Environment File Setup

Create a `.env` file in the `backend/` directory:

```env
# AI APIs
NVIDIA_API_KEY=your_nvidia_key
OPENROUTER_API_KEY=your_openrouter_key

# Job Search APIs
RAPIDAPI_KEY=your_rapidapi_key          # ⭐ Priority 1
ADZUNA_APP_ID=your_adzuna_app_id        # Priority 2
ADZUNA_APP_KEY=your_adzuna_app_key      # Priority 2
REED_API_KEY=your_reed_key              # Priority 3
USAJOBS_API_KEY=your_usajobs_key        # Priority 4
USAJOBS_USER_AGENT=PathFinderApp/1.0

# The Muse, RemoteOK, Arbeitnow - no keys needed ✅
```

---

## API Priority Ranking

| Rank | API | Jobs/Request | Quality | Coverage | Setup Time |
|------|-----|--------------|---------|----------|------------|
| 🥇 | **JSearch (RapidAPI)** | 8-12 | ⭐⭐⭐⭐⭐ | Global | 5 min |
| 🥈 | **The Muse** | 3-5 | ⭐⭐⭐⭐ | US Remote | 0 min ✅ |
| 🥉 | **RemoteOK** | 3-5 | ⭐⭐⭐⭐ | Global Remote | 0 min ✅ |
| 4 | **Adzuna** | 4-6 | ⭐⭐⭐⭐ | Multi-country | 10 min |
| 5 | **Arbeitnow** | 2-4 | ⭐⭐⭐ | Europe | 0 min ✅ |
| 6 | **Reed UK** | 2-3 | ⭐⭐⭐ | UK only | 10 min |
| 7 | **USAJobs** | 2-3 | ⭐⭐⭐ | US Gov | 15 min |

---

## Troubleshooting

### "Only getting 5 jobs"
- Add RapidAPI JSearch key (most important)
- This single API can fetch 8-12 jobs from Indeed/LinkedIn

### "API key not working"
- Check `.env` file is in `backend/` directory
- Restart the backend server after adding keys
- Verify key names match exactly (case-sensitive)

### "Rate limit exceeded"
- Free tiers are usually sufficient (250-2500/month)
- APIs are called in sequence, not all at once
- System automatically skips APIs without keys

---

## Cost Summary

| Setup | Monthly Cost | Jobs/Search | Best For |
|-------|--------------|-------------|----------|
| **Minimal** (free APIs only) | $0 | 5-8 | Testing |
| **Recommended** (+ RapidAPI) | $0 | 10-15 | Production |
| **Full** (all 7 APIs) | $0 | 20-30 | Enterprise |

**Note**: All recommended APIs have generous free tiers. You can serve thousands of users for $0/month.

---

## Support

- API Issues: Check `backend/services/web_job_scraper.py`
- Rate Limits: Each API has independent limits
- Questions: See individual API documentation links above

Happy job hunting! 🚀
