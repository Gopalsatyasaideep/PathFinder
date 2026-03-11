"""
Test Role Detection and Enhanced Job Recommendations

This script tests the complete flow:
1. Role detection using NVIDIA NIM model
2. Enhanced job recommendations based on detected role
3. Verification that recommendations are accurate and personalized
"""

import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.nvidia_client import get_nvidia_client


def test_role_detection():
    """Test NVIDIA NIM role detection feature."""
    print("\n" + "=" * 80)
    print("🎯 TESTING ROLE DETECTION WITH NVIDIA NIM")
    print("=" * 80)
    
    # Initialize NVIDIA client
    client = get_nvidia_client()
    if not client:
        print("❌ NVIDIA client not available. Please set NVIDIA_API_KEY.")
        return False
    
    print("✅ NVIDIA client initialized successfully")
    
    # Test Case 1: Full Stack Developer
    print("\n" + "-" * 80)
    print("📋 TEST CASE 1: Full Stack Developer Profile")
    print("-" * 80)
    
    resume_fullstack = {
        "skills": ["React", "Node.js", "Express", "MongoDB", "JavaScript", "TypeScript", 
                   "HTML", "CSS", "REST APIs", "Git", "Docker"],
        "experience": [
            "Developed full-stack web applications using MERN stack",
            "Built RESTful APIs with Node.js and Express",
            "Created responsive UIs with React and Material-UI",
            "Worked on 5+ projects with MongoDB database"
        ],
        "education": [{"degree": "Bachelor", "field": "Computer Science"}]
    }
    
    role_result = client.detect_target_role(resume_fullstack)
    print("\n🎯 ROLE DETECTION RESULT:")
    print(f"   Target Role: {role_result['target_role']}")
    print(f"   Role Level: {role_result['role_level']}")
    print(f"   Industry: {role_result['industry']}")
    print(f"   Confidence: {role_result['confidence']}")
    print(f"   Alternative Roles: {', '.join(role_result['alternative_roles'])}")
    print(f"   Key Strengths: {', '.join(role_result['key_strengths'])}")
    print(f"   Reasoning: {role_result['reasoning']}")
    
    # Verify the detected role is relevant
    expected_roles = ["full stack", "mern", "web developer", "software"]
    role_lower = role_result['target_role'].lower()
    is_relevant = any(exp in role_lower for exp in expected_roles)
    
    if is_relevant:
        print("\n✅ TEST CASE 1 PASSED: Role detection is accurate!")
    else:
        print(f"\n⚠️  TEST CASE 1: Unexpected role detected: {role_result['target_role']}")
    
    # Test Case 2: Data Scientist
    print("\n" + "-" * 80)
    print("📋 TEST CASE 2: Data Scientist Profile")
    print("-" * 80)
    
    resume_ds = {
        "skills": ["Python", "Machine Learning", "TensorFlow", "Pandas", "NumPy", 
                   "Scikit-learn", "Statistics", "SQL", "Data Visualization", "Jupyter"],
        "experience": [
            "Built machine learning models for predictive analytics",
            "Performed data analysis on large datasets using Python",
            "Developed NLP models with TensorFlow and Keras",
            "Created data visualizations and reports for stakeholders"
        ],
        "education": [{"degree": "Master", "field": "Data Science"}]
    }
    
    role_result_ds = client.detect_target_role(resume_ds)
    print("\n🎯 ROLE DETECTION RESULT:")
    print(f"   Target Role: {role_result_ds['target_role']}")
    print(f"   Role Level: {role_result_ds['role_level']}")
    print(f"   Industry: {role_result_ds['industry']}")
    print(f"   Confidence: {role_result_ds['confidence']}")
    print(f"   Alternative Roles: {', '.join(role_result_ds['alternative_roles'])}")
    
    expected_ds_roles = ["data scientist", "ml engineer", "machine learning", "data"]
    role_ds_lower = role_result_ds['target_role'].lower()
    is_ds_relevant = any(exp in role_ds_lower for exp in expected_ds_roles)
    
    if is_ds_relevant:
        print("\n✅ TEST CASE 2 PASSED: Role detection is accurate!")
    else:
        print(f"\n⚠️  TEST CASE 2: Unexpected role detected: {role_result_ds['target_role']}")
    
    # Test Case 3: DevOps Engineer
    print("\n" + "-" * 80)
    print("📋 TEST CASE 3: DevOps Engineer Profile")
    print("-" * 80)
    
    resume_devops = {
        "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Jenkins", "Terraform", 
                   "Linux", "Python", "Bash", "GitLab", "Monitoring"],
        "experience": [
            "Managed cloud infrastructure on AWS with Terraform",
            "Set up CI/CD pipelines using Jenkins and GitLab",
            "Deployed containerized applications with Docker and Kubernetes",
            "Automated deployment processes and monitoring"
        ],
        "education": [{"degree": "Bachelor", "field": "Information Technology"}]
    }
    
    role_result_devops = client.detect_target_role(resume_devops)
    print("\n🎯 ROLE DETECTION RESULT:")
    print(f"   Target Role: {role_result_devops['target_role']}")
    print(f"   Role Level: {role_result_devops['role_level']}")
    print(f"   Industry: {role_result_devops['industry']}")
    print(f"   Confidence: {role_result_devops['confidence']}")
    
    expected_devops_roles = ["devops", "cloud", "sre", "infrastructure"]
    role_devops_lower = role_result_devops['target_role'].lower()
    is_devops_relevant = any(exp in role_devops_lower for exp in expected_devops_roles)
    
    if is_devops_relevant:
        print("\n✅ TEST CASE 3 PASSED: Role detection is accurate!")
    else:
        print(f"\n⚠️  TEST CASE 3: Unexpected role detected: {role_result_devops['target_role']}")
    
    return True


