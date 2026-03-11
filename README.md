# PathFinder AI - Career Guidance Platform

An AI‑powered resume analyzer and career guidance system with mock interviewing, job recommendations, and personalized learning paths.

---

## 📁 Project Structure

```
PathFinderAI/
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # Full-featured app (all routers)
│   ├── main_lightweight.py     # Lightweight app (NVIDIA API focus)
│   ├── routers/                # API endpoints (auth, resume, chat, etc.)
│   ├── services/               # Business logic (AI, job matching, parsing, etc.)
│   ├── models/                 # Pydantic/data models
│   ├── schemas/                # API request/response schemas
│   ├── utils/                  # Helpers (error handling, etc.)
│   ├── requirements.txt        # Python dependencies
│   ├── env.example             # Template for environment variables
│   └── ... (other backend files)
│
├── frontend/                   # React + Vite SPA
│   ├── src/                    # React components and pages
│   ├── public/                 # Static assets
│   ├── package.json            # JavaScript dependencies
│   ├── vite.config.js          # Vite build config
│   ├── tailwind.config.js      # TailwindCSS config
│   ├── .env.example            # Template for environment variables
│   └── ... (other frontend files)
│
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── ... (other root config/doc files)
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **MongoDB Atlas** account (or local MongoDB)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set environment variables
$env:MONGODB_URL = "mongodb+srv://gopal:YOUR_PASSWORD@cluster0.mgjmdpp.mongodb.net/pathfinder"
$env:SECRET_KEY = "your-secret-key"

# Run the server
python main_lightweight.py
# or: uvicorn main_lightweight:app --host 0.0.0.0 --port 8000
```

Server runs on `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install

# Set environment variables (create .env file):
# VITE_API_URL=http://localhost:8000

# Development server (hot reload)
npm run dev
# or: vite

# Build for production
npm run build
```

Frontend runs on `http://localhost:5173`  
Built output goes to `frontend/dist/`

---

## 🔐 Environment Variables

### Backend (`.env` or PowerShell `$env:*`)

```
MONGODB_URL=mongodb+srv://gopal:password@cluster0.../pathfinder
SECRET_KEY=your-secret-key-change-this
NVIDIA_API_KEY=your-nvidia-key (optional)
OPENROUTER_API_KEY=your-openrouter-key (optional)
ALLOWED_ORIGINS=http://localhost:5173,https://your-vercel-app.vercel.app
```

### Frontend (`.env.local` or `.env`)

```
VITE_API_URL=http://localhost:8000
```

---

## 🌐 Deployment

### MongoDB Atlas (Database)

1. Create a free cluster at https://www.mongodb.com/cloud/atlas
2. Add a database user and enable network access (`0.0.0.0/0` for demo)
3. Copy the connection string and use it as `MONGODB_URL`

### Render (Backend)

1. Create a **Web Service** connected to your GitHub repo
2. **Root directory:** `backend`
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `uvicorn main_lightweight:app --host 0.0.0.0 --port $PORT`
5. **Environment variables:**
   - `MONGODB_URL` → your Atlas connection string
   - `SECRET_KEY` → a random string
   - `ALLOWED_ORIGINS` → `https://<your-vercel-app>.vercel.app`
6. Deploy and note the backend URL (e.g., `https://backend-xxxxx.onrender.com`)

### Vercel (Frontend)

1. **Import** your GitHub repo
2. **Framework:** Vite
3. **Root directory:** `frontend`
4. **Build command:** `npm run build`
5. **Output directory:** `dist`
6. **Environment variables:**
   - `VITE_API_URL` → `https://backend-xxxxx.onrender.com`
7. Deploy and copy the Vercel URL back into Render's `ALLOWED_ORIGINS`

---

## 📚 Key Features

- ✅ **Resume Parsing** – Extract skills, experience, education from PDF/DOCX
- ✅ **AI Analysis** – NVIDIA Qwen 3 or OpenRouter APIs for intelligent insights
- ✅ **Job Recommendations** – Personalized job matches based on resume
- ✅ **Learning Paths** – AI-generated skill development roadmaps
- ✅ **Mock Interviews** – Practice with AI-driven interview scenarios
- ✅ **User History** – Track uploads, interviews, and progress
- ✅ **Authentication** – JWT-based login/signup with MongoDB
- ✅ **Chat Assistant** – RAG-powered career guidance chatbot

---

## 🛠 Development

### Backend API Routes

- `POST /auth/signup` – Create a new account
- `POST /auth/login` – Log in
- `POST /upload-resume` – Upload and parse a resume
- `POST /analyze-profile/quick-analysis` – Analyze extracted resume data
- `GET /job-recommendations` – Fetch job matches
- `GET /learning-path` – Generate learning roadmap
- `POST /chat` – Ask career questions
- `GET /user-history` – View user's history
- `POST /mock-interview/start` – Begin mock interview
- `GET /health` – Check API status

See `http://localhost:8000/docs` for full interactive API specification.

### Frontend Pages

- `/` – Landing page
- `/signup` – Create account
- `/login` – Sign in
- `/dashboard` – Overview and resume upload
- `/analyze` – Resume analysis results
- `/job-recommendations` – Job recommendations
- `/learning-path` – Learning path details
- `/chatbot` – AI career assistant
- `/mock-interview` – Interview practice
- `/history` – View past sessions

---

## 🧪 Testing

### Backend

```bash
cd backend
pytest test_*.py
# or individual tests:
python test_nvidia_integration.py
python test_user_history.py
```

### Frontend

```bash
cd frontend
npm run lint  # ESLint
```

---

## 📝 Notes

- The backend defaults to **lightweight mode** (`main_lightweight.py`) which is optimized for Render's free tier.
- The full backend (`main.py`) includes all routers but may require more resources.
- For local development, ensure MongoDB is accessible (Atlas or local instance).
- Vercel free tier sleeps after 15 minutes of inactivity; same with Render (wakes on request).
- Atlas free tier provides 512 MB storage—suitable for prototypes and demos.

---

## 🔗 Useful Links

- **NVIDIA API:** https://build.nvidia.com/explore/discover
- **OpenRouter:** https://openrouter.ai/keys
- **MongoDB Atlas:** https://www.mongodb.com/cloud/atlas
- **Render:** https://render.com
- **Vercel:** https://vercel.com

---

**Last Updated:** March 11, 2026
