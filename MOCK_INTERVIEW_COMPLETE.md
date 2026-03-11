# Mock Interview Feature - Complete Documentation

## 🎯 Overview

The Mock Interview feature provides an AI-powered interview practice platform with:
- **Smart Question Generation**: 5-10 tailored questions based on job role and description
- **Fullscreen Test Environment**: Professional test interface similar to Unstop
- **Voice Readout**: Text-to-speech for realistic interview simulation
- **AI Evaluation**: Comprehensive feedback with scores and improvement suggestions

---

## 🚀 Features

### 1. Interview Setup Page (`/mock-interview`)
- **Input Fields**:
  - Interview Type: Technical, Behavioral, Case Study, HR, or Mixed
  - Job Role: Target position
  - Experience Level: Entry, Mid, or Senior
  - Job Description: Detailed requirements (minimum 50 characters)

- **AI Question Generation**:
  - Generates 5-10 context-aware questions
  - Questions include difficulty levels and expected points
  - Uses NVIDIA/OpenRouter AI for intelligent generation

### 2. Fullscreen Interview Screen (`/mock-interview/start`)
- **Test Environment Features**:
  - ✅ Fullscreen mode (like Unstop, HackerRank)
  - ✅ Voice readout of each question
  - ✅ Question navigation (previous/next)
  - ✅ Quick jump to any question
  - ✅ Timer tracking
  - ✅ Auto-save answers
  - ✅ Visual progress tracking
  - ✅ Answer status indicators

- **Voice Features**:
  - Automatic question readout on load
  - Manual replay button
  - Voice on/off toggle
  - Speech synthesis controls

- **Navigation**:
  - Previous/Next buttons
  - Quick navigation grid (shows answered/unanswered)
  - Submit button on last question

### 3. Results Page (`/mock-interview/results`)
- **Overall Score**:
  - Total score out of 100
  - Performance level (Excellent/Good/Average/Needs Improvement)
  - Animated circular progress

- **Detailed Feedback**:
  - Key strengths (top 3+)
  - Areas to improve (top 3+)
  - Overall performance analysis
  - Recommended next steps

- **Question-by-Question Breakdown**:
  - Individual scores (0-10)
  - Specific feedback per question
  - Strengths and improvements for each answer
  - Expandable sections for details

---

## 🔧 Technical Implementation

### Frontend Components

#### 1. MockInterview.jsx (`src/pages/MockInterview.jsx`)
Setup form component:
```jsx
- Interview type selection (5 types)
- Role and experience level inputs
- Job description textarea
- Form validation
- API call to generate questions
- Session storage for interview data
```

#### 2. MockInterviewScreen.jsx (`src/pages/MockInterviewScreen.jsx`)
Main interview interface:
```jsx
- Fullscreen API integration
- Web Speech API for text-to-speech
- Real-time timer
- Answer collection and time tracking
- Question navigation
- Progress tracking
- Session storage for answers
```

**Key Features**:
- **Voice Synthesis**: Uses Web Speech API
- **Fullscreen**: Uses Fullscreen API
- **Timer**: Updates every second
- **Auto-save**: Saves to session storage

#### 3. MockInterviewResults.jsx (`src/pages/MockInterviewResults.jsx`)
Results and feedback display:
```jsx
- API call to evaluate answers
- Animated score display
- Expandable question sections
- Retry and navigation options
```

### Backend Endpoints

#### 1. Generate Questions Endpoint
**POST** `/api/mock-interview/generate-questions`

**Request Body**:
```json
{
  "interviewType": "technical|behavioral|case-study|hr|mixed",
  "role": "Senior Software Engineer",
  "jobDescription": "Full job description text...",
  "experienceLevel": "mid",
  "questionCount": 7
}
```

**Response**:
```json
{
  "interview_id": "uuid-string",
  "questions": [
    {
      "id": 1,
      "question": "Question text",
      "type": "technical",
      "difficulty": "medium",
      "expectedPoints": ["point1", "point2", "point3"]
    }
  ],
  "totalQuestions": 7,
  "estimatedDuration": 17
}
```

#### 2. Evaluate Answers Endpoint
**POST** `/api/mock-interview/evaluate-answers`

**Request Body**:
```json
{
  "interview_id": "uuid-string",
  "interviewType": "technical",
  "role": "Senior Software Engineer",
  "answers": [
    {
      "questionId": 1,
      "answer": "User's answer text...",
      "timeSpent": 120
    }
  ]
}
```

