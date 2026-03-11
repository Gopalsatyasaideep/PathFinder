# 🚀 PathFinder AI - Enhanced Setup Guide

## 🎯 What This Project Does

**PathFinder AI** is an intelligent career guidance platform that:

- **📄 Resume Analysis** - Parses PDF/DOCX resumes and extracts skills, experience, education
- **🤖 AI-Powered Insights** - Uses NVIDIA's advanced Qwen model for deep analysis  
- **💼 Job Recommendations** - Generates personalized job matches based on your profile
- **📚 Learning Paths** - Creates custom skill development roadmaps
- **💬 Career Chat** - Interactive guidance for career planning
- **📊 Skills Gap Analysis** - Identifies missing skills for target roles

## 🏗 Enhanced AI Architecture

### **Primary AI Service: NVIDIA API**
- **Model**: Qwen 3 Next 80B (Advanced reasoning & analysis)
- **Use Cases**: Resume analysis, job recommendations, learning paths
- **Quality**: Premium AI responses with better context understanding

### **Fallback Service: OpenRouter** 
- **Models**: Llama 3.2, Gemma 2, Mistral 7B (Free tier)
- **Use Cases**: Basic chatbot, backup for NVIDIA API
- **Reliability**: Automatic fallback if NVIDIA API is unavailable

## ⚡ Quick Setup

### 1. **Backend Setup**

```powershell
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Install spaCy model for text processing
python -m spacy download en_core_web_sm

# Set up your API keys (choose one or both):

# Option A: NVIDIA API (Recommended for best results)
$env:NVIDIA_API_KEY="your-nvidia-api-key-here"

# Option B: OpenRouter API (Free alternative)  
$env:OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Start backend server
python main.py
```

**Backend will run on**: `http://localhost:8000`

### 2. **Frontend Setup**

```powershell
# In a new terminal, navigate to project root
cd ..

# Install dependencies
npm install

# Start frontend
npm run dev  
```

**Frontend will run on**: `http://localhost:5173`

## 🔑 API Key Setup

### **NVIDIA API (Premium Features)**

1. **Get API Key**: 
   - Visit [NVIDIA AI Platform](https://build.nvidia.com/explore/discover)
   - Sign up and get your API key
   - Format: `nvapi-abc123...`

2. **Set Environment Variable**:
   ```powershell
   $env:NVIDIA_API_KEY="your-nvidia-api-key"
   ```

3. **Test Integration**:
   ```powershell
   cd backend
   python test_nvidia_integration.py
   ```

### **OpenRouter API (Free Fallback)**

1. **Get API Key**:
   - Visit [OpenRouter](https://openrouter.ai/keys) 
   - Sign up for free account
   - Format: `sk-or-v1-abc123...`

2. **Set Environment Variable**:
   ```powershell
   $env:OPENROUTER_API_KEY="sk-or-v1-your-key"
   ```

## 🧪 Test Your Setup

```powershell
cd backend
python test_nvidia_integration.py
```

This will test:
- ✅ API connectivity
- ✅ Resume analysis functionality  
- ✅ Job recommendations
- ✅ Learning path generation
- ✅ Fallback mechanisms

## 🌐 Access Your Application

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | `http://localhost:5173` | Main user interface |
| **API Docs** | `http://localhost:8000/docs` | Interactive API documentation |
| **Health Check** | `http://localhost:8000/health` | Server status |

## 🔄 How It Works

### **1. Resume Upload & Analysis**
```
📄 Upload Resume → 🤖 AI Analysis → 📊 Skills Extraction → 💡 Insights
```

### **2. Job Recommendations** 
```
👤 Profile Data → 🧠 NVIDIA AI → 💼 Personalized Jobs → 📈 Match Scores
```

### **3. Learning Path Generation**
```
🎯 Target Role → 📚 Skill Gaps → 🗺️ Learning Roadmap → ⏱️ Timeline
```

### **4. AI Service Flow**
```
🥇 Try NVIDIA API → ❌ If fails → 🥈 Try OpenRouter → ❌ If fails → 🛡️ Basic Fallback
```

## 🎯 Key Features

### **Enhanced Resume Analysis** 
- **Strengths Identification**: AI-powered skill recognition
- **Career Level Assessment**: Entry/Mid/Senior classification  
- **Industry Fit Analysis**: Best matching sectors
- **Improvement Suggestions**: Actionable recommendations

### **Intelligent Job Matching**
- **Personalized Recommendations**: Based on full profile analysis
- **Match Scoring**: Percentage compatibility ratings
- **Salary Insights**: Expected compensation ranges
- **Growth Potential**: Career progression analysis

### **Smart Learning Paths**
- **Skill Gap Identification**: Missing skills for target roles
- **Phase-based Learning**: Foundation → Intermediate → Advanced
- **Time Estimates**: Realistic timeline projections
- **Resource Curation**: Recommended courses and materials

## 🔧 Advanced Configuration

### **Environment Variables**
```bash
# AI Service Configuration
NVIDIA_API_KEY=your-nvidia-key
OPENROUTER_API_KEY=your-openrouter-key
PREFER_NVIDIA_API=true

# AI Model Settings  
AI_TEMPERATURE=0.6
AI_MAX_TOKENS=4096

# Application Settings
BACKEND_HOST=localhost
BACKEND_PORT=8000
LOG_LEVEL=INFO
```

### **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload-resume` | POST | Upload and parse resume |
| `/analyze-profile` | POST | Full AI-powered analysis |
| `/analyze-profile/quick-analysis` | POST | Quick AI insights |
| `/recommendations/jobs` | POST | Get job recommendations |
| `/learning-path/generate` | POST | Generate learning path |
| `/chat` | POST | Career guidance chat |

## 🚨 Troubleshooting

### **Common Issues**

1. **"NVIDIA API key required"**
   - Set `NVIDIA_API_KEY` environment variable
   - Or configure OpenRouter as fallback

2. **"spaCy model not found"** 
   ```powershell
   python -m spacy download en_core_web_sm
   ```

3. **"Port 8000 already in use"**
   ```powershell
   # Kill existing process
   taskkill /f /im python.exe
   ```

4. **"AI analysis temporarily unavailable"**
   - Check API key configuration
   - Verify internet connectivity
   - System will use basic fallback

### **Debug Mode**
```powershell
$env:DEBUG_MODE="true"
$env:LOG_LEVEL="DEBUG"
python main.py
```

## 🎉 Success! Your AI Career Assistant is Ready

1. **Upload a resume** at `http://localhost:5173`
2. **Get AI-powered insights** with career recommendations  
3. **Explore job matches** with detailed compatibility scores
4. **Follow personalized learning paths** to advance your career
5. **Chat with the AI assistant** for ongoing guidance

## 💡 Pro Tips

- **Use NVIDIA API** for the most accurate and detailed analysis
- **Set both API keys** for maximum reliability with automatic fallback
- **Upload detailed resumes** for better AI analysis quality
- **Specify clear target roles** for more precise recommendations
- **Review learning paths regularly** as you develop new skills

---

**🚀 Happy career building with PathFinder AI!**