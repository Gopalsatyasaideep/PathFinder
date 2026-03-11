"""
Simple test server without heavy dependencies
"""
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI

# Add backend directory to path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Simple app
app = FastAPI(title="PathFinder AI Test")

@app.get("/")
def root():
    return {"message": "PathFinder AI Test Server", "status": "running"}

@app.get("/test-nvidia")
def test_nvidia():
    try:
        from services.nvidia_client import get_nvidia_client
        client = get_nvidia_client()
        if not client:
            return {"status": "error", "message": "NVIDIA client not available"}
        
        response = client.generate_text("Say hello!", max_tokens=20)
        return {"status": "success", "nvidia_response": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("🚀 Starting PathFinder AI Test Server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)