**Response**:
```json
{
  "interview_id": "uuid-string",
  "questionEvaluations": [
    {
      "questionId": 1,
      "score": 8,
      "feedback": "Detailed feedback...",
      "strengths": ["strength1", "strength2"],
      "improvements": ["improvement1", "improvement2"]
    }
  ],
  "overallEvaluation": {
    "totalScore": 75,
    "averageScore": 7.5,
    "performance": "Good",
    "keyStrengths": ["strength1", "strength2", "strength3"],
    "areasToImprove": ["area1", "area2", "area3"],
    "detailedFeedback": "Overall feedback paragraph...",
    "nextSteps": ["step1", "step2", "step3"]
  }
}
```

### Backend Files

#### `backend/routers/mock_interview.py`
- Question generation logic
- Answer evaluation logic
- AI prompt engineering
- Fallback responses
- Error handling

**Key Functions**:
- `_build_question_generation_prompt()`: Creates AI prompt for questions
- `_parse_questions_from_response()`: Extracts questions from AI response
- `_build_evaluation_prompt()`: Creates AI prompt for evaluation
- `_parse_evaluation_from_response()`: Extracts evaluation from AI response
- `_get_fallback_questions()`: Provides default questions if AI fails
- `_get_fallback_evaluation()`: Provides default evaluation if AI fails

---

## 🎨 User Flow

### Step 1: Access Mock Interview
1. User logs in
2. Clicks "Mock Interview" in navbar
3. Lands on setup page

### Step 2: Setup Interview
1. Select interview type (Technical/Behavioral/etc.)
2. Enter job role
3. Select experience level
4. Paste job description (min 50 chars)
5. Click "Generate Interview Questions"
6. AI generates 5-10 questions (takes 5-15 seconds)

### Step 3: Start Interview
1. Review interview instructions
2. Click "Start Interview"
3. Optionally enable fullscreen mode
4. First question is read aloud automatically

### Step 4: Answer Questions
1. Listen to question (or replay)
2. Type answer in textarea
3. Navigate using Previous/Next buttons
4. Or use quick navigation grid
5. See progress bar and answered count
6. Review all answers before submitting

### Step 5: Submit & Evaluate
1. Click "Submit Interview"
2. Confirm if any questions unanswered
3. AI evaluates all answers (takes 10-30 seconds)
4. Redirected to results page

### Step 6: View Results
1. See overall score (0-100)
2. View performance level
3. Read key strengths and areas to improve
4. Expand individual questions for detailed feedback
5. Review recommended next steps
6. Try another interview or return to dashboard

---

## 🔊 Voice Feature Implementation

### Web Speech API
```javascript
const speechSynthesis = window.speechSynthesis;
const utterance = new SpeechSynthesisUtterance(questionText);
utterance.rate = 0.9;  // Slightly slower for clarity
utterance.pitch = 1;
utterance.volume = 1;
speechSynthesis.speak(utterance);
```

### Features:
- **Auto-play**: Questions read automatically on load
- **Replay**: Manual replay button for each question
- **Toggle**: Enable/disable voice globally
- **Visual indicator**: Pulsing animation when reading
- **Cancel on navigation**: Stops speech when changing questions

---

## 📱 Fullscreen Implementation

### Fullscreen API
```javascript
// Enter fullscreen
await containerRef.current?.requestFullscreen();

// Exit fullscreen
await document.exitFullscreen();

// Check fullscreen state
const isFullscreen = !!document.fullscreenElement;
```

### Benefits:
- Reduces distractions
- Professional test environment
- Better focus on questions
- Similar to real coding platforms

---

## 🎯 Scoring System

### Individual Question Scores (0-10)
- **9-10**: Excellent - Comprehensive, well-structured, shows deep understanding
- **7-8**: Good - Solid answer with relevant details
- **5-6**: Average - Basic understanding but lacks depth
- **3-4**: Below Average - Incomplete or lacks clarity
- **0-2**: Poor - Inadequate or off-topic

### Overall Performance (0-100)
- **90-100**: "Excellent" - Outstanding performance
- **75-89**: "Good" - Strong performance
- **60-74**: "Average" - Acceptable performance
- **Below 60**: "Needs Improvement" - Requires more preparation

---

## 🛠️ API Integration

### Frontend API Service (`src/services/api.js`)

```javascript
// Generate questions
generateInterviewQuestions: async (formData) => {
  const response = await api.post('/api/mock-interview/generate-questions', formData, {
    timeout: 60000, // 1 minute
  });
  return response.data;
}

// Evaluate answers
evaluateMockInterview: async (evaluationData) => {
  const response = await api.post('/api/mock-interview/evaluate-answers', evaluationData, {
    timeout: 120000, // 2 minutes
  });
  return response.data;
}
```

### Backend Router Registration (`backend/main.py`)
```python
from routers import mock_interview
app.include_router(mock_interview.router)
```

