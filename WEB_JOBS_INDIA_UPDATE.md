# Web Jobs India Priority & No ATS Scoring Update

## Changes Made

### 1. **Removed NVIDIA ATS Comparison for Web Jobs**
   - Web jobs fetched from APIs are **NOT** sent to NVIDIA API for ATS comparison
   - They are displayed directly as raw job recommendations
   - Only match score (based on skills and title) is calculated locally
   - This improves performance and reduces API costs

### 2. **India Job Prioritization**
   - Added `prioritize_india` parameter (default: `True`) to web job search
   - India-based jobs are automatically sorted to the top of results
   - Other location jobs are still included but appear after India jobs
   
### 3. **India Location Detection**
   - Jobs are identified as India-based if location contains:
     - Country: `india`, `in`
     - Cities: `bangalore`, `bengaluru`, `mumbai`, `delhi`, `hyderabad`, `pune`, `chennai`, `kolkata`, `ahmedabad`, `noida`, `gurugram`, `gurgaon`, `chandigarh`, `jaipur`, `kochi`, `indore`

### 4. **Country-Specific API Usage**
   - **Reed UK**: Only used for UK (`uk`, `gb`) job searches
   - **USAJobs**: Only used for US (`us`) job searches
   - This prevents irrelevant job sources from cluttering results

## API Endpoints Updated

### `/web-jobs/search`
```
GET /web-jobs/search?query=Software%20Engineer&location=India&prioritize_india=true
```

**New Parameter:**
- `prioritize_india` (boolean, default: true) - Prioritize India-based jobs in results

**Behavior:**
- Fetches jobs from 7+ APIs
- Filters and prioritizes India jobs first
- Returns raw job data with local match scores
- **NO ATS comparison with NVIDIA**

### `/web-jobs/recommended`
```
GET /web-jobs/recommended?target_role=Full%20Stack%20Developer&location=Bangalore&prioritize_india=true
```

**New Parameter:**
- `prioritize_india` (boolean, default: true) - Prioritize India-based jobs in results

**Behavior:**
- Personalized recommendations based on skills
- India jobs appear first when enabled
- **NO NVIDIA API calls**

## Benefits

1. **Faster Response Times**: No NVIDIA API calls means quicker results
2. **Cost Reduction**: Saves on NVIDIA API usage costs
3. **Better India Job Discovery**: India jobs are prominently featured
4. **Global Coverage**: Still includes jobs from other countries
5. **Simplified Flow**: Direct display without ATS scoring overhead

## Example Output

```json
{
  "query": "Software Engineer",
  "location": "India",
  "web_jobs": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Corp India",
      "location": "Bangalore, India",
      "match_score": 85.5,
      "source": "JSearch (Indeed/LinkedIn)"
    },
    {
      "title": "Full Stack Developer",
      "company": "Startup Hub",
      "location": "Mumbai, India",
      "match_score": 78.0,
      "source": "Adzuna"
    },
    {
      "title": "Software Developer",
      "company": "Global Tech",
      "location": "Remote",
      "match_score": 72.0,
      "source": "RemoteOK"
    }
  ],
  "total_results": 15
}
```

## Testing

To test the changes, start the backend server and try:

```bash
# Test India prioritization
curl "http://localhost:8000/web-jobs/search?query=Software%20Engineer&location=India&prioritize_india=true"

# Test without India prioritization
curl "http://localhost:8000/web-jobs/search?query=Software%20Engineer&location=remote&prioritize_india=false"
```

## Frontend Integration

Update your frontend to pass `prioritize_india` parameter:

```javascript
const response = await fetch(
  `/web-jobs/search?query=${query}&location=${location}&prioritize_india=true`
);
```

---

**Last Updated:** January 26, 2026
