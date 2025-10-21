from typing import List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
# from app.services import question_bank_service
# from app.services.question_bank_service import import_questions_from_excel  # 修复未定义函数

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
    type: Optional[str] = None  # 🔥 添加题型字段 (SC/MC/FILL)
    correct_answer: Optional[str] = None  # 🔥 添加正确答案字段
    is_active: Optional[bool] = True  # 🔥 添加启用状态字段

class QuestionsBriefResp(BaseModel):
    items: List[QuestionBrief]

class TagOut(BaseModel):
    id: int
    name: str
    type: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = True

class QuestionTagsOut(BaseModel):
    subject_id: Optional[int] = None
    level_id: Optional[int] = None
    tag_ids: List[int] = Field(default_factory=list)

class SetQuestionTagsIn(BaseModel):
    subject_id: Optional[int] = None
    level_id: Optional[int] = None
    add_ids: List[int] = Field(default_factory=list)
    remove_ids: List[int] = Field(default_factory=list)

class SimpleOK(BaseModel):
    ok: bool = True

class QuestionUpdate(BaseModel):
    stem: Optional[str] = None
    options: Optional[Union[List[dict], List[str]]] = None
    analysis: Optional[str] = None
    correct_answer: Optional[str] = None
    is_active: Optional[bool] = None
    type: Optional[str] = None  # 🔥 新增：题目类型 (SC/MC/FILL)

class ImportErrorItem(BaseModel):
    row: int
    reason: str

class ImportQuestionsResult(BaseModel):
    total_rows: int
    success: int
    failed: int
    errors: List[ImportErrorItem] = []