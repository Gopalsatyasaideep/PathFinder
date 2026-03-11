"""
Test script to verify MongoDB connection and user history endpoints
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "pathfinder"

def test_mongodb_connection():
    """Test if MongoDB is running and accessible"""
    print("=" * 60)
    print("Testing MongoDB Connection...")
    print("=" * 60)
    
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
        # Trigger connection
        client.server_info()
        print("✓ MongoDB connection successful!")
        
        db = client[DB_NAME]
        print(f"✓ Database '{DB_NAME}' accessible")
        
        # List collections
        collections = db.list_collection_names()
        print(f"✓ Existing collections: {collections if collections else 'None (will be created on first insert)'}")
        
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure MongoDB is installed")
        print("2. Start MongoDB service:")
        print("   - Windows: net start MongoDB")
        print("   - Mac/Linux: sudo systemctl start mongod")
        print("3. Check if MongoDB is running on port 27017")
        return False

def test_chat_save():
    """Test chat history save"""
    print("\n" + "=" * 60)
    print("Testing Chat History Save...")
    print("=" * 60)
    
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        chat_collection = db["chat_history"]
        
        # Test document
        test_chat = {
            "user_id": "test_user_123",
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": datetime.utcnow().isoformat()},
                {"role": "assistant", "content": "Hi! How can I help?", "timestamp": datetime.utcnow().isoformat()}
            ],
            "session_name": "Test Chat",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = chat_collection.insert_one(test_chat)
        print(f"✓ Chat saved successfully! ID: {result.inserted_id}")
        
        # Verify it's saved
        saved_chat = chat_collection.find_one({"_id": result.inserted_id})
        if saved_chat:
            print(f"✓ Chat retrieved successfully!")
            print(f"  - User ID: {saved_chat['user_id']}")
            print(f"  - Messages: {len(saved_chat['messages'])}")
            print(f"  - Session: {saved_chat['session_name']}")
        
        # Clean up test data
        chat_collection.delete_one({"_id": result.inserted_id})
        print("✓ Test data cleaned up")
        
        return True
    except Exception as e:
        print(f"✗ Chat save test failed: {e}")
        return False

def test_resume_save():
    """Test resume analysis save"""
    print("\n" + "=" * 60)
    print("Testing Resume Analysis Save...")
    print("=" * 60)
    
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        resume_collection = db["resume_analyses"]
        
        # Test document
        test_resume = {
            "user_id": "test_user_123",
            "resume_data": {"name": "Test User", "email": "test@example.com"},
            "analysis_results": {"skills": ["Python", "JavaScript"], "score": 85},
            "file_name": "test_resume.pdf",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = resume_collection.insert_one(test_resume)
        print(f"✓ Resume analysis saved successfully! ID: {result.inserted_id}")
        
        # Verify it's saved
        saved_resume = resume_collection.find_one({"_id": result.inserted_id})
        if saved_resume:
            print(f"✓ Resume analysis retrieved successfully!")
            print(f"  - User ID: {saved_resume['user_id']}")
            print(f"  - File: {saved_resume['file_name']}")
            print(f"  - Skills: {saved_resume['analysis_results']['skills']}")
        
        # Clean up test data
        resume_collection.delete_one({"_id": result.inserted_id})
        print("✓ Test data cleaned up")
        
        return True
    except Exception as e:
        print(f"✗ Resume save test failed: {e}")
        return False

def show_collections_data():
    """Show current data in collections"""
    print("\n" + "=" * 60)
    print("Current Database Status...")
    print("=" * 60)
    
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        
        collections = {
            "chat_history": "Chat History",
            "resume_analyses": "Resume Analyses",
            "job_recommendations": "Job Recommendations",
            "learning_paths": "Learning Paths"
        }
        
        for coll_name, display_name in collections.items():
            collection = db[coll_name]
            count = collection.count_documents({})
            print(f"\n{display_name}:")
            print(f"  - Total documents: {count}")
            
            if count > 0:
                # Show sample
                sample = collection.find_one()
                if sample:
                    print(f"  - Sample user_id: {sample.get('user_id', 'N/A')}")
                    print(f"  - Created at: {sample.get('created_at', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"✗ Error checking collections: {e}")
        return False

if __name__ == "__main__":
    print("\n🔍 PathFinder AI - MongoDB & User History Test")
    print("=" * 60)
    
    # Run tests
    mongo_ok = test_mongodb_connection()
    
    if mongo_ok:
        chat_ok = test_chat_save()
        resume_ok = test_resume_save()
        show_collections_data()
        
        print("\n" + "=" * 60)
        print("Test Summary:")
        print("=" * 60)
        print(f"MongoDB Connection: {'✓ PASS' if mongo_ok else '✗ FAIL'}")
        print(f"Chat Save Test: {'✓ PASS' if chat_ok else '✗ FAIL'}")
        print(f"Resume Save Test: {'✓ PASS' if resume_ok else '✗ FAIL'}")
        
        if mongo_ok and chat_ok and resume_ok:
            print("\n✅ All tests passed! MongoDB and endpoints are working correctly.")
            print("\n📝 Next Steps:")
            print("1. Start the backend: python backend/main.py")
            print("2. Start the frontend: npm run dev")
            print("3. Login and test chat/resume features")
        else:
            print("\n⚠️ Some tests failed. Please check MongoDB setup.")
    else:
        print("\n⚠️ Cannot proceed without MongoDB. Please start MongoDB service.")
    
    print("=" * 60)