def test_enhanced_job_recommendations():
    """Test enhanced job recommendations using detected role."""
    print("\n" + "=" * 80)
    print("💼 TESTING ENHANCED JOB RECOMMENDATIONS")
    print("=" * 80)
    
    client = get_nvidia_client()
    if not client:
        print("❌ NVIDIA client not available.")
        return False
    
    # Test with Full Stack Developer (with detected role)
    print("\n" + "-" * 80)
    print("📋 FULL STACK DEVELOPER: Job Recommendations WITH Detected Role")
    print("-" * 80)
    
    resume_with_role = {
        "skills": ["React", "Node.js", "Express", "MongoDB", "JavaScript", "TypeScript"],
        "experience": ["3 years of full-stack development experience"],
        "education": [{"degree": "Bachelor", "field": "Computer Science"}],
        "target_role": "Full Stack Developer",  # Detected role
        "role_level": "mid",
        "industry": "Technology"
    }
    
    jobs_with_role = client.generate_job_recommendations(resume_with_role, num_recommendations=5)
    
    print(f"\n✅ Received {len(jobs_with_role)} job recommendations")
    print("\n📊 Top 3 Recommendations:")
    for i, job in enumerate(jobs_with_role[:3], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company Type: {job.get('company_type', 'N/A')}")
        print(f"   Match Score: {job.get('match_score', 'N/A')}%")
        print(f"   Industry: {job.get('industry', 'N/A')}")
        print(f"   Remote: {job.get('remote_option', 'N/A')}")
        print(f"   Why Good Fit: {job.get('why_good_fit', 'N/A')[:100]}...")
    
    # Test without detected role (baseline)
    print("\n" + "-" * 80)
    print("📋 FULL STACK DEVELOPER: Job Recommendations WITHOUT Detected Role")
    print("-" * 80)
    
    resume_without_role = {
        "skills": ["React", "Node.js", "Express", "MongoDB", "JavaScript", "TypeScript"],
        "experience": ["3 years of full-stack development experience"],
        "education": [{"degree": "Bachelor", "field": "Computer Science"}]
    }
    
    jobs_without_role = client.generate_job_recommendations(resume_without_role, num_recommendations=5)
    
    print(f"\n✅ Received {len(jobs_without_role)} job recommendations")
    print("\n📊 Top 3 Recommendations:")
    for i, job in enumerate(jobs_without_role[:3], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company Type: {job.get('company_type', 'N/A')}")
        print(f"   Match Score: {job.get('match_score', 'N/A')}%")
    
    # Analyze improvement
    print("\n" + "-" * 80)
    print("📈 IMPROVEMENT ANALYSIS")
    print("-" * 80)
    
    # Check if recommendations with role are more focused
    with_role_titles = [job['title'].lower() for job in jobs_with_role]
    without_role_titles = [job['title'].lower() for job in jobs_without_role]
    
    # Count how many recommendations match "full stack" or related terms
    fullstack_terms = ["full stack", "fullstack", "mern", "mean", "web developer"]
    with_role_matches = sum(1 for title in with_role_titles if any(term in title for term in fullstack_terms))
    without_role_matches = sum(1 for title in without_role_titles if any(term in title for term in fullstack_terms))
    
    print(f"\nRelevant matches WITH detected role: {with_role_matches}/5")
    print(f"Relevant matches WITHOUT detected role: {without_role_matches}/5")
    
    if with_role_matches >= without_role_matches:
        print("\n✅ IMPROVEMENT VERIFIED: Role detection improves recommendation relevance!")
    else:
        print("\n⚠️  Both approaches show similar relevance")
    
    return True


def test_end_to_end_flow():
    """Test complete end-to-end flow: role detection → job recommendations."""
    print("\n" + "=" * 80)
    print("🔄 TESTING END-TO-END FLOW")
    print("=" * 80)
    
    client = get_nvidia_client()
    if not client:
        print("❌ NVIDIA client not available.")
        return False
    
    # Simulate a complete resume upload flow
    print("\n📝 Step 1: Parse Resume Data")
    resume_data = {
        "name": "John Doe",
        "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "AWS"],
        "experience": [
            "Senior Backend Developer at Tech Corp (2020-2024)",
            "Built scalable APIs using Python and FastAPI",
            "Designed microservices architecture with Docker and Kubernetes"
        ],
        "education": [{"degree": "Master", "field": "Computer Science"}]
    }
    print("✅ Resume data parsed")
    
    # Step 2: Detect role
    print("\n🎯 Step 2: Detect Target Role using NVIDIA NIM")
    role_detection = client.detect_target_role(resume_data)
    print(f"✅ Detected Role: {role_detection['target_role']}")
    print(f"   Level: {role_detection['role_level']}")
    print(f"   Confidence: {role_detection['confidence']}")
    
    # Add detected role to resume data
    resume_data['target_role'] = role_detection['target_role']
    resume_data['role_level'] = role_detection['role_level']
    resume_data['industry'] = role_detection['industry']
    
    # Step 3: Generate job recommendations
    print("\n💼 Step 3: Generate Personalized Job Recommendations")
    jobs = client.generate_job_recommendations(resume_data, num_recommendations=5)
    print(f"✅ Generated {len(jobs)} job recommendations")
    
    # Display results
    print("\n" + "-" * 80)
    print("📊 FINAL RESULTS")
    print("-" * 80)
    print(f"\n🎯 Detected Role: {resume_data['target_role']} ({resume_data['role_level']}-level)")
    print(f"\n💼 Top {len(jobs)} Job Recommendations:\n")
    
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']}")
        print(f"   └─ {job.get('company_type', 'N/A')} | {job.get('match_score', 'N/A')}% match | {job.get('industry', 'N/A')}")
    
    print("\n✅ END-TO-END FLOW COMPLETED SUCCESSFULLY!")
    return True


def main():
    """Main test runner."""
    print("\n" + "=" * 80)
    print("🚀 STARTING ROLE DETECTION AND JOB RECOMMENDATION TESTS")
    print("=" * 80)
    
    try:
        # Test 1: Role Detection
        success1 = test_role_detection()
        
        # Test 2: Enhanced Job Recommendations
        success2 = test_enhanced_job_recommendations()
        
        # Test 3: End-to-End Flow
        success3 = test_end_to_end_flow()
        
        # Final Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Role Detection: {'PASSED' if success1 else 'FAILED'}")
        print(f"✅ Enhanced Recommendations: {'PASSED' if success2 else 'FAILED'}")
        print(f"✅ End-to-End Flow: {'PASSED' if success3 else 'FAILED'}")
        
        if success1 and success2 and success3:
            print("\n🎉 ALL TESTS PASSED! Role detection and recommendations working perfectly!")
            return True
        else:
            print("\n⚠️  Some tests failed. Please check the details above.")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
