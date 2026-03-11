"""
Test multiple RapidAPI job search endpoints to find working ones
"""
import http.client
import json
import requests

API_KEY = "c0d23f9058msh4d8de44e3f0e86dp15ee2cjsn34acc712be7b"

def test_jsearch_api():
    """Test JSearch API - Indeed, LinkedIn, Glassdoor aggregator"""
    print("\n" + "="*80)
    print("📌 Test 1: JSearch API (Indeed/LinkedIn/Glassdoor)")
    print("="*80)
    
    try:
        url = "https://jsearch.p.rapidapi.com/search"
        
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        params = {
            "query": "Software Engineer",
            "page": "1",
            "num_pages": "1"
        }
        
        print("🔍 Searching for: Software Engineer jobs")
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('data', [])
            
            print(f"✅ SUCCESS! Found {len(jobs)} jobs from JSearch")
            
            if jobs:
                print("\n📋 First 5 jobs:")
                for i, job in enumerate(jobs[:5], 1):
                    print(f"\n  Job {i}:")
                    print(f"    Title: {job.get('job_title', 'N/A')}")
                    print(f"    Company: {job.get('employer_name', 'N/A')}")
                    print(f"    Location: {job.get('job_city', 'N/A')}, {job.get('job_country', 'N/A')}")
                    print(f"    Type: {job.get('job_employment_type', 'N/A')}")
                    print(f"    Remote: {job.get('job_is_remote', False)}")
                    print(f"    Posted: {job.get('job_posted_at_datetime_utc', 'N/A')[:10]}")
                
                return True, jobs
        else:
            print(f"❌ Failed: {response.text[:200]}")
            return False, []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, []

