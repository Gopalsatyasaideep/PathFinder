# Troubleshooting Job Recommendations

## Issue: Job Recommendations Not Showing

### Fixed Issues

1. **API Key Configuration** ✅
   - **Problem**: API key was incorrectly placed in `os.getenv()` as the variable name
   - **Fix**: API key is now correctly set in `DEFAULT_API_KEY` variable
   - **Location**: `backend/services/openrouter_client.py` line 39

2. **AI Recommender Initialization** ✅
   - **Problem**: AI recommender might not initialize if API key was wrong
   - **Fix**: Added better error handling and logging
   - **Location**: `backend/services/orchestrator.py` and `backend/services/ai_job_recommender.py`

3. **Resume Data Handling** ✅
   - **Problem**: AI recommendations only worked if full resume_data was provided
   - **Fix**: Now works with just skills if resume_data is minimal
   - **Location**: `backend/services/orchestrator.py` line 220-240

## How to Verify It's Working

### 1. Check API Key is Set
Open `backend/services/openrouter_client.py` and verify:
```python
DEFAULT_API_KEY = "sk-or-v1-..."  # Should have your API key
```

### 2. Check Backend Logs
When you request job recommendations, you should see:
```
Generating AI job recommendations for X skills...
Received response from OpenRouter (length: XXX)
Parsed X recommendations from JSON
Returning X formatted recommendations
```

### 3. Test the API Directly
```bash
# Test with curl (PowerShell)
$resumeData = @{
    skills = @("Python", "SQL", "AWS")
    experience = @("Software Developer")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/job-recommendations?skills=Python,SQL,AWS" -Method Post -Body $resumeData -ContentType "application/json"
```

### 4. Check Frontend Console
Open browser DevTools (F12) and check:
- Network tab: Look for `/job-recommendations` request
- Console tab: Check for any errors
- Response should have `recommended_jobs` array

## Common Issues

### Issue: "OpenRouter API key is required"
**Solution**: Set `DEFAULT_API_KEY` in `openrouter_client.py`

### Issue: Empty recommendations array
**Possible causes**:
1. API key is invalid or expired
2. OpenRouter API is down
3. JSON parsing failed (check backend logs)
4. No skills provided in request

**Solution**: Check backend terminal for error messages

### Issue: Still showing only 3 jobs
**Solution**: Make sure you're using POST request with resume data, not GET

## Debug Steps

1. **Check API Key**:
   ```python
   # In Python console
   from services.openrouter_client import OpenRouterClient
   client = OpenRouterClient()
   print(f"API Key set: {bool(client.api_key)}")
   ```

2. **Test AI Recommender**:
   ```python
   from services.ai_job_recommender import AIJobRecommender
   recommender = AIJobRecommender()
   result = recommender.generate_recommendations({"skills": ["Python", "SQL"]}, top_n=5)
   print(result)
   ```

3. **Check Backend Response**:
   - Visit `http://localhost:8000/docs`
   - Try the `/job-recommendations` endpoint
   - Check the response format

## Expected Response Format

```json
{
  "recommended_jobs": [
    {
      "job_title": "Software Developer",
      "match_score": 85,
      "matched_skills": ["Python", "SQL"],
      "missing_skills": ["Docker"],
      "reason": "Your skills align well...",
      "description": "Job description..."
    }
  ],
  "message": "AI-generated personalized recommendations"
}
```

