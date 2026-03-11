# OpenRouter API Integration

PathFinder AI now uses OpenRouter's free API for chatbot and learning path generation, providing faster and more reliable responses without requiring local model downloads or GPU resources.

## What Changed

### Chatbot (`/chat` endpoint)
- **Before**: Used local FLAN-T5 model (slow, requires model download)
- **After**: Uses OpenRouter API with free models (fast, no local setup needed)
- **Fallback**: If OpenRouter is unavailable, falls back to local FLAN-T5 or simple responses

### Learning Path (`/learning-path` endpoint)
- **Before**: Used local FLAN-T5 for generating learning outcomes (optional)
- **After**: Uses OpenRouter API for better learning outcome descriptions
- **Fallback**: If OpenRouter is unavailable, uses template-based outcomes

## Setup Instructions

### 1. Get OpenRouter API Key

1. Visit https://openrouter.ai/keys
2. Sign up for a free account (no credit card required)
3. Create an API key
4. Copy your API key

### 2. Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY = "sk-or-v1-..."
```

**Windows (Command Prompt):**
```cmd
set OPENROUTER_API_KEY=sk-or-v1-...
```

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY=sk-or-v1-...
```

**Or add to your shell profile** (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export OPENROUTER_API_KEY=sk-or-v1-...
```

### 3. Restart Backend Server

After setting the environment variable, restart your FastAPI server:
```bash
python main.py
```

## Available Free Models

The system uses these free models by default (in order of preference):

1. `meta-llama/llama-3.2-3b-instruct:free` (default)
2. `google/gemma-2-2b-it:free`
3. `microsoft/phi-3-mini-128k-instruct:free`
4. `mistralai/mistral-7b-instruct:free`

You can change the model by setting the `OPENROUTER_MODEL` environment variable or modifying the config in the code.

## How It Works

1. **Chatbot Flow:**
   - User asks a question
   - System retrieves relevant context from FAISS vector store
   - Context is sent to OpenRouter API with the question
   - OpenRouter generates a response using the free model
   - Response is returned to the user

2. **Learning Path Flow:**
   - System identifies missing skills
   - Retrieves learning resources from FAISS
   - For each skill, generates learning outcomes using OpenRouter
   - Returns structured learning path with AI-generated descriptions

## Fallback Behavior

If OpenRouter API key is not set or API calls fail:

- **Chatbot**: Falls back to local FLAN-T5 model (if available) or simple keyword-based responses
- **Learning Path**: Uses template-based outcomes instead of AI-generated ones

The system gracefully degrades, so it will still work without OpenRouter, just with reduced functionality.

## Troubleshooting

### "OpenRouter API key is required" error

**Solution**: Set the `OPENROUTER_API_KEY` environment variable before starting the server.

### API calls timing out

**Solution**: 
- Check your internet connection
- Verify your API key is valid at https://openrouter.ai/keys
- Check OpenRouter status page for service issues

### Getting rate limit errors

**Solution**: 
- Free tier has rate limits
- Wait a few seconds between requests
- Consider upgrading to a paid plan if you need higher limits

## Benefits

✅ **No local model downloads** - No need to download multi-GB model files  
✅ **Faster responses** - API calls are typically faster than local inference  
✅ **No GPU required** - Works on any machine with internet  
✅ **Better quality** - Free models on OpenRouter are well-optimized  
✅ **Easy updates** - Can switch models without code changes  

## Cost

OpenRouter's free tier provides:
- Access to free models (no cost)
- Limited rate limits (sufficient for development/testing)
- No credit card required

For production use with higher limits, consider OpenRouter's paid plans.

