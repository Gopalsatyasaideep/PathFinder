"""
Simple test script for PathFinder AI Resume Parser API

Usage:
    python test_api.py [path_to_resume_file]
"""

import requests
import sys
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


def test_health():
    """Test the health endpoint"""
    print("=" * 50)
    print("Testing Health Endpoint...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("Make sure the backend server is running on http://localhost:8000")
        return False


def test_root():
    """Test the root endpoint"""
    print("\n" + "=" * 50)
    print("Testing Root Endpoint...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint works!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_upload(file_path):
    """Test the upload endpoint"""
    print("\n" + "=" * 50)
    print("Testing Upload Endpoint...")
    print("=" * 50)
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    file_ext = Path(file_path).suffix.lower()
    if file_ext not in ['.pdf', '.docx']:
        print(f"❌ Invalid file type: {file_ext}. Only PDF and DOCX are supported.")
        return False
    
    print(f"Uploading file: {file_path}")
    print(f"File type: {file_ext}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, f'application/{file_ext[1:]}')}
            response = requests.post(f"{BASE_URL}/upload-resume", files=files)
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            print("\nParsed Resume Data:")
            print(json.dumps(response.json(), indent=2))
            
            # Display summary
            data = response.json()
            print("\n" + "-" * 50)
            print("Summary:")
            print("-" * 50)
            print(f"Name: {data.get('name', 'Not found')}")
            print(f"Skills Found: {len(data.get('skills', []))}")
            print(f"Education Entries: {len(data.get('education', []))}")
            print(f"Experience Entries: {len(data.get('experience', []))}")
            
            return True
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return False


def test_error_cases():
    """Test error handling"""
    print("\n" + "=" * 50)
    print("Testing Error Cases...")
    print("=" * 50)
    
    # Test invalid file type
    print("\n1. Testing invalid file type...")
    try:
        files = {'file': ('test.txt', b'fake content', 'text/plain')}
        response = requests.post(f"{BASE_URL}/upload-resume", files=files)
        if response.status_code == 400:
            print("✅ Invalid file type correctly rejected")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test missing file
    print("\n2. Testing missing file...")
    try:
        response = requests.post(f"{BASE_URL}/upload-resume")
        if response.status_code >= 400:
            print("✅ Missing file correctly handled")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main test function"""
    print("\n" + "=" * 50)
    print("PathFinder AI - Resume Parser API Test")
    print("=" * 50)
    
    # Test health and root endpoints
    health_ok = test_health()
    root_ok = test_root()
    
    if not health_ok:
        print("\n❌ Server is not running. Please start the backend server first.")
        print("Run: cd backend && python main.py")
        sys.exit(1)
    
    # Test upload if file path provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        test_upload(file_path)
    else:
        print("\n" + "=" * 50)
        print("No resume file provided for upload test.")
        print("Usage: python test_api.py <path_to_resume_file>")
        print("=" * 50)
    
    # Test error cases
    test_error_cases()
    
    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
