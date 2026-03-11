"""
Test JSearch and Jobs API 14 to fetch real jobs
"""
import http.client
import json

API_KEY = "c0d23f9058msh4d8de44e3f0e86dp15ee2cjsn34acc712be7b"

def test_jsearch_search():
    """Test JSearch API - Search for jobs"""
    print("\n" + "="*80)
    print("📌 Test 1: JSearch API - Job Search")
    print("="*80)
    
    try:
        conn = http.client.HTTPSConnection("jsearch.p.rapidapi.com")
        
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "jsearch.p.rapidapi.com"
        }
        
        # Search for software engineer jobs
        conn.request("GET", "/search?query=Software%20Engineer&page=1&num_pages=1", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        
        print(f"✅ Status Code: {res.status}")
        
        if res.status == 200:
            result = json.loads(data.decode("utf-8"))
            jobs = result.get('data', [])
            
            print(f"✅ SUCCESS! Found {len(jobs)} jobs from JSearch Search")
            
            if jobs:
                print("\n📋 First 5 jobs:")
                for i, job in enumerate(jobs[:5], 1):
                    print(f"\n  Job {i}:")
                    print(f"    ID: {job.get('job_id', 'N/A')}")
                    print(f"    Title: {job.get('job_title', 'N/A')}")
                    print(f"    Company: {job.get('employer_name', 'N/A')}")
                    print(f"    Location: {job.get('job_city', 'N/A')}, {job.get('job_country', 'N/A')}")
                    print(f"    Type: {job.get('job_employment_type', 'N/A')}")
                    print(f"    Remote: {job.get('job_is_remote', False)}")
                
                conn.close()
                return True, jobs
        else:
            print(f"❌ Failed: {data.decode('utf-8')[:500]}")
            
        conn.close()
        return False, []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def test_jobs_api14_list():
    """Test Jobs API 14 - List jobs"""
    print("\n" + "="*80)
    print("📌 Test 2: Jobs API 14 - Job List")
    print("="*80)
    
    try:
        conn = http.client.HTTPSConnection("jobs-api14.p.rapidapi.com")
        
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "jobs-api14.p.rapidapi.com"
        }
        
        # List jobs with query
        conn.request("GET", "/v2/list?query=Software%20Engineer&location=United%20States&distance=1.0&language=en_US&remoteOnly=false&datePosted=month&employmentTypes=fulltime&index=0", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        
        print(f"✅ Status Code: {res.status}")
        
        if res.status == 200:
            result = json.loads(data.decode("utf-8"))
            jobs = result.get('jobs', []) or result.get('data', [])
            
            print(f"✅ SUCCESS! Found {len(jobs)} jobs from Jobs API 14")
            
            if jobs:
                print("\n📋 First 5 jobs:")
                for i, job in enumerate(jobs[:5], 1):
                    print(f"\n  Job {i}:")
                    print(f"    Title: {job.get('title', 'N/A')}")
                    print(f"    Company: {job.get('company', 'N/A')}")
                    print(f"    Location: {job.get('location', 'N/A')}")
                    print(f"    Type: {job.get('employmentType', 'N/A')}")
                
                conn.close()
                return True, jobs
        else:
            print(f"❌ Failed: {data.decode('utf-8')[:500]}")
            
        conn.close()
        return False, []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def main():
    print("\n" + "🚀"*40)
    print("TESTING JSEARCH & JOBS API 14")
    print("🚀"*40)
    print(f"\n🔑 Using API Key: {API_KEY[:20]}...")
    
    # Test JSearch
    success1, jobs1 = test_jsearch_search()
    
    # Test Jobs API 14
    success2, jobs2 = test_jobs_api14_list()
    
    # Summary
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80)
    
    if success1:
        print(f"✅ JSearch API: {len(jobs1)} jobs - WORKING!")
    else:
        print(f"❌ JSearch API: FAILED")
    
    if success2:
        print(f"✅ Jobs API 14: {len(jobs2)} jobs - WORKING!")
    else:
        print(f"❌ Jobs API 14: FAILED")
    
    total_jobs = len(jobs1) + len(jobs2)
    if total_jobs >= 10:
        print(f"\n🎉 SUCCESS! Total {total_jobs} jobs fetched!")
        return jobs1 + jobs2
    else:
        print(f"\n⚠️ Only {total_jobs} jobs fetched (need 10+)")
        return jobs1 + jobs2

if __name__ == "__main__":
    jobs = main()
    print(f"\n\n✅ Retrieved {len(jobs)} total jobs!")
