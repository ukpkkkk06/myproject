from pydantic import BaseModel
from typing import Optional, List, Literal

class CreateSessionRequest(BaseModel):
    size: int = 5
    subject_id: Optional[int] = None
    knowledge_id: Optional[int] = None  # 知识点ID,支持按知识点筛选题目
    include_children: Optional[bool] = True  # 是否包含子知识点
    question_types: Optional[List[str]] = None  # 题型列表,如["SC","MC","FILL"],None表示全部类型
    practice_mode: Optional[Literal['RANDOM', 'SMART', 'WEAK_POINT']] = 'RANDOM'  # 🆕 练习模式

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
