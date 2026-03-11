"""
Test script to verify that job recommendations are personalized based on resume content.

This test will:
1. Create two different resumes (Data Scientist and Frontend Developer)
2. Upload each resume and get job recommendations
3. Verify that the job recommendations are different and relevant to each resume
"""

import requests
import json
from pathlib import Path

# Backend URL
BASE_URL = "http://localhost:8000"

def test_personalized_recommendations():
    """Test that different resumes get different job recommendations."""
    
    print("=" * 80)
    print("TESTING PERSONALIZED JOB RECOMMENDATIONS")
    print("=" * 80)
    
    # Test case 1: Data Scientist Resume
    print("\n📄 Test Case 1: Data Scientist Resume")
    print("-" * 80)
    
    data_scientist_resume = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "phone": "123-456-7890",
        "skills": [
            "Python",
            "Machine Learning",
            "TensorFlow",
            "PyTorch",
            "Pandas",
            "NumPy",
            "SQL",
            "Data Visualization",
            "Statistics",
            "Deep Learning"
        ],
        "experience": [
            "Senior Data Scientist at Tech Corp (2020-2023)",
            "Data Analyst at Analytics Inc (2018-2020)",
            "Junior Data Scientist at StartupXYZ (2017-2018)"
        ],
        "education": [
            "MS in Data Science - University of Example (2017)",
            "BS in Statistics - University of Sample (2015)"
        ]
    }
    
    # Test case 2: Frontend Developer Resume
    print("\n📄 Test Case 2: Frontend Developer Resume")
    print("-" * 80)
    
    frontend_resume = {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "phone": "987-654-3210",
        "skills": [
            "JavaScript",
            "React",
            "Vue.js",
            "HTML5",
            "CSS3",
            "TypeScript",
            "Redux",
            "Webpack",
            "Responsive Design",
            "UI/UX Design"
        ],
        "experience": [
            "Senior Frontend Developer at WebSolutions (2019-2023)",
            "Frontend Developer at DesignHub (2017-2019)"
        ],
        "education": [
            "BS in Computer Science - Tech University (2017)"
        ]
    }
    
    # Test both resumes
    resumes = [
        ("Data Scientist", data_scientist_resume),
        ("Frontend Developer", frontend_resume)
    ]
    
    results = []
    
    for role, resume_data in resumes:
        print(f"\n{'='*80}")
        print(f"Testing: {role}")
        print(f"{'='*80}")
        
        # Test with job recommendations API
        try:
            response = requests.post(
                f"{BASE_URL}/job-recommendations",
                json=resume_data,
                params={"top_n": 10},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('recommended_jobs', [])
                
                print(f"\n✅ Received {len(jobs)} job recommendations")
                print(f"\nTop 5 Job Titles:")
                for i, job in enumerate(jobs[:5], 1):
                    title = job.get('title', 'Unknown')
                    match_score = job.get('match_score', 0)
                    matched_skills = job.get('matched_skills', [])
                    print(f"  {i}. {title}")
                    print(f"     Match Score: {match_score}%")
                    print(f"     Matched Skills: {', '.join(matched_skills[:5])}")
                
                results.append({
                    'role': role,
                    'jobs': jobs,
                    'skills': resume_data['skills']
                })
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   {response.text}")
        
        except Exception as e:
            print(f"❌ Error testing {role}: {e}")
    
    # Verify that recommendations are different
    print(f"\n{'='*80}")
    print("VERIFICATION: Are recommendations personalized?")
    print(f"{'='*80}")
    
    if len(results) == 2:
        ds_jobs = [j.get('title', '').lower() for j in results[0]['jobs'][:5]]
        fe_jobs = [j.get('title', '').lower() for j in results[1]['jobs'][:5]]
        
        print(f"\nData Scientist Top Jobs: {ds_jobs}")
        print(f"Frontend Developer Top Jobs: {fe_jobs}")
        
        # Check if jobs are different
        common_jobs = set(ds_jobs) & set(fe_jobs)
        
        if len(common_jobs) < 3:  # Less than 3 common jobs means good personalization
            print(f"\n✅ SUCCESS! Recommendations are personalized!")
            print(f"   Only {len(common_jobs)} common jobs out of 5")
            
            # Check if data scientist jobs contain data-related keywords
            ds_keywords = ['data', 'scientist', 'analyst', 'machine learning', 'ml', 'ai']
            ds_matches = sum(1 for job in ds_jobs if any(kw in job for kw in ds_keywords))
            
            # Check if frontend jobs contain frontend-related keywords
            fe_keywords = ['frontend', 'front-end', 'react', 'ui', 'ux', 'web', 'javascript']
            fe_matches = sum(1 for job in fe_jobs if any(kw in job for kw in fe_keywords))
            
            print(f"\n   Data Scientist jobs with relevant keywords: {ds_matches}/5")
            print(f"   Frontend jobs with relevant keywords: {fe_matches}/5")
            
            if ds_matches >= 2 and fe_matches >= 2:
                print(f"\n🎉 EXCELLENT! Jobs are highly relevant to each resume!")
            else:
                print(f"\n⚠️  Jobs could be more relevant to skills")
        else:
            print(f"\n❌ FAILED! Too many common jobs ({len(common_jobs)}/5)")
            print(f"   Recommendations might not be personalized enough")
            print(f"   Common jobs: {common_jobs}")
    else:
        print("❌ Could not complete comparison - insufficient test results")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_personalized_recommendations()
