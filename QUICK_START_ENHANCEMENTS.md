# Quick Start - Test the Enhancements

## Start Backend

```bash
cd backend
python main.py
```

## Start Frontend (new terminal)

```bash
npm run dev
```

## Test the Features

### 1. Test Personalized Recommendations

Upload different resumes with different skills:

**Data Science Resume**:
- Skills: Python, Machine Learning, TensorFlow, Pandas, SQL
- Expected: Data Scientist, ML Engineer jobs

**Frontend Resume**:
- Skills: React, JavaScript, HTML, CSS, TypeScript
- Expected: Frontend Developer, React Developer jobs

**DevOps Resume**:
- Skills: Docker, Kubernetes, AWS, Jenkins, Terraform
- Expected: DevOps Engineer, Cloud Engineer jobs

### 2. Test API Coverage

Visit: http://localhost:8000/docs

Try this endpoint:
```
GET /web-jobs/search
```

Parameters:
- query: "Python Developer"
- location: "India"
- max_results: 20
- prioritize_india: true

Expected: Jobs from multiple sources (Remotive, Jobicy, IndianAPI, RemoteOK, etc.)

### 3. Check Console Logs

Look for:
```
🎯 Auto-detected target role: [Role Name]
✅ Found X jobs from Remotive
✅ Found X jobs from Jobicy
✅ Found X jobs from IndianAPI
✅ Found X jobs from RemoteOK
```

## Quick API Test (Backend must be running)

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/web-jobs/search?query=Developer&location=India&max_results=20" | ConvertFrom-Json | ConvertTo-Json
```

### Or use browser
```
http://localhost:8000/web-jobs/search?query=Developer&location=India&max_results=20
```

## Success Indicators

✅ Different resumes get different job titles  
✅ Jobs match the resume's skills  
✅ Console shows different detected roles  
✅ 30-50+ jobs returned from multiple APIs  
✅ India jobs prioritized when requested  

## Troubleshooting

### No jobs returned
- Check backend is running on port 8000
- Check internet connection (APIs need access)
- Check console for API errors

### Same jobs for all resumes
- Clear browser localStorage
- Hard refresh (Ctrl+Shift+R)
- Check backend logs for role detection

### API errors
- Some APIs may be temporarily down (normal)
- System uses multiple APIs for redundancy
- At least 7 free APIs should work without keys

## Documentation

- `JOB_PERSONALIZATION_FIX.md` - Personalization details
- `JOB_APIS_INTEGRATED.md` - All 12+ APIs documented
- `COMPLETE_JOB_ENHANCEMENT.md` - Full overview
- `TEST_PERSONALIZATION.md` - Detailed testing guide

Enjoy the enhanced job recommendations! 🎉
