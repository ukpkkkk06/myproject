from pydantic import BaseModel
from typing import Optional, List

class CreateSessionRequest(BaseModel):
    size: int = 5
    subject_id: Optional[int] = None

class CreateSessionResponse(BaseModel):
    attempt_id: int
    paper_id: int
    total: int
    first_seq: int = 1

class QuestionView(BaseModel):
    seq: int
    question_id: int
    type: str
    difficulty: Optional[int] = None
    stem: str
    options: List[str] = []
    explanation: Optional[str] = None  # 新增：题目解析

class SubmitAnswerRequest(BaseModel):
    seq: int
    user_answer: str
    time_spent_ms: Optional[int] = None

class SubmitAnswerResponse(BaseModel):
    seq: int
    correct: bool
    correct_answer: str
    total: int

class FinishResponse(BaseModel):
    total: int
    answered: int
    correct_count: int
    accuracy: float
    duration_seconds: int

class SubjectOut(BaseModel):
    id: int
    name: str
