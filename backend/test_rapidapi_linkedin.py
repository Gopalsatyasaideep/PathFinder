"""
Test RapidAPI LinkedIn Job Search API directly
"""
import http.client
import json

def test_linkedin_api():
    """Test LinkedIn Job Search API with different endpoints"""
    
    API_KEY = "c0d23f9058msh4d8de44e3f0e86dp15ee2cjsn34acc712be7b"
    
    print("="*60)
    print("🧪 Testing RapidAPI LinkedIn Job Search")
    print("="*60)
    
    # Test 1: Active jobs from last 1 hour
    print("\n📌 Test 1: Active jobs from last 1 hour")
    print("-"*60)
    try:
        conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")
        
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "linkedin-job-search-api.p.rapidapi.com"
        }
        
        conn.request("GET", "/active-jb-1h?limit=10&offset=0&description_type=text", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        
        print(f"✅ Status Code: {res.status}")
        print(f"✅ Response Headers: {dict(res.headers)}")
        
        result = json.loads(data.decode("utf-8"))
        
        if isinstance(result, dict):
            if 'error' in result:
                print(f"❌ API Error: {result}")
            elif 'message' in result:
                print(f"⚠️ API Message: {result}")
            else:
                jobs_data = result.get('data', [])
                print(f"✅ Found {len(jobs_data)} jobs")
                
                if jobs_data:
                    print("\n📋 First 3 jobs:")
                    for i, job in enumerate(jobs_data[:3], 1):
                        print(f"\n  Job {i}:")
                        print(f"    Title: {job.get('title', 'N/A')}")
                        print(f"    Company: {job.get('company', 'N/A')}")
                        print(f"    Location: {job.get('location', 'N/A')}")
                        print(f"    URL: {job.get('url', 'N/A')[:80]}...")
        elif isinstance(result, list):
            print(f"✅ Found {len(result)} jobs (direct list)")
            if result:
                print("\n📋 First 3 jobs:")
                for i, job in enumerate(result[:3], 1):
                    print(f"\n  Job {i}:")
                    print(f"    Title: {job.get('title', 'N/A')}")
                    print(f"    Company: {job.get('company', 'N/A')}")
                    print(f"    Location: {job.get('location', 'N/A')}")
        else:
            print(f"⚠️ Unexpected response type: {type(result)}")
            print(f"Response: {str(result)[:200]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Active jobs from last 24 hours
    print("\n\n📌 Test 2: Active jobs from last 24 hours")
    print("-"*60)
    try:
        conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")
        
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "linkedin-job-search-api.p.rapidapi.com"
        }
        
        conn.request("GET", "/active-jb-24h?limit=10&offset=0&description_type=text", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        
        print(f"✅ Status Code: {res.status}")
        
        result = json.loads(data.decode("utf-8"))
        
        if isinstance(result, dict):
            if 'error' in result or 'message' in result:
                print(f"⚠️ Response: {result}")
            else:
                jobs_data = result.get('data', [])
                print(f"✅ Found {len(jobs_data)} jobs")
        elif isinstance(result, list):
            print(f"✅ Found {len(result)} jobs")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Try different endpoint - search by keyword
    print("\n\n📌 Test 3: Search by keyword (Software Engineer)")
    print("-"*60)
    try:
        conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")
        
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "linkedin-job-search-api.p.rapidapi.com"
        }
        
        # Try search endpoint if available
        conn.request("GET", "/search?keywords=Software%20Engineer&location=United%20States&limit=10", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        
        print(f"✅ Status Code: {res.status}")
        
        result = json.loads(data.decode("utf-8"))
        
        if isinstance(result, dict):
            if 'error' in result or 'message' in result:
                print(f"⚠️ Response: {result}")
            else:
                jobs_data = result.get('data', []) or result.get('jobs', [])
                print(f"✅ Found {len(jobs_data)} jobs")
                
                if jobs_data:
                    print("\n📋 Sample job:")
                    job = jobs_data[0]
                    print(f"  Title: {job.get('title', 'N/A')}")
                    print(f"  Company: {job.get('company', 'N/A')}")
                    print(f"  Location: {job.get('location', 'N/A')}")
        elif isinstance(result, list):
            print(f"✅ Found {len(result)} jobs")
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Search endpoint may not be available: {e}")
    
    # Test 4: Check API quota/status
    print("\n\n📌 Test 4: API Status Check")
    print("-"*60)
    try:
        conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")
        
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': "linkedin-job-search-api.p.rapidapi.com"
        }
        
        conn.request("GET", "/", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        
        print(f"✅ Status Code: {res.status}")
        print(f"Response: {data.decode('utf-8')[:300]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Status check: {e}")
    
    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60)
    print("\n💡 Notes:")
    print("  - If you see jobs, the API is working!")
    print("  - If you see 'error' or 'message', check API subscription")
    print("  - If you see 403/429, you may have hit rate limits")
    print("  - Check RapidAPI dashboard for usage limits")
    print("\n🔗 RapidAPI Dashboard:")
    print("   https://rapidapi.com/rockapis-rockapis-default/api/linkedin-job-search-api")

if __name__ == "__main__":
    test_linkedin_api()