---

## 🎨 UI/UX Features

### Design Highlights
- **Gradient backgrounds**: Modern, professional look
- **Animated score circle**: Engaging visual feedback
- **Color-coded badges**: Quick visual understanding
- **Expandable sections**: Progressive disclosure of information
- **Responsive design**: Works on all screen sizes
- **Loading states**: Clear feedback during AI processing

### Color Coding
- **Green**: Strengths, good scores, answered questions
- **Orange/Yellow**: Areas to improve, medium scores
- **Red**: Poor scores, critical improvements
- **Blue/Indigo**: Primary actions, current question
- **Gray**: Inactive/unanswered questions

---

## 📋 Usage Instructions

### For Users

1. **Prepare Job Description**:
   - Copy full job posting
   - Include requirements, responsibilities, skills
   - Minimum 50 characters required

2. **During Interview**:
   - Use fullscreen for best experience
   - Take time to think before answering
   - Provide specific examples (STAR method)
   - Review all answers before submitting

3. **After Interview**:
   - Study the detailed feedback
   - Focus on areas to improve
   - Follow recommended next steps
   - Practice with different interview types

### For Developers

1. **Testing**:
   ```bash
   # Start backend
   cd backend
   python main.py
   
   # Start frontend
   npm run dev
   ```

2. **Customize Questions**:
   - Edit `_build_question_generation_prompt()` in `mock_interview.py`
   - Adjust question count (5-10)
   - Modify difficulty levels

3. **Customize Evaluation**:
   - Edit `_build_evaluation_prompt()` in `mock_interview.py`
   - Adjust scoring criteria
   - Modify performance thresholds

---

## 🔐 Security & Privacy

- Interviews stored in **session storage** only (cleared on tab close)
- No permanent storage of interview answers
- User authentication required
- API rate limiting recommended for production

---

## 🐛 Error Handling

### Frontend
- Form validation before submission
- Loading states during API calls
- Error alerts for failed requests
- Graceful fallback to home page

### Backend
- Try-catch blocks around AI calls
- Fallback questions if AI fails
- Fallback evaluations if parsing fails
- Comprehensive error logging

---

## 🚀 Future Enhancements

### Potential Features
1. **Video Recording**: Record user's video during interview
2. **Voice Recognition**: Allow voice answers instead of typing
3. **Interview History**: Save past interviews for review
4. **Practice Mode**: Timed vs untimed options
5. **Company-Specific**: Pre-set questions for major companies
6. **Peer Comparison**: Anonymous score benchmarking
7. **Mock Interviewer Avatar**: AI video interviewer
8. **Real-time Hints**: Contextual tips during answering
9. **Export Results**: PDF report generation
10. **Interview Scheduling**: Calendar integration

---

## 📊 Performance Metrics

### API Response Times
- Question Generation: 5-15 seconds
- Answer Evaluation: 10-30 seconds
- Session Storage: Instant

### Timeouts
- Question Generation: 60 seconds
- Answer Evaluation: 120 seconds

---

## 🎓 Best Practices

### For Interview Takers
1. **Research the Role**: Understand job requirements
2. **Use STAR Method**: Situation, Task, Action, Result
3. **Be Specific**: Provide concrete examples
4. **Stay Calm**: Take time to think
5. **Review Thoroughly**: Check all answers before submitting

### For Interview Creators
1. **Clear Questions**: Avoid ambiguity
2. **Relevant Examples**: Match industry standards
3. **Balanced Difficulty**: Mix easy, medium, hard
4. **Constructive Feedback**: Focus on improvement

---

## 📝 Configuration

### Environment Variables
```env
# Already configured in your existing setup
NVIDIA_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

### Frontend Configuration
```javascript
// src/services/api.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

### Backend Configuration
```python
# backend/routers/mock_interview.py
DEFAULT_QUESTION_COUNT = 7
MIN_QUESTIONS = 5
MAX_QUESTIONS = 10
```

---

## 🎉 Success!

Your Mock Interview feature is now fully implemented with:
✅ Navbar integration (visible after login)
✅ Setup form with validation
✅ AI question generation
✅ Fullscreen test environment
✅ Voice readout (text-to-speech)
✅ Answer collection and tracking
✅ AI evaluation
✅ Detailed results and feedback

### Quick Start
1. Login to the application
2. Click "Mock Interview" in navbar
3. Fill out the interview setup form
4. Start practicing!

---

## 📞 Support

For issues or questions:
- Check browser console for errors
- Verify AI API keys are configured
- Ensure backend server is running
- Check network requests in DevTools

---

**Happy Interviewing! 🎯**
