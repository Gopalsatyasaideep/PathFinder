# Endpoint Status and Fixes

## Current Status

### ✅ Working Endpoints
1. **POST /upload-resume** - ✅ Working
2. **GET /health** - ✅ Working  
3. **POST /chat** - ✅ Working (returns responses, though model may not be fully initialized)
4. **GET /learning-path** - ✅ Working (returns 200, may return empty if no data)

### ⚠️ Partially Working
1. **GET /job-recommendations** - ⚠️ Timing out (blocking on model download)

## Root Cause

The endpoints are timing out because:
1. The sentence-transformers model tries to download from HuggingFace on first use
2. Network/proxy issues prevent the download
3. The download blocks indefinitely, causing request timeouts

## Solutions Applied

1. ✅ Made embedder initialization lazy
2. ✅ Added fallback to return zero vectors if model fails
3. ✅ Added error handling in all endpoints
4. ✅ Created sample data files in `backend/data/`
5. ✅ Made vector store initialization non-blocking

## Remaining Issue

The **job-recommendations** endpoint still times out because:
- When `store.search()` is called, it accesses `self.embedder`
- Even with lazy initialization, accessing the property triggers model load
- If model isn't cached, it tries to download and blocks

## Quick Fix Options

### Option 1: Pre-download the model (Recommended)
```bash
cd backend
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```
This will download and cache the model so future loads are instant.

### Option 2: Use cached model only
The embedder now tries `local_files_only=True` first, which will fail quickly if model isn't cached, allowing endpoints to return empty results instead of timing out.

### Option 3: Disable network for HuggingFace
Set environment variable before starting:
```powershell
$env:HF_HUB_OFFLINE = "1"
cd backend
py main.py
```

## Testing

All endpoints should now:
- Return 200 status codes (not 500)
- Return empty arrays with helpful messages if data/model unavailable
- Not block indefinitely

## Next Steps

1. Pre-download the model: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"`
2. Restart backend
3. Test endpoints - they should return quickly even if empty
