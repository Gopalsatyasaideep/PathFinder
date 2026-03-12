"""
Test script to verify backend connectivity and auth endpoints
Run this after deploying to Render to test the API
"""

import requests
import json
import time

# Backend URL - update this to your Render URL
BACKEND_URL = "https://pathfinderai2026-1.onrender.com"

def test_health():
    """Test the health endpoint"""
    print("\n" + "="*50)
    print("1. Testing /health endpoint...")
    print("="*50)
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_root():
    """Test the root endpoint"""
    print("\n" + "="*50)
    print("2. Testing / (root) endpoint...")
    print("="*50)
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_signup():
    """Test the signup endpoint"""
    print("\n" + "="*50)
    print("3. Testing /auth/signup endpoint...")
    print("="*50)
    
    # Use unique email to avoid conflicts
    test_email = f"test{int(time.time())}@example.com"
    
    payload = {
        "name": "Test User",
        "email": test_email,
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Signup successful!")
            print(f"User ID: {data.get('user', {}).get('id')}")
            print(f"Token received: {'Yes' if data.get('access_token') else 'No'}")
            return True
        else:
            print(f"Signup failed")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test the login endpoint"""
    print("\n" + "="*50)
    print("4. Testing /auth/login endpoint...")
    print("="*50)
    
    # Use a test account - you may need to create one first
    payload = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Login successful!")
            print(f"User ID: {data.get('user', {}).get('id')}")
            print(f"Token received: {'Yes' if data.get('access_token') else 'No'}")
            return True
        elif response.status_code == 401:
            print(f"Invalid credentials (expected for test account)")
            return None  # Not a failure, just means no test user exists
        else:
            print(f"Login failed")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_cors():
    """Test CORS configuration"""
    print("\n" + "="*50)
    print("5. Testing CORS configuration...")
    print("="*50)
    
    # Test preflight request
    try:
        response = requests.options(
            f"{BACKEND_URL}/auth/login",
            headers={
                "Origin": "https://pathfinderai-psi.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin", "Not set"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods", "Not set"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers", "Not set"),
        }
        
        print(f"Status: {response.status_code}")
        print("CORS Headers:")
        for key, value in cors_headers.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"Error testing CORS: {e}")
        return False

def main():
    print("="*50)
    print("PathFinder AI - Backend Deployment Test")
    print("="*50)
    print(f"Backend URL: {BACKEND_URL}")
    
    results = {}
    
    # Run tests
    results["health"] = test_health()
    results["root"] = test_root()
    results["cors"] = test_cors()
    results["signup"] = test_signup()
    results["login"] = test_login()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL" if result == False else "SKIP"
        print(f"{test_name.upper()}: {status}")
        if result == False:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("All tests passed! Backend is working correctly.")
    else:
        print("Some tests failed. Check the errors above.")
    print("="*50)

if __name__ == "__main__":
    main()

