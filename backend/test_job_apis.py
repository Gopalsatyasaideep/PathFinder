"""
Test script to verify job fetching from multiple APIs
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.web_job_scraper import WebJobScraper

def test_job_apis():
    print("=" * 60)
    print("🧪 Testing Job API Integration")
    print("=" * 60)
    
    scraper = WebJobScraper()
    
    # Check which APIs have keys
    print("\n📊 API Configuration Status:")
    print("-" * 60)
    
    apis_status = {
        "The Muse": "✅ Active (no key required)",
        "RemoteOK": "✅ Active (no key required)",
        "Arbeitnow": "✅ Active (no key required)",
        "Adzuna": "✅ Active" if (scraper.adzuna_app_id and scraper.adzuna_app_key) else "⚠️  No API key",
        "JSearch (RapidAPI)": "✅ Active" if scraper.rapidapi_key else "⚠️  No API key (RECOMMENDED)",
        "Reed UK": "✅ Active" if scraper.reed_api_key else "⚠️  No API key",
        "USAJobs": "✅ Active" if scraper.usajobs_api_key else "⚠️  No API key",
    }
    
    active_count = sum(1 for status in apis_status.values() if "✅" in status)
    
    for api, status in apis_status.items():
        print(f"{api:25} {status}")
    
    print("-" * 60)
    print(f"Total Active APIs: {active_count}/7")
    print()
    
    # Test search
    print("🔍 Testing Job Search: 'Software Engineer' (remote)")
    print("-" * 60)
    
    try:
        jobs = scraper.search_jobs(
            query="Software Engineer",
            location="remote",
            max_results=15
        )
        
        print(f"\n✅ Successfully fetched {len(jobs)} jobs")
        print("\nJob Results:")
        print("=" * 60)
        
        for idx, job in enumerate(jobs, 1):
            print(f"\n{idx}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Source: {job['source']}")
            print(f"   URL: {job['url'][:80]}..." if len(job['url']) > 80 else f"   URL: {job['url']}")
        
        print("\n" + "=" * 60)
        
        # Analyze results by source
        sources = {}
        for job in jobs:
            source = job['source']
            sources[source] = sources.get(source, 0) + 1
        
        print("\n📈 Results by Source:")
        print("-" * 60)
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"{source:25} {count} jobs")
        
        print("\n" + "=" * 60)
        
        if len(jobs) >= 10:
            print("✅ SUCCESS: Fetched 10+ jobs as required!")
        else:
            print(f"⚠️  WARNING: Only {len(jobs)} jobs fetched.")
            print("\n💡 Recommendation:")
            print("   Add RAPIDAPI_KEY to your .env file for 10+ jobs")
            print("   Get free key at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_job_apis()
