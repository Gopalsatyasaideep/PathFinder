"""
Mock Interview Database Model

Defines the structure for storing mock interview sessions in MongoDB
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class MockInterviewQuestion(BaseModel):
    """Individual question in the interview"""
    id: int
    question: str
    type: str
    difficulty: str
    expectedPoints: List[str]


class MockInterviewAnswer(BaseModel):
    """User's answer to a question"""
    questionId: int
    answer: str
    timeSpent: int  # in seconds
    score: Optional[int] = None  # 0-10, filled after evaluation
    isCorrect: Optional[bool] = None
    feedback: Optional[str] = None
    correctAnswer: Optional[str] = None
    strengths: Optional[List[str]] = None
    improvements: Optional[List[str]] = None


class MockInterviewSession(BaseModel):
    """Complete mock interview session stored in database"""
    interview_id: str = Field(..., description="Unique interview identifier")
    user_id: str = Field(..., description="User who took the interview")
    user_email: str = Field(..., description="User's email")
    
    # Interview configuration
    interviewType: str = Field(..., description="Type of interview")
    role: str = Field(..., description="Job role")
    jobDescription: str = Field(..., description="Job description")
    experienceLevel: str = Field(..., description="Experience level")
    
    # Questions
    questions: List[MockInterviewQuestion] = Field(..., description="Generated questions")
    totalQuestions: int
    estimatedDuration: int  # in minutes
    
    # Answers and evaluation (filled after submission)
    answers: Optional[List[MockInterviewAnswer]] = None
    totalScore: Optional[int] = None  # 0-100
    averageScore: Optional[float] = None
    performance: Optional[str] = None  # Excellent, Good, Average, Needs Improvement
    keyStrengths: Optional[List[str]] = None
    areasToImprove: Optional[List[str]] = None
    detailedFeedback: Optional[str] = None
    nextSteps: Optional[List[str]] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None  # When user started answering
    completed_at: Optional[datetime] = None  # When evaluation was done
    
    # Status
    status: str = Field(default="generated", description="generated, in_progress, completed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MockInterviewHistory(BaseModel):
    """Summary for interview history list"""
    interview_id: str
    interviewType: str
    role: str
    totalQuestions: int
    totalScore: Optional[int]
    performance: Optional[str]
    status: str
    created_at: str
    completed_at: Optional[str]


# Database helper functions
def create_interview_document(interview_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a MongoDB document for a new interview"""
    return {
        "interview_id": interview_data["interview_id"],
        "user_id": interview_data["user_id"],
        "user_email": interview_data["user_email"],
        "interviewType": interview_data["interviewType"],
        "role": interview_data["role"],
        "jobDescription": interview_data["jobDescription"],
        "experienceLevel": interview_data["experienceLevel"],
        "questions": [q.dict() if hasattr(q, 'dict') else q for q in interview_data["questions"]],
        "totalQuestions": interview_data["totalQuestions"],
        "estimatedDuration": interview_data["estimatedDuration"],
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


def update_interview_with_evaluation(evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create update document for interview evaluation"""
    return {
        "$set": {
            "answers": evaluation_data["answers"],
            "totalScore": evaluation_data["totalScore"],
            "averageScore": evaluation_data["averageScore"],
            "performance": evaluation_data["performance"],
            "keyStrengths": evaluation_data["keyStrengths"],
            "areasToImprove": evaluation_data["areasToImprove"],
            "detailedFeedback": evaluation_data["detailedFeedback"],
            "nextSteps": evaluation_data["nextSteps"],
            "completed_at": datetime.utcnow(),
            "status": "completed"
        }
    }
