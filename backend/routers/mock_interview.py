"""
Mock Interview Router

Handles mock interview question generation and answer evaluation
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from services.orchestrator import Orchestrator, get_orchestrator
from pymongo import MongoClient
from datetime import datetime
import json
import logging
import jwt
import os

router = APIRouter(prefix="/api/mock-interview", tags=["Mock Interview"])
logger = logging.getLogger("pathfinder.mock_interview")

# MongoDB connection
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "pathfinder"
INTERVIEWS_COLLECTION = "mock_interviews"

# JWT config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# Database helper
def get_db():
    """Get MongoDB database connection"""
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    return db

# Authentication dependency
async def get_current_user(authorization: str = Header(None)):
    """Extract user from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from "Bearer <token>" format
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization
        
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"user_id": user_id, "email": email}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


class InterviewRequest(BaseModel):
    """Request model for generating interview questions"""
    interviewType: str = Field(..., description="Type of interview (technical, behavioral, case-study, hr, mixed)")
    role: str = Field(..., description="Job role/position")
    jobDescription: str = Field(..., description="Detailed job description")
    experienceLevel: str = Field(default="mid", description="Experience level (entry, mid, senior)")
    questionCount: int = Field(default=7, ge=5, le=10, description="Number of questions to generate")


class Question(BaseModel):
    """Interview question model"""
    id: int
    question: str
    type: str
    difficulty: str
    expectedPoints: List[str]


class InterviewQuestionsResponse(BaseModel):
    """Response model for generated interview questions"""
    interview_id: str
    questions: List[Question]
    totalQuestions: int
    estimatedDuration: int  # in minutes


class Answer(BaseModel):
    """User's answer to a question"""
    questionId: int
    answer: str
    timeSpent: int  # in seconds


class EvaluationRequest(BaseModel):
    """Request model for evaluating interview answers"""
    interview_id: str
    interviewType: str
    role: str
    answers: List[Answer]


class QuestionEvaluation(BaseModel):
    """Evaluation for a single question"""
    questionId: int
    score: int  # 0-10
    isCorrect: bool = True  # Whether the answer is correct
    feedback: str
    correctAnswer: str = ""  # The correct/expected answer
    strengths: List[str]
    improvements: List[str]


class OverallEvaluation(BaseModel):
    """Overall interview evaluation"""
    totalScore: int  # 0-100
    averageScore: float
    performance: str  # Excellent, Good, Average, Needs Improvement
    keyStrengths: List[str]
    areasToImprove: List[str]
    detailedFeedback: str
    nextSteps: List[str]


class EvaluationResponse(BaseModel):
    """Response model for interview evaluation"""
    interview_id: str
    questions: List[Question]  # Original questions for display
    questionEvaluations: List[QuestionEvaluation]
    overallEvaluation: OverallEvaluation


