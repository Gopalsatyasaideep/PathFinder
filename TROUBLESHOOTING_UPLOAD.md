# Troubleshooting: "Failed to upload resume" Error

## Quick Fixes

### 1. Check Backend is Running
```bash
# Check if backend is running
netstat -ano | findstr :8000

# If not running, start it:
cd backend
py main.py
```

### 2. Check Browser Console
- Press `F12` to open Developer Tools
- Go to **Console** tab
- Look for error messages
- Go to **Network** tab
- Try uploading again
- Click on the `/upload-resume` request
- Check the **Response** tab for error details

### 3. Common Issues & Solutions

#### Issue: "Cannot connect to server"
**Solution:**
- Make sure backend is running on `http://localhost:8000`
- Check if port 8000 is blocked by firewall
- Try accessing `http://localhost:8000/health` in browser

#### Issue: CORS Error
**Solution:**
- Backend CORS is already configured
- If still seeing CORS errors, check browser console
- Make sure you're accessing frontend from `http://localhost:5173`

#### Issue: "File size exceeds maximum"
**Solution:**
- Maximum file size is 5MB
- Compress your PDF or use a smaller file

#### Issue: "Invalid file type"
**Solution:**
- Only PDF and DOCX files are supported
- Make sure file extension is `.pdf` or `.docx` (case-insensitive)

#### Issue: "Error parsing resume"
**Solution:**
- File might be corrupted or password-protected
- Try a different resume file
- Make sure the file has extractable text (not just images)

## Testing Steps

### Step 1: Test Backend Directly
```powershell
# Test health endpoint
Invoke-WebRequest -Uri http://localhost:8000/health

# Test upload (replace path)
$file = Get-Item "C:\path\to\resume.pdf"
Invoke-RestMethod -Uri http://localhost:8000/upload-resume -Method Post -InFile $file.FullName -ContentType "multipart/form-data"
```

### Step 2: Test via Swagger UI
1. Go to: `http://localhost:8000/docs`
2. Find `POST /upload-resume`
3. Click "Try it out"
4. Upload a file
5. Check the response

### Step 3: Check Frontend Console
1. Open browser DevTools (`F12`)
2. Go to **Console** tab
3. Upload a file
4. Look for error messages
5. Check **Network** tab for request details

## Debug Information

The improved error handling now shows:
- **Connection errors**: "Cannot connect to server..."
- **Server errors**: Actual error message from backend
- **Network errors**: Detailed network failure info

Check the browser console for full error details!
