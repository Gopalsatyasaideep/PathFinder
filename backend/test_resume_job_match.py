"""
Test Resume-Based Job Matching with RapidAPI JSearch
Run this to test the new smart job matching endpoint.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.resume_job_matcher import get_resume_job_matcher


def test_job_matcher():
    """Test the resume-based job matcher."""
    
    print("🧪 Testing Resume-Based Job Matching with RapidAPI JSearch")
    print("=" * 60)
    
    # Sample resume data (replace with your actual data)
    sample_resume = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+91 9876543210',
        'skills': [
            'Python', 'React', 'Node.js', 'JavaScript', 
            'MongoDB', 'Express.js', 'AWS', 'Docker',
            'Git', 'REST API', 'FastAPI', 'HTML', 'CSS'
        ],
        'experience': [
            {
                'title': 'Full Stack Developer',
                'company': 'Tech Corp',
                'duration': '2 years',
                'description': 'Built web applications with React and Node.js'
            },
            {
                'title': 'Junior Developer',
                'company': 'Startup Inc',
                'duration': '1 year',
                'description': 'Developed backend APIs with Python'
            }
        ],
        'education': [
            {
                'degree': 'Bachelor of Technology',
                'field': 'Computer Science',
                'institution': 'ABC University'
            }
        ]
    }
    
    # Initialize matcher
    matcher = get_resume_job_matcher()
    
    # Test 1: Auto-detect target role
    print("\n📋 Test 1: Auto-Detect Target Role")
    print("-" * 60)
    jobs = matcher.get_job_recommendations(
        resume_data=sample_resume,
        target_role=None,  # Will auto-detect
        location='remote',
        max_results=10,
        prioritize_india=True
    )
    
    if jobs:
        print(f"✅ Found {len(jobs)} jobs!")
        print(f"🎯 Auto-detected role: {jobs[0]['title'] if jobs else 'N/A'}")
        print(f"📊 Top 3 matches:\n")
        
        for i, job in enumerate(jobs[:3], 1):
            print(f"{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Relevance: {job['relevance_score']}%")
            print(f"   Skill Match: {job['skill_match_percentage']}%")
            print(f"   Salary: ${job['salary_min']:,} - ${job['salary_max']:,}")
            print(f"   URL: {job['url'][:60]}...")
            print()
    else:
        print("❌ No jobs found. Check your API key and internet connection.")
    
    # Test 2: Specific target role
    print("\n📋 Test 2: Specific Target Role (Full Stack Developer)")
    print("-" * 60)
    jobs2 = matcher.get_job_recommendations(
        resume_data=sample_resume,
        target_role='Full Stack Developer',
        location='India',
        max_results=5,
        prioritize_india=True
    )
    
    if jobs2:
        print(f"✅ Found {len(jobs2)} jobs for 'Full Stack Developer'")
        avg_score = sum(j['relevance_score'] for j in jobs2) / len(jobs2)
        print(f"📊 Average Relevance: {avg_score:.1f}%")
        print(f"🇮🇳 India jobs: {sum(1 for j in jobs2 if 'india' in j['location'].lower())}")
        print(f"🏠 Remote jobs: {sum(1 for j in jobs2 if j.get('is_remote', False))}")
    else:
        print("⚠️ No jobs found for this specific role.")
    
    # Test 3: Remote only
    print("\n📋 Test 3: Remote Jobs Only")
    print("-" * 60)
    jobs3 = matcher.get_job_recommendations(
        resume_data=sample_resume,
        target_role='Software Engineer',
        location='remote',
        max_results=10,
        prioritize_india=False
    )
    
    if jobs3:
        print(f"✅ Found {len(jobs3)} remote jobs")
        remote_count = sum(1 for j in jobs3 if j.get('is_remote', False))
        print(f"🌍 Remote jobs: {remote_count}/{len(jobs3)}")
    else:
        print("⚠️ No remote jobs found.")
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("\nAPI Key Status:")
    print(f"   Key: {matcher.api_key[:20]}...")
    print(f"   Status: {'Active ✅' if matcher.api_key else 'Missing ❌'}")
    
    print("\n💡 Next Steps:")
    print("   1. Check the results above")
    print("   2. Verify jobs are real (from Indeed/LinkedIn)")
    print("   3. Test with your own resume data")
    print("   4. Integrate with frontend")
    
    return jobs if jobs else []


if __name__ == "__main__":
    try:
        jobs = test_job_matcher()
        print(f"\n🎉 Success! Found {len(jobs)} jobs!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("   - Check your internet connection")
        print("   - Verify RAPIDAPI_KEY is set")
        print("   - Try again in a few seconds")
        sys.exit(1)
