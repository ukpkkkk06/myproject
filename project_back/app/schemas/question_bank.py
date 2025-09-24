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