@router.post("/generate-questions", response_model=InterviewQuestionsResponse)
async def generate_questions(
    request: InterviewRequest,
    current_user: dict = Depends(get_current_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """
    Generate interview questions based on role and job description
    Requires authentication - saves interview to database
    """
    try:
        logger.info(f"Generating {request.questionCount} {request.interviewType} questions for {request.role} (user: {current_user['email']})")
        
        # Build the prompt for AI
        prompt = _build_question_generation_prompt(request)
        
        # Get response from AI using NVIDIA client directly
        from services.nvidia_client import get_nvidia_client
        nvidia_client = get_nvidia_client()
        
        if not nvidia_client:
            # Fallback to OpenRouter
            from services.openrouter_client import get_openrouter_client
            openrouter_client = get_openrouter_client()
            if openrouter_client:
                ai_response = openrouter_client.generate_with_fallback(
                    prompt=prompt,
                    max_tokens=2000,
                    temperature=0.3
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="No AI service available. Please configure NVIDIA_API_KEY or OPENROUTER_API_KEY."
                )
        else:
            # Use specialized method that selects the right model
            ai_response = nvidia_client.generate_interview_questions(
                prompt=prompt,
                interview_type=request.interviewType,
                temperature=0.3,
                max_tokens=2000
            )
        
        # Parse the response
        questions = _parse_questions_from_response(ai_response, request.questionCount)
        
        # Generate interview ID
        import uuid
        interview_id = str(uuid.uuid4())
        
        # Calculate estimated duration (2-3 minutes per question)
        estimated_duration = len(questions) * 2.5
        
        # Save interview to database
        db = get_db()
        interviews_collection = db[INTERVIEWS_COLLECTION]
        
        interview_doc = {
            "interview_id": interview_id,
            "user_id": current_user["user_id"],
            "user_email": current_user["email"],
            "interviewType": request.interviewType,
            "role": request.role,
            "jobDescription": request.jobDescription,
            "experienceLevel": request.experienceLevel,
            "questions": [q.dict() for q in questions],
            "totalQuestions": len(questions),
            "estimatedDuration": int(estimated_duration),
            "answers": None,
            "totalScore": None,
            "averageScore": None,
            "performance": None,
            "keyStrengths": None,
            "areasToImprove": None,
            "detailedFeedback": None,
            "nextSteps": None,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "status": "generated"
        }
        
        interviews_collection.insert_one(interview_doc)
        logger.info(f"Interview {interview_id} saved to database for user {current_user['email']}")
        
        return InterviewQuestionsResponse(
            interview_id=interview_id,
            questions=questions,
            totalQuestions=len(questions),
            estimatedDuration=int(estimated_duration)
        )
        
    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")


@router.post("/evaluate-answers", response_model=EvaluationResponse)
async def evaluate_answers(
    request: EvaluationRequest,
    current_user: dict = Depends(get_current_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """
    Evaluate user's answers and provide detailed feedback
    Requires authentication - updates interview in database
    """
    try:
        logger.info(f"Evaluating {len(request.answers)} answers for interview {request.interview_id} (user: {current_user['email']})")
        
        # Verify interview belongs to user
        db = get_db()
        interviews_collection = db[INTERVIEWS_COLLECTION]
        
        interview = interviews_collection.find_one({
            "interview_id": request.interview_id,
            "user_id": current_user["user_id"]
        })
        
        if not interview:
            raise HTTPException(
                status_code=404,
                detail="Interview not found or does not belong to current user"
            )
        
        # Build evaluation prompt with original questions from database
        prompt = _build_evaluation_prompt(request, interview)
        
        # Get AI evaluation using NVIDIA client directly
        from services.nvidia_client import get_nvidia_client
        nvidia_client = get_nvidia_client()
        
        if not nvidia_client:
            # Fallback to OpenRouter
            from services.openrouter_client import get_openrouter_client
            openrouter_client = get_openrouter_client()
            if openrouter_client:
                ai_response = openrouter_client.generate_with_fallback(
                    prompt=prompt,
                    max_tokens=3000,
                    temperature=0.3
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="No AI service available. Please configure NVIDIA_API_KEY or OPENROUTER_API_KEY."
                )
        else:
            # Use specialized method that selects the right model
            ai_response = nvidia_client.evaluate_interview_answers(
                prompt=prompt,
                interview_type=request.interviewType,
                temperature=0.3,
                max_tokens=3000
            )
        
        # Parse evaluation from response
        evaluation = _parse_evaluation_from_response(ai_response, len(request.answers))
        
        # Update interview in database with evaluation results
        answers_with_evaluation = []
        for ans, eval_data in zip(request.answers, evaluation['question_evaluations']):
            answers_with_evaluation.append({
                "questionId": ans.questionId,
                "answer": ans.answer,
                "timeSpent": ans.timeSpent,
                "score": eval_data.score,
                "isCorrect": eval_data.isCorrect,
                "feedback": eval_data.feedback,
                "correctAnswer": eval_data.correctAnswer,
                "strengths": eval_data.strengths,
                "improvements": eval_data.improvements
            })
        
        overall = evaluation['overall_evaluation']
        update_doc = {
            "$set": {
                "answers": answers_with_evaluation,
                "totalScore": overall.totalScore,
                "averageScore": overall.averageScore,
                "performance": overall.performance,
                "keyStrengths": overall.keyStrengths,
                "areasToImprove": overall.areasToImprove,
                "detailedFeedback": overall.detailedFeedback,
                "nextSteps": overall.nextSteps,
                "completed_at": datetime.utcnow(),
                "status": "completed"
            }
        }
        
        interviews_collection.update_one(
            {"interview_id": request.interview_id},
            update_doc
        )
        
        logger.info(f"Interview {request.interview_id} evaluation saved to database")
        
        # Convert questions from dict to Question objects
        questions_list = [Question(**q) for q in interview.get('questions', [])]
        
        return EvaluationResponse(
            interview_id=request.interview_id,
            questions=questions_list,
            questionEvaluations=evaluation['question_evaluations'],
            overallEvaluation=evaluation['overall_evaluation']
        )
        
    except Exception as e:
        logger.error(f"Error evaluating answers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate answers: {str(e)}")


def _build_question_generation_prompt(request: InterviewRequest) -> str:
    """Build prompt for generating interview questions"""
    
    interview_type_details = {
        'technical': 'Focus on technical skills, coding problems, system design, and domain-specific knowledge.',
        'behavioral': 'Focus on past experiences, soft skills, teamwork, conflict resolution, and leadership.',
        'case-study': 'Focus on problem-solving, analytical thinking, and strategic decision-making.',
        'hr': 'Focus on career goals, company fit, work style, and motivations.',
        'mixed': 'Include a balanced mix of technical, behavioral, and situational questions.'
    }
    
    experience_context = {
        'entry': 'Focus on fundamental concepts, learning ability, and potential.',
        'mid': 'Focus on practical experience, problem-solving, and technical depth.',
        'senior': 'Focus on leadership, architecture decisions, mentoring, and strategic thinking.'
    }
    
    prompt = f"""You are an expert interviewer conducting a {request.interviewType} interview for a {request.role} position.

JOB DESCRIPTION:
{request.jobDescription}

EXPERIENCE LEVEL: {request.experienceLevel.upper()}
{experience_context.get(request.experienceLevel, '')}

INTERVIEW TYPE: {request.interviewType.upper()}
{interview_type_details.get(request.interviewType, '')}

Generate EXACTLY {request.questionCount} high-quality interview questions. Return ONLY a valid JSON array with this exact structure:

[
  {{
    "id": 1,
    "question": "The actual question text",
    "type": "technical|behavioral|situational|case-study",
    "difficulty": "easy|medium|hard",
    "expectedPoints": ["key point 1", "key point 2", "key point 3"]
  }}
]

REQUIREMENTS:
- Questions must be specific to the role and job description
- Include variety in difficulty levels
- Questions should be clear and concise
- Include 3-5 expected key points for each question
- Make questions realistic and practical
- NO explanations, ONLY the JSON array
- Ensure proper JSON formatting with double quotes"""

    return prompt


def _parse_questions_from_response(response: str, expected_count: int) -> List[Question]:
    """Parse questions from AI response"""
    try:
        # Extract JSON from response
        response = response.strip()
        
        # Find JSON array in response
        start_idx = response.find('[')
        end_idx = response.rfind(']') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON array found in response")
        
        json_str = response[start_idx:end_idx]
        questions_data = json.loads(json_str)
        
        # Convert to Question objects
        questions = []
        for idx, q_data in enumerate(questions_data[:expected_count], 1):
            questions.append(Question(
                id=idx,
                question=q_data.get('question', ''),
                type=q_data.get('type', 'general'),
                difficulty=q_data.get('difficulty', 'medium'),
                expectedPoints=q_data.get('expectedPoints', [])
            ))
        
        return questions
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        logger.error(f"Response was: {response}")
        # Return fallback questions
        return _get_fallback_questions(expected_count)
    except Exception as e:
        logger.error(f"Error parsing questions: {e}")
        return _get_fallback_questions(expected_count)


def _get_fallback_questions(count: int) -> List[Question]:
    """Return fallback questions if AI generation fails"""
    fallback = [
        Question(
            id=1,
            question="Tell me about yourself and your relevant experience for this role.",
            type="behavioral",
            difficulty="easy",
            expectedPoints=["Background", "Relevant experience", "Key skills", "Career goals"]
        ),
        Question(
            id=2,
            question="What interests you most about this position?",
            type="behavioral",
            difficulty="easy",
            expectedPoints=["Company research", "Role alignment", "Career growth", "Skills match"]
        ),
        Question(
            id=3,
            question="Describe a challenging project you worked on and how you overcame obstacles.",
            type="behavioral",
            difficulty="medium",
            expectedPoints=["Problem description", "Your approach", "Actions taken", "Results achieved"]
        ),
        Question(
            id=4,
            question="What are your greatest strengths and how do they apply to this role?",
            type="behavioral",
            difficulty="easy",
            expectedPoints=["Specific strengths", "Examples", "Role relevance", "Impact"]
        ),
        Question(
            id=5,
            question="Where do you see yourself in 5 years?",
            type="behavioral",
            difficulty="easy",
            expectedPoints=["Career goals", "Growth mindset", "Company alignment", "Realistic expectations"]
        ),
    ]
    
    return fallback[:count]


def _build_evaluation_prompt(request: EvaluationRequest, interview: Dict) -> str:
    """Build prompt for evaluating answers with original questions from database"""
    
    # Get the original questions from the interview document
    original_questions = interview.get('questions', [])
    
    # Build detailed question-answer pairs
    qa_pairs = []
    for ans in request.answers:
        # Find the matching question
        question_data = next(
            (q for q in original_questions if q.get('id') == ans.questionId),
            None
        )
        
        if question_data:
            qa_text = f"""QUESTION {ans.questionId}:
Question Text: {question_data.get('question', 'N/A')}
Type: {question_data.get('type', 'general')}
Difficulty: {question_data.get('difficulty', 'medium')}
Expected Key Points: {', '.join(question_data.get('expectedPoints', []))}

USER'S ANSWER: {ans.answer}
TIME SPENT: {ans.timeSpent}s"""
        else:
            qa_text = f"""QUESTION {ans.questionId}:
USER'S ANSWER: {ans.answer}
TIME SPENT: {ans.timeSpent}s"""
        
        qa_pairs.append(qa_text)
    
    answers_text = "\n\n" + "\n\n".join(qa_pairs)
    
    prompt = f"""You are an expert interviewer evaluating answers for a {request.interviewType} interview for a {request.role} position.

CRITICAL INSTRUCTIONS:
1. Compare each answer against the ACTUAL QUESTION provided
2. Validate for CORRECTNESS - Does the answer actually address the question?
3. Check for COMPLETENESS - Does it cover the expected key points?
4. For nonsensical answers (random text, gibberish), score 0-2 and mark as incorrect
5. Provide the CORRECT/EXPECTED answer when user is wrong
6. Be specific about what was good and what needs improvement

QUESTIONS AND ANSWERS TO EVALUATE:
{answers_text}

Provide a comprehensive evaluation in EXACTLY this JSON format:

{{
  "question_evaluations": [
    {{
      "questionId": 1,
      "score": 8,
      "isCorrect": true,
      "feedback": "Your answer is [correct/partially correct/incorrect]. [If incorrect, explain why]. [Provide specific examples from their answer]. The key points you covered well were X, Y. However, you missed Z.",
      "correctAnswer": "For technical questions: Provide the correct/complete answer here. For behavioral: Provide ideal answer structure.",
      "strengths": ["Specific thing they did well 1", "Specific thing they did well 2"],
      "improvements": ["Specific actionable improvement 1", "What they should have mentioned", "How to structure better"]
    }}
  ],
  "overall_evaluation": {{
    "totalScore": 75,
    "averageScore": 7.5,
    "performance": "Good",
    "keyStrengths": ["Specific overall strength with example", "Another strength with context", "Third strength"],
    "areasToImprove": ["Specific area with why it matters", "Another area with how to improve", "Third area"],
    "detailedFeedback": "Overall comprehensive feedback: Start with what they did well overall, then areas for improvement, and conclude with encouragement and specific next steps.",
    "nextSteps": ["Specific actionable step 1", "Specific actionable step 2", "Specific actionable step 3"]
  }}
}}

SCORING CRITERIA (Be strict and accurate):
- 9-10: Excellent - Factually correct, comprehensive, well-structured, real examples, shows mastery
- 7-8: Good - Mostly correct, covers main points, some minor gaps
- 5-6: Average - Partially correct, missing important details, needs more depth
- 3-4: Below Average - Incomplete, some incorrect information, lacks clarity  
- 0-2: Poor - Incorrect information, off-topic, or inadequate

VALIDATION RULES:
- For TECHNICAL questions: Verify technical accuracy. If wrong, provide correct answer
- For BEHAVIORAL questions: Check if they used STAR method (Situation, Task, Action, Result)
- For CASE STUDY questions: Evaluate logic, structure, and problem-solving approach
- For HR questions: Check authenticity, clarity, and role alignment

PERFORMANCE LEVELS:
- 90-100: "Excellent" - Ready for real interview
- 75-89: "Good" - Minor improvements needed
- 60-74: "Average" - Needs significant practice
- Below 60: "Needs Improvement" - Major gaps to address

Be constructive but honest. If an answer is wrong, say it clearly and explain why. Provide the correct answer.
Return ONLY the JSON object, no additional text."""

    return prompt


def _parse_evaluation_from_response(response: str, num_answers: int) -> Dict[str, Any]:
    """Parse evaluation from AI response"""
    try:
        # Extract JSON from response
        response = response.strip()
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response")
        
        json_str = response[start_idx:end_idx]
        evaluation_data = json.loads(json_str)
        
        # Convert to proper models
        question_evals = [
            QuestionEvaluation(**q_eval)
            for q_eval in evaluation_data.get('question_evaluations', [])
        ]
        
        overall_eval = OverallEvaluation(**evaluation_data.get('overall_evaluation', {}))
        
        return {
            'question_evaluations': question_evals,
            'overall_evaluation': overall_eval
        }
        
    except Exception as e:
        logger.error(f"Error parsing evaluation: {e}")
        # Return fallback evaluation
        return _get_fallback_evaluation(num_answers)


def _get_fallback_evaluation(num_answers: int) -> Dict[str, Any]:
    """Return fallback evaluation if parsing fails"""
    question_evals = [
        QuestionEvaluation(
            questionId=i,
            score=7,
            isCorrect=True,
            feedback="Your answer demonstrates understanding. To improve, provide more specific examples and details relevant to the role.",
            correctAnswer="Focus on providing concrete examples using the STAR method (Situation, Task, Action, Result) for better structure.",
            strengths=["Clear communication", "Relevant points mentioned"],
            improvements=["Add more specific examples", "Provide quantifiable results", "Structure answer more clearly"]
        )
        for i in range(1, num_answers + 1)
    ]
    
    overall_eval = OverallEvaluation(
        totalScore=70,
        averageScore=7.0,
        performance="Good",
        keyStrengths=[
            "Good communication skills",
            "Relevant experience mentioned",
            "Positive attitude"
        ],
        areasToImprove=[
            "Provide more specific examples",
            "Structure answers using STAR method",
            "Practice concise responses"
        ],
        detailedFeedback="Overall, you demonstrated good understanding and communication. To improve, focus on providing specific examples and structuring your answers more clearly.",
        nextSteps=[
            "Practice with STAR method (Situation, Task, Action, Result)",
            "Prepare specific examples from past experience",
            "Research the company and role more thoroughly"
        ]
    )
    
    return {
        'question_evaluations': question_evals,
        'overall_evaluation': overall_eval
    }


class InterviewHistoryItem(BaseModel):
    """Summary item for interview history"""
    interview_id: str
    interviewType: str
    role: str
    totalQuestions: int
    totalScore: Optional[int]
    performance: Optional[str]
    status: str
    created_at: str
    completed_at: Optional[str]


class InterviewHistoryResponse(BaseModel):
    """Response for interview history"""
    interviews: List[InterviewHistoryItem]
    total: int
    page: int
    per_page: int


class InterviewDetailResponse(BaseModel):
    """Detailed interview response for viewing past interviews"""
    interview_id: str
    interviewType: str
    role: str
    jobDescription: str
    experienceLevel: str
    questions: List[Question]
    answers: Optional[List[Dict[str, Any]]]
    totalScore: Optional[int]
    performance: Optional[str]
    keyStrengths: Optional[List[str]]
    areasToImprove: Optional[List[str]]
    detailedFeedback: Optional[str]
    nextSteps: Optional[List[str]]
    created_at: str
    completed_at: Optional[str]
    status: str


@router.get("/history", response_model=InterviewHistoryResponse)
async def get_interview_history(
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    per_page: int = 10
):
    """
    Get user's interview history with pagination
    """
    try:
        db = get_db()
        interviews_collection = db[INTERVIEWS_COLLECTION]
        
        # Calculate skip
        skip = (page - 1) * per_page
        
        # Get total count
        total = interviews_collection.count_documents({"user_id": current_user["user_id"]})
        
        # Get interviews sorted by created_at (newest first)
        interviews = list(interviews_collection.find(
            {"user_id": current_user["user_id"]},
            {
                "interview_id": 1,
                "interviewType": 1,
                "role": 1,
                "totalQuestions": 1,
                "totalScore": 1,
                "performance": 1,
                "status": 1,
                "created_at": 1,
                "completed_at": 1,
                "_id": 0
            }
        ).sort("created_at", -1).skip(skip).limit(per_page))
        
        # Convert to response format
        history_items = []
        for interview in interviews:
            history_items.append(InterviewHistoryItem(
                interview_id=interview["interview_id"],
                interviewType=interview["interviewType"],
                role=interview["role"],
                totalQuestions=interview["totalQuestions"],
                totalScore=interview.get("totalScore"),
                performance=interview.get("performance"),
                status=interview["status"],
                created_at=interview["created_at"].isoformat() if isinstance(interview["created_at"], datetime) else interview["created_at"],
                completed_at=interview["completed_at"].isoformat() if interview.get("completed_at") and isinstance(interview["completed_at"], datetime) else interview.get("completed_at")
            ))
        
        return InterviewHistoryResponse(
            interviews=history_items,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error fetching interview history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch interview history: {str(e)}")


@router.get("/detail/{interview_id}", response_model=InterviewDetailResponse)
async def get_interview_detail(
    interview_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific interview
    """
    try:
        db = get_db()
        interviews_collection = db[INTERVIEWS_COLLECTION]
        
        # Find interview and verify ownership
        interview = interviews_collection.find_one(
            {
                "interview_id": interview_id,
                "user_id": current_user["user_id"]
            },
            {"_id": 0}
        )
        
        if not interview:
            raise HTTPException(
                status_code=404,
                detail="Interview not found or does not belong to current user"
            )
        
        # Convert questions to Question objects
        questions = [Question(**q) for q in interview["questions"]]
        
        return InterviewDetailResponse(
            interview_id=interview["interview_id"],
            interviewType=interview["interviewType"],
            role=interview["role"],
            jobDescription=interview["jobDescription"],
            experienceLevel=interview["experienceLevel"],
            questions=questions,
            answers=interview.get("answers"),
            totalScore=interview.get("totalScore"),
            performance=interview.get("performance"),
            keyStrengths=interview.get("keyStrengths"),
            areasToImprove=interview.get("areasToImprove"),
            detailedFeedback=interview.get("detailedFeedback"),
            nextSteps=interview.get("nextSteps"),
            created_at=interview["created_at"].isoformat() if isinstance(interview["created_at"], datetime) else interview["created_at"],
            completed_at=interview["completed_at"].isoformat() if interview.get("completed_at") and isinstance(interview["completed_at"], datetime) else interview.get("completed_at"),
            status=interview["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching interview detail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch interview detail: {str(e)}")