def test_linkedin_jobs_api():
    """Test LinkedIn Jobs API"""
    print("\n" + "="*80)
    print("📌 Test 2: LinkedIn Jobs API")
    print("="*80)
    
    try:
        conn = http.client.HTTPSConnection("linkedin-jobs-search.p.rapidapi.com")
        
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "linkedin-jobs-search.p.rapidapi.com"
        }
        
        conn.request("GET", "/?keywords=Software%20Engineer", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        
        print(f"✅ Status Code: {res.status}")
        
        if res.status == 200:
            result = json.loads(data.decode("utf-8"))
            jobs = result if isinstance(result, list) else result.get('data', [])
            
            print(f"✅ SUCCESS! Found {len(jobs)} jobs from LinkedIn")
            
            if jobs:
                print("\n📋 First 3 jobs:")
                for i, job in enumerate(jobs[:3], 1):
                    print(f"\n  Job {i}:")
                    print(f"    Title: {job.get('title', 'N/A')}")
                    print(f"    Company: {job.get('company', 'N/A')}")
                    print(f"    Location: {job.get('location', 'N/A')}")
            
            conn.close()
            return True, jobs
        else:
            print(f"❌ Failed: {data.decode('utf-8')[:200]}")
            conn.close()
            return False, []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, []

def test_jobs_api():
    """Test Jobs API"""
    print("\n" + "="*80)
    print("📌 Test 3: Jobs API (General)")
    print("="*80)
    
    try:
        url = "https://jobs-api14.p.rapidapi.com/list"
        
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "jobs-api14.p.rapidapi.com"
        }
        
        params = {
            "query": "Software Engineer",
            "location": "United States",
            "distance": "1.0",
            "language": "en_US",
            "remoteOnly": "false",
            "datePosted": "month",
            "employmentTypes": "fulltime",
            "index": "0"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', []) or data.get('data', [])
            
            print(f"✅ SUCCESS! Found {len(jobs)} jobs")
            
            if jobs:
                print("\n📋 First 3 jobs:")
                for i, job in enumerate(jobs[:3], 1):
                    print(f"\n  Job {i}:")
                    print(f"    Title: {job.get('title', 'N/A')}")
                    print(f"    Company: {job.get('company', 'N/A')}")
            
            return True, jobs
        else:
            print(f"❌ Failed: {response.text[:200]}")
            return False, []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, []

def test_indeed_api():
    """Test Indeed API"""
    print("\n" + "="*80)
    print("📌 Test 4: Indeed API")
    print("="*80)
    
    try:
        url = "https://indeed12.p.rapidapi.com/jobs/search"
        
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "indeed12.p.rapidapi.com"
        }
        
        params = {
            "query": "Software Engineer",
            "location": "United States",
            "page_id": "1"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('hits', []) or data.get('jobs', []) or data.get('data', [])
            
            print(f"✅ SUCCESS! Found {len(jobs)} jobs from Indeed")
            
            if jobs:
                print("\n📋 First 3 jobs:")
                for i, job in enumerate(jobs[:3], 1):
                    print(f"\n  Job {i}:")
                    print(f"    Title: {job.get('title', 'N/A')}")
                    print(f"    Company: {job.get('company', job.get('company_name', 'N/A'))}")
            
            return True, jobs
        else:
            print(f"❌ Failed: {response.text[:200]}")
            return False, []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, []

def test_job_search_api():
    """Test Job Search API"""
    print("\n" + "="*80)
    print("📌 Test 5: Job Search API")
    print("="*80)
    
    try:
        url = "https://job-search-api1.p.rapidapi.com/v1/job-search"
        
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "job-search-api1.p.rapidapi.com"
        }
        
        params = {
            "title": "Software Engineer",
            "location": "United States",
            "page": "1"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', []) or data.get('data', []) or data.get('results', [])
            
            print(f"✅ SUCCESS! Found {len(jobs)} jobs")
            
            if jobs:
                print("\n📋 First 3 jobs:")
                for i, job in enumerate(jobs[:3], 1):
                    print(f"\n  Job {i}:")
                    print(f"    {job}")
            
            return True, jobs
        else:
            print(f"❌ Failed: {response.text[:200]}")
            return False, []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, []

def main():
    print("\n" + "🚀"*40)
    print("TESTING ALL RAPIDAPI JOB SEARCH APIS")
    print("🚀"*40)
    print(f"\n🔑 Using API Key: {API_KEY[:20]}...")
    
    results = []
    
    # Test all APIs
    success1, jobs1 = test_jsearch_api()
    results.append(("JSearch (Indeed/LinkedIn/Glassdoor)", success1, len(jobs1)))
    
    success2, jobs2 = test_linkedin_jobs_api()
    results.append(("LinkedIn Jobs API", success2, len(jobs2)))
    
    success3, jobs3 = test_jobs_api()
    results.append(("Jobs API", success3, len(jobs3)))
    
    success4, jobs4 = test_indeed_api()
    results.append(("Indeed API", success4, len(jobs4)))
    
    success5, jobs5 = test_job_search_api()
    results.append(("Job Search API", success5, len(jobs5)))
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY OF ALL API TESTS")
    print("="*80)
    
    working_apis = []
    for name, success, count in results:
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{status} - {name}: {count} jobs")
        if success:
            working_apis.append((name, count))
    
    print("\n" + "="*80)
    if working_apis:
        print(f"✅ SUCCESS! {len(working_apis)} API(s) are working:")
        for name, count in working_apis:
            print(f"   • {name}: {count} jobs")
        
        print("\n💡 Recommendation:")
        best_api = max(working_apis, key=lambda x: x[1])
        print(f"   Use '{best_api[0]}' - it returned the most jobs ({best_api[1]} jobs)")
        
        # Return the best working jobs
        if success1 and jobs1:
            return jobs1
        elif success2 and jobs2:
            return jobs2
        elif success3 and jobs3:
            return jobs3
        elif success4 and jobs4:
            return jobs4
        elif success5 and jobs5:
            return jobs5
    else:
        print("❌ No APIs are currently working!")
        print("\n💡 Possible reasons:")
        print("   • API subscription required on RapidAPI")
        print("   • Rate limits exceeded")
        print("   • API key issues")
        print("\n🔗 Subscribe to APIs at:")
        print("   https://rapidapi.com/hub")
    
    return []

if __name__ == "__main__":
    jobs = main()
    
    if jobs:
        print(f"\n\n🎉 Total Jobs Retrieved: {len(jobs)}")
        print("="*80)
