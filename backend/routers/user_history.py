"""
User History Router - Stores and retrieves user's resume analyses, chat history, and job recommendations
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import os
import jwt

# Initialize router
router = APIRouter(prefix="/user-history", tags=["user-history"])

# MongoDB connection
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "pathfinder"
CHAT_HISTORY_COLLECTION = "chat_history"
RESUME_ANALYSES_COLLECTION = "resume_analyses"
JOB_RECOMMENDATIONS_COLLECTION = "job_recommendations"
LEARNING_PATHS_COLLECTION = "learning_paths"

# JWT config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# Database helper
def get_db():
    """Get MongoDB database connection"""
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    return db

# Get user ID from token
def get_user_id_from_token(authorization: str) -> str:
    """Extract user ID from JWT token"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Models
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str

class SaveChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_name: Optional[str] = None
    user_id: str

class ResumeAnalysisRequest(BaseModel):
    resume_data: Dict[str, Any]
    analysis_results: Dict[str, Any]
    file_name: Optional[str] = None
    user_id: str

class JobRecommendationRequest(BaseModel):
    jobs: List[Dict[str, Any]]
    resume_id: Optional[str] = None
    user_id: str

# ===== CHAT HISTORY ENDPOINTS =====

@router.post("/chat/save")
async def save_chat_history(chat_data: SaveChatRequest):
    """Save chat conversation for user"""
    try:
        user_id = chat_data.user_id
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        db = get_db()
        chat_collection = db[CHAT_HISTORY_COLLECTION]
        
        chat_doc = {
            "user_id": user_id,
            "messages": [msg.dict() for msg in chat_data.messages],
            "session_name": chat_data.session_name or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = chat_collection.insert_one(chat_doc)
        
        return {
            "success": True,
            "chat_id": str(result.inserted_id),
            "message": "Chat history saved successfully"
        }
    
    except Exception as e:
        print(f"Error saving chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/list")
async def get_chat_history(user_id: str):
    """Get all chat sessions for a user"""
    try:
        db = get_db()
        chat_collection = db[CHAT_HISTORY_COLLECTION]
        
        chats = list(chat_collection.find(
            {"user_id": user_id}
        ).sort("updated_at", -1).limit(50))
        
        # Convert ObjectId to string
        for chat in chats:
            chat["_id"] = str(chat["_id"])
        
        return {
            "success": True,
            "chats": chats
        }
    
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/{chat_id}")
async def get_chat_by_id(chat_id: str, user_id: str):
    """Get specific chat session"""
    try:
        db = get_db()
        chat_collection = db[CHAT_HISTORY_COLLECTION]
        
        chat = chat_collection.find_one({
            "_id": ObjectId(chat_id),
            "user_id": user_id
        })
        
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        chat["_id"] = str(chat["_id"])
        
        return {
            "success": True,
            "chat": chat
        }
    
    except Exception as e:
        print(f"Error fetching chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/chat/{chat_id}")
async def update_chat_history(chat_id: str, chat_data: SaveChatRequest):
    """Update existing chat session"""
    try:
        user_id = chat_data.user_id
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
            
        db = get_db()
        chat_collection = db[CHAT_HISTORY_COLLECTION]
        
        result = chat_collection.update_one(
            {"_id": ObjectId(chat_id), "user_id": user_id},
            {
                "$set": {
                    "messages": [msg.dict() for msg in chat_data.messages],
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return {
            "success": True,
            "message": "Chat updated successfully"
        }
    
    except Exception as e:
        print(f"Error updating chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str, user_id: str):
    """Delete a chat session"""
    try:
        db = get_db()
        chat_collection = db[CHAT_HISTORY_COLLECTION]
        
        result = chat_collection.delete_one({
            "_id": ObjectId(chat_id),
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return {
            "success": True,
            "message": "Chat deleted successfully"
        }
    
    except Exception as e:
        print(f"Error deleting chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== RESUME ANALYSIS HISTORY =====

@router.post("/resume/save")
async def save_resume_analysis(analysis: ResumeAnalysisRequest):
    """Save resume analysis for user"""
    try:
        user_id = analysis.user_id
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
            
        db = get_db()
        resume_collection = db[RESUME_ANALYSES_COLLECTION]
        
        analysis_doc = {
            "user_id": user_id,
            "resume_data": analysis.resume_data,
            "analysis_results": analysis.analysis_results,
            "file_name": analysis.file_name,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = resume_collection.insert_one(analysis_doc)
        
        return {
            "success": True,
            "analysis_id": str(result.inserted_id),
            "message": "Resume analysis saved successfully"
        }
    
    except Exception as e:
        print(f"Error saving resume analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resume/list")
async def get_resume_analyses(user_id: str):
    """Get all resume analyses for a user"""
    try:
        db = get_db()
        resume_collection = db[RESUME_ANALYSES_COLLECTION]
        
        analyses = list(resume_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(50))
        
        for analysis in analyses:
            analysis["_id"] = str(analysis["_id"])
        
        return {
            "success": True,
            "analyses": analyses
        }
    
    except Exception as e:
        print(f"Error fetching resume analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resume/{analysis_id}")
async def get_resume_analysis(analysis_id: str, user_id: str):
    """Get specific resume analysis"""
    try:
        db = get_db()
        resume_collection = db[RESUME_ANALYSES_COLLECTION]
        
        analysis = resume_collection.find_one({
            "_id": ObjectId(analysis_id),
            "user_id": user_id
        })
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis["_id"] = str(analysis["_id"])
        
        return {
            "success": True,
            "analysis": analysis
        }
    
    except Exception as e:
        print(f"Error fetching analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== JOB RECOMMENDATIONS HISTORY =====

@router.post("/jobs/save")
async def save_job_recommendations(job_data: JobRecommendationRequest):
    """Save job recommendations for user"""
    try:
        user_id = job_data.user_id
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
            
        db = get_db()
        jobs_collection = db[JOB_RECOMMENDATIONS_COLLECTION]
        
        job_doc = {
            "user_id": user_id,
            "jobs": job_data.jobs,
            "resume_id": job_data.resume_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = jobs_collection.insert_one(job_doc)
        
        return {
            "success": True,
            "recommendation_id": str(result.inserted_id),
            "message": "Job recommendations saved successfully"
        }
    
    except Exception as e:
        print(f"Error saving job recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/list")
async def get_job_recommendations(user_id: str):
    """Get all job recommendations for a user"""
    try:
        db = get_db()
        jobs_collection = db[JOB_RECOMMENDATIONS_COLLECTION]
        
        recommendations = list(jobs_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(50))
        
        for rec in recommendations:
            rec["_id"] = str(rec["_id"])
        
        return {
            "success": True,
            "recommendations": recommendations
        }
    
    except Exception as e:
        print(f"Error fetching job recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{recommendation_id}")
async def get_job_recommendation(recommendation_id: str, user_id: str):
    """Get specific job recommendation"""
    try:
        db = get_db()
        jobs_collection = db[JOB_RECOMMENDATIONS_COLLECTION]
        
        recommendation = jobs_collection.find_one({
            "_id": ObjectId(recommendation_id),
            "user_id": user_id
        })
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        recommendation["_id"] = str(recommendation["_id"])
        
        return {
            "success": True,
            "recommendation": recommendation
        }
    
    except Exception as e:
        print(f"Error fetching recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== DASHBOARD SUMMARY =====

@router.get("/summary")
async def get_user_history_summary(user_id: str):
    """Get summary of all user activities"""
    try:
        db = get_db()
        
        chat_count = db[CHAT_HISTORY_COLLECTION].count_documents({"user_id": user_id})
        resume_count = db[RESUME_ANALYSES_COLLECTION].count_documents({"user_id": user_id})
        job_count = db[JOB_RECOMMENDATIONS_COLLECTION].count_documents({"user_id": user_id})
        
        # Get latest items
        latest_chat = db[CHAT_HISTORY_COLLECTION].find_one(
            {"user_id": user_id},
            sort=[("updated_at", -1)]
        )
        latest_resume = db[RESUME_ANALYSES_COLLECTION].find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        latest_jobs = db[JOB_RECOMMENDATIONS_COLLECTION].find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        return {
            "success": True,
            "summary": {
                "total_chats": chat_count,
                "total_resume_analyses": resume_count,
                "total_job_recommendations": job_count,
                "latest_chat_date": latest_chat["updated_at"] if latest_chat else None,
                "latest_resume_date": latest_resume["created_at"] if latest_resume else None,
                "latest_jobs_date": latest_jobs["created_at"] if latest_jobs else None
            }
        }
    
    except Exception as e:
        print(f"Error fetching summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== LEARNING PATH ENDPOINTS =====

class LearningPathGenerateRequest(BaseModel):
    current_skills: Optional[str] = None
    target_role: str
    learning_goal: str
    time_commitment: str = "5-10"

class LearningPathSaveRequest(BaseModel):
    target_role: str
    learning_goal: str
    current_skills: Optional[str] = None
    time_commitment: str = "5-10"
    path: List[Dict[str, Any]]
    user_id: str

@router.post("/learning-path/generate")
async def generate_learning_path(request: LearningPathGenerateRequest):
    """Generate AI-powered personalized learning path with character dialogues"""
    try:
        from services.nvidia_client import get_nvidia_client
        from services.openrouter_client import get_openrouter_client
        
        # Get AI client
        nvidia_client = get_nvidia_client()
        openrouter_client = get_openrouter_client()
        
        if not nvidia_client and not openrouter_client:
            return generate_basic_learning_path(request)
        
        # Use AI to generate personalized path
        client = nvidia_client if nvidia_client else openrouter_client
        
        prompt = f"""You are an expert AI career mentor creating a premium, animated learning path presentation.

STUDENT PROFILE:
- Target Role: {request.target_role}
- Current Skills: {request.current_skills or 'Beginner - no prior experience'}
- Learning Goal: {request.learning_goal}
- Available Time: {request.time_commitment} hours per week

YOUR TASK:
Generate a comprehensive, step-by-step learning roadmap with exactly 7 phases.
Each phase will be presented by an animated AI character who "speaks" to the student.

For EACH phase, you MUST provide ALL of the following fields:

1. "title" - Clear, catchy phase name (e.g., "Mastering the Fundamentals")
2. "description" - Detailed 3-4 sentence explanation of what will be learned and why it matters
3. "duration" - Estimated time (e.g., "2-3 weeks")
4. "difficulty" - One of: "Beginner", "Intermediate", "Advanced"
5. "phase" - Category label (e.g., "Foundation", "Core Skills", "Advanced", "Specialization", "Capstone")
6. "resources" - Array of 4 specific learning resources, each as {{"title": "...", "url": "...", "type": "course"}}
7. "outcome" - One sentence: what the student can DO after completing this phase
8. "key_concepts" - Array of 4-6 core concepts/technologies covered (short strings)
9. "projects" - Array of 2 hands-on project ideas, each as {{"name": "...", "description": "..."}}
10. "character_dialogue" - THIS IS CRITICAL. Write 3-4 sentences as if you are a friendly, motivational AI mentor speaking DIRECTLY to the student. Use second person ("you"). Be encouraging, specific, and educational. Reference the actual skills being taught. Make it feel personal and alive. Each phase should have unique, contextual dialogue.

CRITICAL RULES:
- Return ONLY a valid JSON array. No markdown, no code fences, no explanation.
- Every phase MUST include ALL 10 fields listed above.
- character_dialogue must be natural, warm, and motivational - like a real mentor speaking.
- Resources should reference real platforms (freeCodeCamp, Udemy, Coursera, MDN, YouTube channels, etc.).
- Tailor everything specifically to the target role of "{request.target_role}".
- Make the path progressive: start easy, escalate to advanced.
- The final phase should be a capstone/portfolio project that combines all learned skills.
"""
        
        print(f"🎓 Generating enhanced learning path for: {request.target_role}")
        print(f"   Skills: {request.current_skills or 'Beginner'}")
        print(f"   Goal: {request.learning_goal}")
        
        # Call AI service — use generate_text (NOT complete!)
        response = client.generate_text(prompt, max_tokens=4096, temperature=0.4)
        
        print(f"🎓 AI Response length: {len(response)} chars")
        
        # Parse AI response — robust JSON extraction
        import json
        import re
        
        # Clean markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith('```'):
            parts = cleaned.split('```')
            if len(parts) >= 2:
                cleaned = parts[1]
                if cleaned.startswith('json'):
                    cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        
        # Try to extract JSON array
        json_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if json_match:
            learning_path = json.loads(json_match.group())
        else:
            print(f"⚠️ Could not extract JSON array from AI response")
            return generate_basic_learning_path(request)
        
        # Validate and ensure all fields exist
        required_fields = ['title', 'description', 'duration', 'difficulty', 'phase', 'resources', 'character_dialogue']
        for i, step in enumerate(learning_path):
            for field in required_fields:
                if field not in step:
                    step[field] = "" if field != 'resources' else []
            step.setdefault('outcome', f"Complete {step.get('title', f'Phase {i+1}')}")
            step.setdefault('key_concepts', [])
            step.setdefault('projects', [])
        
        print(f"✅ Generated {len(learning_path)} phases with character dialogues")
        
        return {
            "success": True,
            "learning_path": learning_path,
            "target_role": request.target_role,
            "total_phases": len(learning_path)
        }
    
    except Exception as e:
        print(f"❌ Error generating learning path: {e}")
        import traceback
        traceback.print_exc()
        return generate_basic_learning_path(request)

def generate_basic_learning_path(request: LearningPathGenerateRequest):
    """Generate a basic learning path without AI — includes character_dialogue for the animated frontend"""
    role_paths = {
        "Full Stack Developer": [
            {
                "title": "HTML & CSS Basics",
                "description": "Learn how web pages are structured with HTML and beautifully styled with CSS. This is the foundation of everything on the web.",
                "duration": "2 weeks",
                "difficulty": "Beginner",
                "phase": "Foundation",
                "resources": [{"title": "freeCodeCamp HTML/CSS", "url": "https://freecodecamp.org", "type": "course"}, {"title": "MDN Web Docs", "url": "https://developer.mozilla.org", "type": "tutorial"}],
                "outcome": "Build responsive, well-structured web pages from scratch",
                "key_concepts": ["HTML5 Semantic Elements", "CSS Flexbox", "CSS Grid", "Responsive Design"],
                "projects": [{"name": "Personal Portfolio", "description": "Build your own portfolio website with responsive design"}, {"name": "Landing Page Clone", "description": "Recreate a popular website's landing page"}],
                "character_dialogue": "Welcome aboard! 🎉 Let's start with the building blocks of the web — HTML and CSS. Think of HTML as the skeleton and CSS as the outfit. By the end of this phase, you'll be crafting beautiful web pages from scratch!"
            },
            {
                "title": "JavaScript Fundamentals",
                "description": "Master the programming language of the web. JavaScript makes pages interactive and dynamic — it's the most important language for web development.",
                "duration": "3 weeks",
                "difficulty": "Beginner",
                "phase": "Foundation",
                "resources": [{"title": "JavaScript.info", "url": "https://javascript.info", "type": "tutorial"}, {"title": "Eloquent JavaScript", "url": "https://eloquentjavascript.net", "type": "book"}],
                "outcome": "Write interactive JavaScript programs and manipulate the DOM",
                "key_concepts": ["Variables & Types", "Functions & Closures", "DOM Manipulation", "Async/Await", "ES6+ Features"],
                "projects": [{"name": "Interactive Quiz App", "description": "Build a quiz app with scoring and timer"}, {"name": "Todo List", "description": "Create a fully functional todo application"}],
                "character_dialogue": "Now we're getting to the fun part — JavaScript! This is what makes websites come alive. Don't worry about the learning curve — once you get the hang of functions and DOM manipulation, you'll feel like a wizard! ✨"
            },
            {
                "title": "React.js Framework",
                "description": "Learn the most popular frontend framework used by companies like Meta, Netflix, and Airbnb. React lets you build fast, component-based user interfaces.",
                "duration": "4 weeks",
                "difficulty": "Intermediate",
                "phase": "Frontend",
                "resources": [{"title": "React Official Docs", "url": "https://react.dev", "type": "tutorial"}, {"title": "Full React Course on Udemy", "url": "https://udemy.com", "type": "course"}],
                "outcome": "Build single-page applications with React components, state, and hooks",
                "key_concepts": ["Components & JSX", "State & Props", "React Hooks", "React Router", "Context API"],
                "projects": [{"name": "Movie Search App", "description": "Build a movie search app using an external API"}, {"name": "E-commerce Product Page", "description": "Create a product listing with cart functionality"}],
                "character_dialogue": "React time! 🚀 This is the framework that powers Instagram, Facebook, and thousands of other apps. Once you learn to think in components, you'll be building UIs 10x faster. Let's dive in!"
            },
            {
                "title": "Node.js & Express",
                "description": "Take your JavaScript skills to the server-side. Node.js and Express let you build powerful REST APIs and backend services.",
                "duration": "3 weeks",
                "difficulty": "Intermediate",
                "phase": "Backend",
                "resources": [{"title": "Node.js Docs", "url": "https://nodejs.org/docs", "type": "tutorial"}, {"title": "Express.js Guide", "url": "https://expressjs.com", "type": "tutorial"}],
                "outcome": "Build RESTful APIs with authentication and middleware",
                "key_concepts": ["Node.js Runtime", "Express Routing", "Middleware", "REST APIs", "Authentication"],
                "projects": [{"name": "Blog API", "description": "Build a REST API for a blog with CRUD operations"}, {"name": "Auth System", "description": "Implement JWT authentication from scratch"}],
                "character_dialogue": "You've conquered the frontend — now let's build the engine behind it! 💪 Node.js lets you use JavaScript on the server too. By the end of this phase, you'll be building real APIs that your React apps can talk to!"
            },
            {
                "title": "Databases (MongoDB/PostgreSQL)",
                "description": "Learn how to store, query, and manage data. Understanding databases is essential for any full-stack developer.",
                "duration": "3 weeks",
                "difficulty": "Intermediate",
                "phase": "Backend",
                "resources": [{"title": "MongoDB University", "url": "https://university.mongodb.com", "type": "course"}, {"title": "PostgreSQL Tutorial", "url": "https://www.postgresqltutorial.com", "type": "tutorial"}],
                "outcome": "Design schemas, write complex queries, and integrate databases with your APIs",
                "key_concepts": ["SQL vs NoSQL", "Schema Design", "CRUD Operations", "Indexing", "Aggregation"],
                "projects": [{"name": "User Dashboard", "description": "Build a dashboard with real data persistence"}, {"name": "Data Migration Script", "description": "Write scripts to migrate data between databases"}],
                "character_dialogue": "Every app needs a memory — that's what databases are! 🗄️ We'll explore both SQL and NoSQL so you can pick the right tool for any project. This is where your apps start feeling real and permanent!"
            },
            {
                "title": "DevOps & Deployment",
                "description": "Learn to deploy your applications to the cloud, set up CI/CD pipelines, and use Docker for containerization.",
                "duration": "2 weeks",
                "difficulty": "Intermediate",
                "phase": "DevOps",
                "resources": [{"title": "Docker Getting Started", "url": "https://docs.docker.com/get-started", "type": "tutorial"}, {"title": "Vercel Deployment", "url": "https://vercel.com/docs", "type": "tutorial"}],
                "outcome": "Deploy full-stack applications to production with CI/CD",
                "key_concepts": ["Docker", "CI/CD", "Cloud Deployment", "Environment Variables", "Nginx"],
                "projects": [{"name": "Dockerize Your App", "description": "Containerize a full-stack app with Docker Compose"}, {"name": "CI/CD Pipeline", "description": "Set up GitHub Actions for automated testing and deployment"}],
                "character_dialogue": "Time to show the world what you've built! 🌍 Deployment is where your code goes from localhost to the real internet. We'll cover Docker, CI/CD, and cloud hosting. This is the final stretch before you become a true full-stack developer!"
            },
            {
                "title": "Full Stack Capstone Project",
                "description": "Combine everything you've learned into one impressive portfolio project. This is your chance to build something that showcases all your skills.",
                "duration": "4 weeks",
                "difficulty": "Advanced",
                "phase": "Capstone",
                "resources": [{"title": "Project Ideas", "url": "https://github.com/practical-tutorials/project-based-learning", "type": "tutorial"}, {"title": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "type": "book"}],
                "outcome": "Have a production-ready full-stack application in your portfolio",
                "key_concepts": ["System Design", "Performance Optimization", "Testing", "Documentation", "Portfolio Presentation"],
                "projects": [{"name": "SaaS Application", "description": "Build a complete SaaS product with auth, payments, and dashboard"}, {"name": "Social Platform", "description": "Create a social media-like platform with real-time features"}],
                "character_dialogue": "This is it — your masterpiece! 🎓 Everything you've learned comes together in this capstone project. Build something you're proud of, something that makes recruiters say 'WOW'. You've got this — I believe in you! Go build something amazing!"
            }
        ],
    }
    
    # Default generic path if role not in predefined
    default_path = [
        {
            "title": f"Introduction to {request.target_role}",
            "description": f"Explore the fundamentals needed for a career as a {request.target_role}. Understand the industry landscape and key skills required.",
            "duration": "2 weeks",
            "difficulty": "Beginner",
            "phase": "Foundation",
            "resources": [{"title": "Industry Overview", "url": "https://roadmap.sh", "type": "tutorial"}],
            "outcome": f"Understand what a {request.target_role} does and the skills required",
            "key_concepts": ["Industry Overview", "Core Skills", "Career Path", "Tools & Technologies"],
            "projects": [{"name": "Research Report", "description": f"Write a report on the {request.target_role} career path"}],
            "character_dialogue": f"Welcome to your journey toward becoming a {request.target_role}! 🚀 Let's start by understanding what this role is all about and the exciting opportunities ahead of you!"
        },
        {
            "title": "Core Technical Skills",
            "description": f"Dive deep into the essential technical skills every {request.target_role} needs. This phase builds your technical foundation.",
            "duration": "4 weeks",
            "difficulty": "Intermediate",
            "phase": "Core Skills",
            "resources": [{"title": "Comprehensive Courses", "url": "https://coursera.org", "type": "course"}],
            "outcome": "Master the fundamental technical skills for the role",
            "key_concepts": ["Technical Foundations", "Best Practices", "Industry Standards", "Problem Solving"],
            "projects": [{"name": "Skill Showcase", "description": "Build a project demonstrating your core skills"}],
            "character_dialogue": "Now we're building your technical muscle! 💪 These are the skills that will set you apart. Practice daily, even just for 30 minutes — consistency is key!"
        },
        {
            "title": "Advanced Concepts & Specialization",
            "description": "Go beyond the basics and develop expertise in advanced areas relevant to your target role.",
            "duration": "4 weeks",
            "difficulty": "Advanced",
            "phase": "Advanced",
            "resources": [{"title": "Advanced Topics", "url": "https://udemy.com", "type": "course"}],
            "outcome": "Apply advanced techniques confidently in real-world scenarios",
            "key_concepts": ["Advanced Techniques", "Optimization", "Architecture", "Best Practices"],
            "projects": [{"name": "Advanced Project", "description": "Tackle a complex project that pushes your limits"}],
            "character_dialogue": "You've come so far! 🌟 Now it's time to level up into the advanced territory. These concepts will separate you from beginners — embrace the challenge!"
        },
        {
            "title": "Portfolio & Job Preparation",
            "description": "Build your portfolio, prepare for interviews, and position yourself for your dream role.",
            "duration": "3 weeks",
            "difficulty": "Advanced",
            "phase": "Capstone",
            "resources": [{"title": "Portfolio Guide", "url": "https://github.com", "type": "tutorial"}],
            "outcome": f"Have a polished portfolio and be interview-ready for {request.target_role} positions",
            "key_concepts": ["Portfolio Building", "Interview Prep", "Networking", "Resume Optimization"],
            "projects": [{"name": "Capstone Project", "description": f"Build your definitive {request.target_role} portfolio piece"}],
            "character_dialogue": f"The finish line is in sight! 🎓 Let's package everything into a stunning portfolio that screams '{request.target_role}'. You've earned this — now let's show the world!"
        }
    ]
    
    # Get path for role or default
    path = role_paths.get(request.target_role, default_path)
    
    return {
        "success": True,
        "learning_path": path,
        "target_role": request.target_role,
        "total_phases": len(path)
    }

@router.post("/learning-path/save")
async def save_learning_path(path_data: LearningPathSaveRequest):
    """Save learning path for user"""
    try:
        db = get_db()
        paths_collection = db[LEARNING_PATHS_COLLECTION]
        
        path_doc = {
            "user_id": path_data.user_id,
            "target_role": path_data.target_role,
            "learning_goal": path_data.learning_goal,
            "current_skills": path_data.current_skills,
            "time_commitment": path_data.time_commitment,
            "path": path_data.path,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = paths_collection.insert_one(path_doc)
        
        return {
            "success": True,
            "path_id": str(result.inserted_id),
            "message": "Learning path saved successfully"
        }
    
    except Exception as e:
        print(f"Error saving learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-path/list")
async def get_learning_paths(user_id: str):
    """Get all learning paths for a user"""
    try:
        db = get_db()
        paths_collection = db[LEARNING_PATHS_COLLECTION]
        
        paths = list(paths_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(50))
        
        for path in paths:
            path["_id"] = str(path["_id"])
        
        return {
            "success": True,
            "paths": paths
        }
    
    except Exception as e:
        print(f"Error fetching learning paths: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/learning-path/{path_id}")
async def delete_learning_path(path_id: str, user_id: str):
    """Delete a learning path"""
    try:
        db = get_db()
        paths_collection = db[LEARNING_PATHS_COLLECTION]
        
        result = paths_collection.delete_one({
            "_id": ObjectId(path_id),
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        return {
            "success": True,
            "message": "Learning path deleted successfully"
        }
    
    except Exception as e:
        print(f"Error deleting learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))
