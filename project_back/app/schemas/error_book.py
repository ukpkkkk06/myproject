from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class ErrorBookItem(BaseModel):
    id: int
    question_id: int
    wrong_count: int
    first_wrong_time: Optional[datetime] = None
    last_wrong_time: Optional[datetime] = None
    next_review_time: Optional[datetime] = None
    mastered: bool = False
    stem: str = ""
    
    class Config:
        from_attributes = True

class ErrorBookListResp(BaseModel):
    total: int
    page: int
    size: int
    items: List[ErrorBookItem]