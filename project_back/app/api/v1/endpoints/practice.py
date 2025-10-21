from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import select
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.practice import (
    CreateSessionRequest, CreateSessionResponse,
    QuestionView, SubmitAnswerRequest, SubmitAnswerResponse,
    FinishResponse, SubjectOut
)
from app.services import practice_service
from app.models.tag import Tag

router = APIRouter()

@router.post("/practice/session", response_model=CreateSessionResponse)
@router.post("/practice/sessions", response_model=CreateSessionResponse)
def create_session(body: CreateSessionRequest, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    attempt_id, paper_id, total, first_seq = practice_service.create_session(
        db, me, body.size, body.subject_id, body.knowledge_id, body.include_children, 
        body.question_types, body.practice_mode  # 🆕 传递练习模式参数
    )
    return {"attempt_id": attempt_id, "paper_id": paper_id, "total": total, "first_seq": first_seq}

@router.get("/practice/sessions/{attempt_id:int}/questions/{seq:int}", response_model=QuestionView)
def get_question(attempt_id: int, seq: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    return practice_service.get_question(db, me, attempt_id, seq)

@router.post("/practice/sessions/{attempt_id:int}/answers", response_model=SubmitAnswerResponse)
def submit_answer(attempt_id: int, body: SubmitAnswerRequest, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    return practice_service.submit_answer(db, me, attempt_id, body.seq, body.user_answer, body.time_spent_ms)

@router.post("/practice/sessions/{attempt_id:int}/finish", response_model=FinishResponse)
def finish(attempt_id: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    return practice_service.finish(db, me, attempt_id)

# 学科列表：供前端选择
@router.get("/practice/subjects", response_model=List[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    rows = db.execute(select(Tag).where(Tag.type == "SUBJECT").order_by(Tag.id)).scalars().all()
    return [SubjectOut(id=t.id, name=t.name) for t in rows]

# 🆕 获取用户错题统计（供前端判断是否可用智能模式）
@router.get("/practice/error-stats")
def get_error_stats(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    """
    获取用户错题统计
    
    Returns:
        {
            "total_errors": 15,  # 错题总数
            "unmastered": 12     # 未掌握的错题数
        }
    """
    from app.models.error_book import ErrorBook
    
    total = db.query(ErrorBook).filter(ErrorBook.user_id == me.id).count()
    unmastered = db.query(ErrorBook).filter(
        ErrorBook.user_id == me.id,
        ErrorBook.mastered == False
    ).count()
    
    return {
        "total_errors": total,
        "unmastered": unmastered
    }

# 获取下一题（新增可选学科筛选）
@router.get("/practice/next")
def next_question(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    subject_id: Optional[int] = Query(default=None, description="按学科筛选")
):
    return practice_service.get_question(db, current_user.id, subject_id=subject_id)


