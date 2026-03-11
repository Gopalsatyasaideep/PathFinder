#!/usr/bin/env python3
"""
Direct test of NVIDIA API integration
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.nvidia_client import get_nvidia_client


def test_nvidia_direct():
    """Test NVIDIA client directly"""
    print("🧪 Testing NVIDIA API Direct Connection...")
    print("=" * 50)
    
    client = get_nvidia_client()
    if not client:
        print("❌ NVIDIA client not available")
        return False
    
    print("✅ NVIDIA client initialized")
    print(f"   API Key: {client.api_key[:15]}...")
    print(f"   Model: {client.model}")
    
    # Test simple text generation
    print("\n🤖 Testing simple text generation...")
    try:
        response = client.generate_text(
            "Say 'Hello, NVIDIA API is working!' in a professional tone.",
            temperature=0.1,
            max_tokens=50
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        return False
    
    # Test resume analysis
    print("\n📄 Testing resume analysis...")
    try:
        sample_resume = {
            "skills": ["Python", "JavaScript", "React", "Node.js", "Docker"],
            "experience_summary": "2 years of full-stack development experience with Python and JavaScript. Built web applications using React and Node.js.",
            "education": [{"degree": "Bachelor of Computer Science", "field": "Computer Science"}]
        }
        
        analysis = client.generate_resume_analysis(sample_resume)
        print(f"✅ Resume Analysis Success:")
        print(f"   Strengths: {len(analysis.get('strengths', []))}")
        print(f"   Improvements: {len(analysis.get('improvements', []))}")
        print(f"   Career Level: {analysis.get('career_level', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Resume analysis failed: {e}")
        return False
    
    # Test job recommendations
    print("\n🎯 Testing job recommendations...")
    try:
        jobs = client.generate_job_recommendations(sample_resume, num_recommendations=3)
        print(f"✅ Job Recommendations Success:")
        print(f"   Generated: {len(jobs)} jobs")
        for i, job in enumerate(jobs[:2]):
            title = job.get('title', 'Unknown')
            score = job.get('match_score', 0)
            print(f"   {i+1}. {title} - {score}% match")
            
    except Exception as e:
        print(f"❌ Job recommendations failed: {e}")
        return False
    
    print("\n🎉 All NVIDIA tests passed!")
    return True


if __name__ == "__main__":
    success = test_nvidia_direct()
    exit(0 if success else 1)