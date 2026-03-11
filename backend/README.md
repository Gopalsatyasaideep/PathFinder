# PathFinder AI - Resume Parser Module

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Configure OpenRouter API (for Chatbot and Learning Path)

The chatbot and learning path features use OpenRouter's free API. You need to set up an API key:

1. **Get your API key:**
   - Visit https://openrouter.ai/keys
   - Sign up for a free account
   - Create an API key

2. **Set the environment variable:**
   
   **Windows (PowerShell):**
   ```powershell
   $env:OPENROUTER_API_KEY = "your-api-key-here"
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   set OPENROUTER_API_KEY=your-api-key-here
   ```
   
   **Linux/Mac:**
   ```bash
   export OPENROUTER_API_KEY=your-api-key-here
   ```
   
   **Or create a `.env` file in the backend directory:**
   ```
   OPENROUTER_API_KEY=your-api-key-here
   ```

   **Note:** If the API key is not set, the system will fall back to local models (FLAN-T5) or simple keyword-based responses.

### 4. Run the Server

```bash
# From the backend directory
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 5. API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoint

### POST /upload-resume

Upload a resume file (PDF or DOCX) and get parsed structured data.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (PDF or DOCX, max 5MB)

**Response:**
```json
{
  "success": true,
  "message": "Resume parsed successfully",
  "data": {
    "name": "Candidate Name",
    "skills": ["Python", "AWS", "SQL"],
    "education": ["B.Tech Computer Science"],
    "experience": ["Worked on cloud-based applications"]
  }
}
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── routers/
│   └── resume.py          # Resume upload endpoint
├── services/
│   └── resume_parser.py   # Core parsing logic
├── utils/
│   └── text_cleaner.py    # Text cleaning utilities
└── requirements.txt       # Python dependencies
```

## Testing

### Quick Test Methods

**1. Using Swagger UI (Recommended):**
- Visit `http://localhost:8000/docs`
- Click on `POST /upload-resume`
- Click "Try it out"
- Upload a PDF or DOCX file
- Click "Execute"

**2. Using Frontend:**
- Open `http://localhost:5173`
- Navigate to "Upload Resume"
- Upload a resume file
- View results on Dashboard

**3. Using Python Test Script:**
```bash
# Install requests if needed
py -m pip install requests

# Run test script
cd backend
py test_api.py path/to/your/resume.pdf
```

**4. Using cURL (PowerShell):**
```powershell
$file = Get-Item "path\to\resume.pdf"
Invoke-RestMethod -Uri http://localhost:8000/upload-resume -Method Post -InFile $file.FullName -ContentType "multipart/form-data"
```

For detailed testing instructions, see [TESTING.md](./TESTING.md)

## Notes

- The parser uses heuristic-based extraction methods
- Name extraction may not always be accurate
- Skills are matched against a predefined keyword list
- Education and experience extraction looks for common patterns
- All extraction methods are documented with their limitations
- spaCy is optional (handled gracefully if not available)
