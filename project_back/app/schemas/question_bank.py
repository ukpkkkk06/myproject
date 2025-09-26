from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class MyQuestionItem(BaseModel):
    question_id: int
    type: str
    difficulty: int | None
    stem: str
    audit_status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class MyQuestionListResp(BaseModel):
    total: int
    page: int
    size: int
    items: List[MyQuestionItem]

# 若已存在，请忽略下面两个模型
class QuestionOption(BaseModel):
    key: Optional[str] = None
    text: Optional[str] = None
    content: Optional[str] = None
    is_correct: Optional[bool] = None

class QuestionBrief(BaseModel):
    id: int
    stem: str
    options: Optional[List[QuestionOption]] = None
    analysis: Optional[str] = None

class QuestionsBriefResp(BaseModel):
    items: List[QuestionBrief]