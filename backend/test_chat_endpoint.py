"""
Quick test script for the chat endpoint with NVIDIA API
"""

import requests
import json

# Test the chat endpoint
def test_chat():
    url = "http://localhost:8000/chat"
    
    # Simple test payload
    payload = {
        "question": "What are the key skills for a software engineer?",
        "resume_json": None,
        "skill_gap_report": None,
        "job_recommendations": None
    }
    
    print("Testing chat endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS!")
            print(f"Question: {result.get('question', 'N/A')}")
            print(f"Answer: {result.get('answer', 'N/A')[:200]}...")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    test_chat()
