# How to Run PathFinder AI

## Quick Start

### Option 1: Run Both Servers (Recommended)

**Terminal 1 - Backend (FastAPI):**
```powershell
cd backend
python main.py
```
Backend will run on: `http://localhost:8000`

**Terminal 2 - Frontend (React/Vite):**
```powershell
npm run dev
```
Frontend will run on: `http://localhost:5173`

### Option 2: Using PowerShell Scripts

**Start Backend:**
```powershell
cd backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python main.py"
```

**Start Frontend:**
```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"
```

## Access the Application

1. **Frontend UI**: Open your browser and go to `http://localhost:5173`
2. **Backend API Docs**: Visit `http://localhost:8000/docs` for Swagger UI
3. **Health Check**: `http://localhost:8000/health`

## Prerequisites

### Backend Requirements
- Python 3.10+ installed
- Dependencies installed: `pip install -r backend/requirements.txt`
- spaCy model: `python -m spacy download en_core_web_sm`
- (Optional) OpenRouter API key for chatbot/learning path: Set `OPENROUTER_API_KEY` environment variable

### Frontend Requirements
- Node.js installed
- Dependencies installed: `npm install`

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify Python dependencies are installed
- Check for error messages in the terminal

### Frontend won't start
- Check if port 5173 is already in use
- Verify Node.js dependencies: `npm install`
- Check for error messages in the terminal

### OpenRouter API Issues
- The system works without OpenRouter API key (uses fallbacks)
- For better chatbot/learning path, set `OPENROUTER_API_KEY` environment variable
- See `backend/OPENROUTER_SETUP.md` for details

## Stopping the Servers

Press `Ctrl+C` in each terminal window to stop the servers.

