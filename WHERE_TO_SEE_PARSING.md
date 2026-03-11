# Where to See Parsing Results

After uploading a resume, you can see the parsed results in **3 places**:

---

## 🎯 Method 1: Frontend Dashboard (Best Visual Experience)

### Steps:
1. **Upload a Resume**
   - Go to: `http://localhost:5173/upload`
   - Upload a PDF or DOCX file
   - Click "Upload Resume"

2. **View Dashboard**
   - After upload, you'll be **automatically redirected** to `/dashboard`
   - Or manually navigate to: `http://localhost:5173/dashboard`

3. **See Parsed Data**
   The Dashboard displays:
   - ✅ **Name** (at the top)
   - ✅ **Extracted Skills** (as colored badges)
   - ✅ **Education** (degree information)
   - ✅ **Work Experience** (job descriptions)
   - ⏳ Skill Gap Analysis (coming in future modules)
   - ⏳ Job Recommendations (coming in future modules)
   - ⏳ Learning Path (coming in future modules)

---

## 🔧 Method 2: Swagger UI (Raw JSON Response)

### Steps:
1. **Open Swagger UI**
   - Go to: `http://localhost:8000/docs`

2. **Test Upload**
   - Find `POST /upload-resume`
   - Click "Try it out"
   - Upload a file
   - Click "Execute"

3. **See Response**
   - Scroll down to see the **Response body**
   - You'll see raw JSON like:
   ```json
   {
     "name": "John Doe",
     "skills": ["Python", "FastAPI", "PostgreSQL"],
     "education": ["B.Tech Computer Science"],
     "experience": ["Developed RESTful APIs using FastAPI"]
   }
   ```

---

## 💻 Method 3: Browser Developer Tools

### Steps:
1. **Open Browser Console**
   - Press `F12` or `Right-click → Inspect`
   - Go to **Console** tab

2. **Upload Resume**
   - Upload a file through the frontend

3. **Check Network Tab**
   - Go to **Network** tab
   - Find the `/upload-resume` request
   - Click on it
   - Go to **Response** tab
   - See the parsed JSON data

4. **Check localStorage**
   - In Console tab, type:
   ```javascript
   JSON.parse(localStorage.getItem('resumeData'))
   ```
   - This shows the stored parsed data

---

## 📊 Method 4: Python Test Script

### Steps:
1. **Run Test Script**
   ```bash
   cd backend
   py test_api.py path/to/your/resume.pdf
   ```

2. **See Output**
   - The script will print:
     - Health check status
     - Parsed resume data
     - Summary (name, skills count, education count, experience count)

---

## 🎨 Visual Guide: Dashboard Layout

```
┌─────────────────────────────────────────────────┐
│  Dashboard                                       │
│  Resume Analysis for: John Doe                  │
├─────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐           │
│  │ Extracted    │  │ Education    │           │
│  │ Skills       │  │              │           │
│  │ [Python]     │  │ B.Tech CS    │           │
│  │ [AWS]        │  │ M.S. SE      │           │
│  │ [SQL]        │  │              │           │
│  └──────────────┘  └──────────────┘           │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ Work         │  │ Skill Gap    │           │
│  │ Experience   │  │ Analysis     │           │
│  │ • Developed  │  │ (Coming soon)│           │
│  │   REST APIs  │  │              │           │
│  │ • Led team   │  │              │           │
│  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────┘
```

---

## ✅ Quick Test Checklist

- [ ] Upload a resume via frontend (`/upload`)
- [ ] Check Dashboard shows parsed data (`/dashboard`)
- [ ] Verify skills appear as badges
- [ ] Verify education is listed
- [ ] Verify experience is listed
- [ ] Check Swagger UI shows JSON response (`/docs`)
- [ ] Verify browser console shows no errors

---

## 🐛 Troubleshooting

### Dashboard shows "No resume data found"
- **Solution**: Upload a resume first, then check dashboard
- The data is stored in browser localStorage after upload

### Dashboard shows empty cards
- **Solution**: Check if your resume has extractable text
- Try a different resume format
- Check browser console for errors

### Want to see raw data?
- Use Swagger UI: `http://localhost:8000/docs`
- Or check browser localStorage in console

---

## 📝 Summary

**Best way to see parsing results:**
1. Upload resume → `http://localhost:5173/upload`
2. View Dashboard → `http://localhost:5173/dashboard` (auto-redirects after upload)
3. See all parsed data displayed beautifully!

**For developers:**
- Swagger UI: `http://localhost:8000/docs` (raw JSON)
- Browser Console: Check Network tab or localStorage
