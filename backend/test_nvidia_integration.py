"""
Test NVIDIA API Integration

This script tests the NVIDIA API client, ATS scoring, and chatbot integration.
"""

import os
import sys
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


def test_nvidia_client():
    """Test basic NVIDIA client functionality"""
    print("=" * 60)
    print("Testing NVIDIA Client...")
    print("=" * 60)
    
    try:
        from services.nvidia_client import NVIDIAClient, get_nvidia_client
        
        # Check if API key is set
        api_key = os.environ.get("NVIDIA_API_KEY")
        if not api_key:
            print("❌ NVIDIA_API_KEY not found in environment variables")
            print("   Set it with: $env:NVIDIA_API_KEY='nvapi-xxxxx'")
            return False
        
        print(f"✓ API Key found: {api_key[:10]}...")
        
        # Initialize client
        client = get_nvidia_client()
        if not client:
            print("❌ Failed to initialize NVIDIA client")
            return False
        
        print("✓ NVIDIA client initialized successfully")
        
        # Test basic text generation
        print("\nTesting text generation...")
        response = client.generate_text(
            "Say 'Hello from NVIDIA API' in one short sentence.",
            temperature=0.3,
            max_tokens=50
        )
        print(f"✓ Response: {response[:100]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ats_scorer():
    """Test ATS scoring functionality"""
    print("\n" + "=" * 60)
    print("Testing ATS Scorer...")
    print("=" * 60)
    
    try:
        from services.ats_scorer import get_ats_scorer
        
        scorer = get_ats_scorer()
        if not scorer:
            print("❌ ATS Scorer not available (check NVIDIA API key)")
            return False
        
        print("✓ ATS Scorer initialized")
        
        # Test with sample resume data
        sample_resume = {
            "name": "John Doe",
            "skills": ["Python", "React", "SQL", "Docker", "Git"],
            "experience_summary": "3 years of full-stack development experience. Built scalable web applications using React and Python. Implemented CI/CD pipelines.",
            "education": [
                {"degree": "Bachelor", "field": "Computer Science"}
            ]
        }
        
        sample_job_description = """
        Software Engineer Position
        
        We're looking for a mid-level software engineer with:
        - 3+ years of Python experience
        - Strong React/frontend skills
        - Database knowledge (SQL)
        - Experience with Docker and containerization
        - Familiarity with CI/CD pipelines
        """
        
        print("\nScoring sample resume against job description...")
        score = scorer.score_resume(
            resume_data=sample_resume,
            job_description=sample_job_description
        )
        
        print(f"\n✓ ATS Score: {score['overall_score']}/100")
        print(f"  Pass Likelihood: {score['pass_likelihood']}")
        print(f"  Skills Match: {score['category_scores']['skills_match']}/100")
        print(f"\n  Strengths:")
        for strength in score['strengths'][:3]:
            print(f"    - {strength}")
        print(f"\n  Recommendations:")
        for rec in score['ats_recommendations'][:3]:
            print(f"    - {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chatbot_nvidia():
    """Test chatbot with NVIDIA integration"""
    print("\n" + "=" * 60)
    print("Testing Chatbot with NVIDIA...")
    print("=" * 60)
    
    try:
        from services.rag_chatbot import RagCareerAssistant, NVIDIAGenerator
        from services.vector_store import FaissVectorStore
        
        # Initialize with empty store for testing
        store = FaissVectorStore()
        
        # Try to initialize NVIDIA generator
        print("Initializing NVIDIA generator...")
        try:
            generator = NVIDIAGenerator()
            print("✓ NVIDIA generator initialized")
        except Exception as e:
            print(f"⚠ Could not initialize NVIDIA generator: {e}")
            print("  Chatbot will use fallback generator")
            generator = None
        
        # Initialize chatbot
        assistant = RagCareerAssistant(
            store=store,
            generator=generator,
            use_nvidia=True
        )
        
        print("✓ Chatbot initialized")
        
        # Test question
        question = "What skills should I learn to become a better software engineer?"
        print(f"\nAsking: {question}")
        
        response = assistant.ask(question)
        
        print(f"\n✓ Response received:")
        print(f"  Answer: {response.answer[:200]}...")
        print(f"  Confidence: {response.confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_extraction():
    """Test PDF extraction capabilities"""
    print("\n" + "=" * 60)
    print("Testing PDF Extraction...")
    print("=" * 60)
    
    try:
        import pdfplumber
        print("✓ pdfplumber installed")
    except ImportError:
        print("❌ pdfplumber not installed")
        return False
    
    try:
        import PyPDF2
        print("✓ PyPDF2 installed")
    except ImportError:
        print("⚠ PyPDF2 not installed (optional)")
    
    try:
        from services.resume_parser import ResumeParser
        parser = ResumeParser()
        print("✓ ResumeParser initialized")
        return True
    except Exception as e:
        print(f"❌ Error initializing parser: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("NVIDIA API Integration Test Suite")
    print("=" * 60)
    
    results = {
        "PDF Extraction": test_pdf_extraction(),
        "NVIDIA Client": test_nvidia_client(),
        "ATS Scorer": test_ats_scorer(),
        "Chatbot (NVIDIA)": test_chatbot_nvidia()
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
        print("\nCommon issues:")
        print("1. NVIDIA_API_KEY not set - run: $env:NVIDIA_API_KEY='nvapi-xxxxx'")
        print("2. Dependencies not installed - run: pip install -r requirements.txt")
        print("3. Network issues - check internet connection")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
        
        # Test resume analysis
        print("\n📋 Testing resume analysis...")
        sample_resume = {
            "skills": ["Python", "React", "SQL", "Docker"],
            "experience_summary": "2 years as junior developer at tech startup",
            "education": [{"degree": "Bachelor", "field": "Computer Science"}]
        }
        
        analysis = client.generate_resume_analysis(sample_resume)
        print("Resume Analysis Results:")
        print(json.dumps(analysis, indent=2))
        
        # Test job recommendations
        print("\n💼 Testing job recommendations...")
        job_recs = client.generate_job_recommendations(sample_resume, num_recommendations=3)
        print(f"Generated {len(job_recs)} job recommendations")
        for i, job in enumerate(job_recs[:2]):  # Show first 2
            print(f"{i+1}. {job.get('title', 'N/A')} - Match: {job.get('match_score', 'N/A')}%")
        
        # Test learning path
        print("\n📚 Testing learning path generation...")
        learning_path = client.generate_learning_path(
            current_skills=["Python", "SQL"], 
            target_role="Senior Software Engineer"
        )
        print(f"Learning Path: {len(learning_path.get('learning_phases', []))} phases")
        print(f"Skill Gaps: {learning_path.get('skill_gaps', [])}")
        
        print("\n🎉 All NVIDIA API tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ NVIDIA API test failed: {e}")
        return False


def test_ai_service_manager():
    """Test AI Service Manager with fallback capabilities."""
    print("\n🤖 Testing AI Service Manager...")
    
    try:
        # Test with different configurations
        # Note: This will use env variables or defaults
        manager = AIServiceManager(prefer_nvidia=True)
        
        # Test resume analysis with fallback
        sample_resume = {
            "skills": ["JavaScript", "Node.js", "MongoDB"],
            "experience_summary": "1 year frontend developer",
            "education": [{"degree": "Bachelor", "field": "Information Technology"}]
        }
        
        print("📋 Testing manager resume analysis...")
        analysis = manager.generate_resume_analysis(sample_resume)
        print(f"Analysis completed - Career Level: {analysis.get('career_level', 'unknown')}")
        
        print("💼 Testing manager job recommendations...")
        job_recs = manager.generate_job_recommendations(sample_resume, num_recommendations=2)
        print(f"Generated {len(job_recs)} recommendations")
        
        print("📚 Testing manager learning path...")
        learning_path = manager.generate_learning_path(
            current_skills=["JavaScript", "HTML", "CSS"],
            target_role="Full Stack Developer"
        )
        print(f"Learning path has {len(learning_path.get('learning_phases', []))} phases")
        
        print("✅ AI Service Manager tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ AI Service Manager test failed: {e}")
        return False


def test_integration_status():
    """Check which AI services are available."""
    print("\n📊 AI Services Status Check...")
    
    # Check NVIDIA API
    nvidia_client = get_nvidia_client()
    nvidia_status = "✅ Available" if nvidia_client else "❌ Not Available"
    print(f"NVIDIA API: {nvidia_status}")
    
    # Check OpenRouter API  
    from services.openrouter_client import get_openrouter_client
    openrouter_client = get_openrouter_client()
    openrouter_status = "✅ Available" if openrouter_client else "❌ Not Available"
    print(f"OpenRouter API: {openrouter_status}")
    
    if not nvidia_client and not openrouter_client:
        print("\n⚠️  No AI services available!")
        print("   Please configure at least one API key:")
        print("   - NVIDIA API: Set NVIDIA_API_KEY environment variable")
        print("   - OpenRouter API: Set OPENROUTER_API_KEY or update DEFAULT_API_KEY")
        return False
    
    print(f"\n✅ AI services configured correctly!")
    return True


if __name__ == "__main__":
    print("🚀 PathFinder AI - NVIDIA Integration Test")
    print("=" * 50)
    
    # Test integration status first
    status_ok = test_integration_status()
    
    if status_ok:
        print("\n" + "=" * 50)
        
        # Test NVIDIA API if available
        nvidia_client = get_nvidia_client()
        if nvidia_client:
            nvidia_ok = test_nvidia_api()
        else:
            print("⏭️  Skipping NVIDIA API tests (not configured)")
            nvidia_ok = True
        
        # Test AI Service Manager
        if nvidia_ok:
            manager_ok = test_ai_service_manager()
        else:
            manager_ok = False
        
        print("\n" + "=" * 50)
        if nvidia_ok and manager_ok:
            print("🎉 All integration tests passed!")
            print("✅ Your PathFinder AI system is ready to use enhanced AI features")
        else:
            print("⚠️  Some tests failed - check API configuration")
    
    print("\n💡 Next Steps:")
    print("1. Set your NVIDIA_API_KEY environment variable")
    print("2. Run: python main.py to start the backend")
    print("3. The system will automatically use the best available AI service")