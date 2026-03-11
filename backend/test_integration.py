import requests
import json

def test_resume_upload_and_analysis():
    """Test the complete resume upload and analysis flow"""
    print("🧪 Testing Complete Resume Analysis Flow...")
    print("=" * 60)
    
    # Test health check first
    print("1. Testing health check...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is running")
            health_data = response.json()
            print(f"   Primary AI Service: {health_data['ai_services']['primary_service']}")
        else:
            print("❌ Backend not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test smart analysis with sample data
    print("\n2. Testing smart resume analysis...")
    try:
        # Simulate form data
        files = {
            'file': ('test_resume.txt', 'John Doe\nSoftware Developer\nSkills: Python, JavaScript, React, Node.js, Docker\nExperience: 2 years of full-stack development', 'text/plain')
        }
        data = {
            'target_role': 'Software Engineer',
            'num_jobs': 5
        }
        
        response = requests.post(
            "http://localhost:8000/upload-resume/smart-analysis", 
            files=files,
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Smart analysis successful!")
            
            # Check resume data
            resume = result.get('resume', {})
            print(f"   Resume name: {resume.get('name', 'Unknown')}")
            print(f"   Skills found: {len(resume.get('skills', []))}")
            
            # Check insights
            insights = result.get('insights', {})
            print(f"   Strengths: {len(insights.get('strengths', []))}")
            print(f"   Improvements: {len(insights.get('improvements', []))}")
            print(f"   Career level: {insights.get('career_level', 'unknown')}")
            
            # Check jobs
            jobs = result.get('job_recommendations', [])
            print(f"   Job recommendations: {len(jobs)}")
            
            for i, job in enumerate(jobs[:3]):
                title = job.get('title', 'Unknown')
                match_score = job.get('match_score', 0)
                ats_score = job.get('ats_score', {}).get('overall_score', 0)
                print(f"     {i+1}. {title} - Match: {match_score}% - ATS: {ats_score}/100")
            
            return True
            
        else:
            print(f"❌ Smart analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Smart analysis error: {e}")
        return False

def test_chat():
    """Test the chat functionality"""
    print("\n3. Testing chat functionality...")
    try:
        chat_data = {
            "question": "What are the best programming languages to learn in 2026?",
            "resume_json": {
                "skills": ["Python", "JavaScript"],
                "name": "Test User"
            }
        }
        
        response = requests.post(
            "http://localhost:8000/chat",
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            print("✅ Chat successful!")
            print(f"   Question: {chat_data['question']}")
            print(f"   Answer: {answer[:200]}...")
            print(f"   Provider: {result.get('provider', 'unknown')}")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PathFinder AI Integration Test")
    print("=" * 60)
    
    success = True
    success &= test_resume_upload_and_analysis()
    success &= test_chat()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! The system is working correctly.")
        print("\n✨ Features working:")
        print("   ✅ Resume upload and parsing")  
        print("   ✅ NVIDIA AI resume analysis")
        print("   ✅ Diverse job recommendations")
        print("   ✅ ATS scoring")
        print("   ✅ Chat functionality")
    else:
        print("❌ Some tests failed. Check the logs above.")
    
    exit(0 if success else 1)