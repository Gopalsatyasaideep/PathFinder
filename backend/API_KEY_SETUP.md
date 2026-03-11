# OpenRouter API Key Setup

## Quick Setup

To use AI-powered job recommendations and chatbot features, you need to set your OpenRouter API key.

### Option 1: Set API Key in Code (Recommended for Quick Testing)

1. Open `backend/services/openrouter_client.py`
2. Find the line: `DEFAULT_API_KEY = ""`
3. Add your API key:
   ```python
   DEFAULT_API_KEY = "sk-or-v1-your-api-key-here"
   ```
4. Save the file and restart the backend server

### Option 2: Set API Key via Environment Variable

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY = "sk-or-v1-your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

## Get Your Free API Key

1. Visit https://openrouter.ai/keys
2. Sign up for a free account (no credit card required)
3. Create a new API key
4. Copy the key (starts with `sk-or-v1-`)

## What This Enables

✅ **AI-Powered Job Recommendations**: Generates diverse, personalized job recommendations based on each resume (not just the 3 static job files)

✅ **Smart Chatbot**: Provides intelligent career guidance using OpenRouter's free models

✅ **Learning Path Generation**: Creates detailed learning outcomes using AI

## Fallback Behavior

If no API key is set:
- Job recommendations will use vector store matching (limited to 3 static jobs)
- Chatbot will use simple keyword-based responses
- Learning path will use template-based outcomes

The system will still work, but with reduced functionality.

