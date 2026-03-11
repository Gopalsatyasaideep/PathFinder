"""
Authentication router for login and signup.
Uses MongoDB for user storage.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from pymongo import MongoClient
import os

# Initialize router
router = APIRouter(prefix="/auth", tags=["authentication"])

# MongoDB connection
# The application reads the connection URL from the MONGODB_URL environment
# variable. For local development you can run a local Mongo instance, but for
# production (Atlas) set an explicit string such as:
#   mongodb+srv://gopal:YOUR_PASSWORD@cluster0.mgjmdpp.mongodb.net/pathfinder?retryWrites=true&w=majority
# Leaving the default blank will point at localhost which may fail if no server
# is running.
MONGO_URL = os.getenv("MONGODB_URL", "mongodb+srv://gopal:gopal@2005@cluster0.mgjmdpp.mongodb.net/?appName=Cluster0")
DB_NAME = "pathfinder"

# warn if using the localhost default while not on localhost
if MONGO_URL.startswith("mongodb://localhost"):
    print("⚠️  Using default MongoDB URL (localhost). "
          "Set MONGODB_URL to your Atlas connection string to connect to the cloud.")
USERS_COLLECTION = "users"

# JWT config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Database helper
def get_db():
    """Get MongoDB database connection"""
    try:
        client = MongoClient(MONGO_URL)
        # optional ping to verify connection
        client.admin.command('ping')
        db = client[DB_NAME]
        return db
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        raise

# Models
class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Hash password
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Create JWT token
def create_access_token(user_id: str, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/signup", response_model=LoginResponse)
async def signup(user_data: UserSignup):
    """
    User signup endpoint
    Creates new user account in MongoDB
    """
    try:
        db = get_db()
        users_collection = db[USERS_COLLECTION]
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "name": user_data.name,
            "email": user_data.email,
            "password": hashed_password,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert user
        result = users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Create token
        access_token = create_access_token(user_id, user_data.email)
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user_id,
                name=user_data.name,
                email=user_data.email,
                created_at=user_doc["created_at"]
            )
        )
    
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=LoginResponse)
async def login(user_data: UserLogin):
    """
    User login endpoint
    Authenticates user against MongoDB
    """
    try:
        db = get_db()
        users_collection = db[USERS_COLLECTION]
        
        # Find user
        user = users_collection.find_one({"email": user_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(user_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create token
        user_id = str(user["_id"])
        access_token = create_access_token(user_id, user_data.email)
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user_id,
                name=user["name"],
                email=user["email"],
                created_at=user.get("created_at", "")
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify")
async def verify_token(token: str = Body(...)):
    """
    Verify JWT token validity
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"valid": True, "user_id": user_id, "email": email}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
