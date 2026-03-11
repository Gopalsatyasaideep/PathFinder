# Testing Guide - Module 2: Resume Upload & Parsing

## Prerequisites

1. ✅ Backend server running on `http://localhost:8000`
2. ✅ Frontend running on `http://localhost:5173`
3. ✅ Sample resume files (PDF or DOCX format)

---

## Method 1: Using Swagger UI (Easiest)

### Steps:

1. **Open Swagger UI**
   - Navigate to: `http://localhost:8000/docs`
   - You'll see an interactive API documentation interface

2. **Test the Upload Endpoint**
   - Find the `POST /upload-resume` endpoint
   - Click on it to expand
   - Click "Try it out" button
   - Click "Choose File" and select a PDF or DOCX resume
   - Click "Execute"

3. **Check Response**
   - You should see a response with status `200 OK`
   - Response body will contain:
     ```json
     {
       "name": "Candidate Name",
       "skills": ["Python", "AWS", "SQL"],
       "education": ["B.Tech Computer Science"],
       "experience": ["Worked on cloud-based applications"]
     }
     ```

---

## Method 2: Using Frontend (User-Friendly)

### Steps:

1. **Open Frontend**
   - Navigate to: `http://localhost:5173`
   - You should see the landing page

2. **Navigate to Upload Page**
   - Click "Upload Resume" button or navigate to `/upload`
   - You'll see a file upload interface

3. **Upload a Resume**
   - Click the upload area or drag & drop a PDF/DOCX file
   - Select your resume file (max 5MB)
   - Click "Upload Resume" button

4. **View Results**
   - After successful upload, you'll be redirected to Dashboard (`/dashboard`)
   - The dashboard will display:
     - Extracted Skills
     - Skill Gap Analysis
     - Recommended Job Roles
     - Learning Path

---

## Method 3: Using cURL (Command Line)

### Test Health Endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","service":"PathFinder AI Resume Parser"}
```

### Test Upload Endpoint:
```bash
curl -X POST "http://localhost:8000/upload-resume" \
  -F "file=@path/to/your/resume.pdf"
```

**Windows PowerShell:**
```powershell
$filePath = "C:\path\to\your\resume.pdf"
$uri = "http://localhost:8000/upload-resume"
Invoke-RestMethod -Uri $uri -Method Post -InFile $filePath -ContentType "multipart/form-data"
```

---

## Method 4: Using Python Script

Create a test script to programmatically test the API:

```python
import requests

# Test health endpoint
response = requests.get("http://localhost:8000/health")
print("Health Check:", response.json())

# Test upload endpoint
with open("path/to/resume.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/upload-resume", files=files)
    print("Upload Response:", response.json())
```

---

## Expected Test Results

### ✅ Successful Upload Response:
```json
{
  "name": "John Doe",
  "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "education": [
    "B.Tech Computer Science Engineering",
    "Master of Science in Software Engineering"
  ],
  "experience": [
    "Developed RESTful APIs using FastAPI",
    "Worked on cloud-based microservices architecture",
    "Led a team of 5 developers"
  ]
}
```

### ❌ Error Responses:

**Invalid File Type:**
```json
{
  "detail": "Invalid file type. Allowed types: PDF, DOCX"
}
```

**File Too Large:**
```json
{
  "detail": "File size exceeds maximum allowed size of 5.0MB"
}
```

**Parsing Error:**
```json
{
  "detail": "Error parsing resume: No text could be extracted from the resume file"
}
```

---

## Test Cases Checklist

### Basic Functionality:
- [ ] Health endpoint returns healthy status
- [ ] Root endpoint returns API information
- [ ] Upload PDF resume successfully
- [ ] Upload DOCX resume successfully
- [ ] Receive parsed data in correct JSON format

### Error Handling:
- [ ] Reject non-PDF/DOCX files
- [ ] Reject files larger than 5MB
- [ ] Handle corrupted/invalid files gracefully
- [ ] Return appropriate error messages

### Data Extraction:
- [ ] Name is extracted (if present in resume)
- [ ] Skills are extracted correctly
- [ ] Education information is extracted
- [ ] Experience descriptions are extracted
- [ ] Empty/null values handled gracefully

### Frontend Integration:
- [ ] File upload UI works
- [ ] Drag & drop functionality works
- [ ] Loading indicator shows during upload
- [ ] Success redirects to dashboard
- [ ] Error messages display correctly
- [ ] Dashboard displays parsed data

---

## Sample Test Files

### Good Test Cases:
1. **Standard Resume** - Well-formatted PDF with clear sections
2. **DOCX Resume** - Microsoft Word document
3. **Resume with Skills Section** - Should extract skills easily
4. **Resume with Education** - Should extract degree information
5. **Resume with Experience** - Should extract work history

### Edge Cases:
1. **Very Short Resume** - Minimal content
2. **Very Long Resume** - Multiple pages
3. **Resume with Images** - Text extraction may vary
4. **Scanned PDF** - May not extract text (if not OCR'd)

---

## Troubleshooting

### Backend Not Starting:
```bash
# Check if port 8000 is already in use
netstat -ano | findstr :8000

# Kill process if needed, then restart
cd backend
py main.py
```

### Import Errors:
```bash
# Make sure you're in the backend directory
cd backend
py main.py
```

### CORS Errors:
- Backend CORS is configured to allow all origins
- If issues persist, check browser console for specific errors

### File Upload Fails:
- Check file size (must be < 5MB)
- Check file format (PDF or DOCX only)
- Check backend logs for error messages

---

## Quick Test Commands

**Windows PowerShell:**
```powershell
# Health check
Invoke-RestMethod -Uri http://localhost:8000/health

# Upload test (replace path)
$file = Get-Item "C:\path\to\resume.pdf"
Invoke-RestMethod -Uri http://localhost:8000/upload-resume -Method Post -InFile $file.FullName -ContentType "multipart/form-data"
```

**Linux/Mac:**
```bash
# Health check
curl http://localhost:8000/health

# Upload test
curl -X POST http://localhost:8000/upload-resume -F "file=@/path/to/resume.pdf"
```

---

## Next Steps After Testing

Once Module 2 is tested and working:
1. ✅ Resume upload works
2. ✅ Text extraction works
3. ✅ Data parsing works
4. ✅ Frontend integration works

You can proceed to:
- Module 3: RAG Pipeline Integration
- Module 4: Job Matching Algorithm
- Module 5: Learning Path Generation
