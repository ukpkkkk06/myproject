from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.practice import (
    CreateSessionRequest, CreateSessionResponse,
    QuestionView, SubmitAnswerRequest, SubmitAnswerResponse,
    FinishResponse
)
from app.services import practice_service

router = APIRouter()

@router.post("/practice/sessions", response_model=CreateSessionResponse)
def create_session(body: CreateSessionRequest, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    attempt_id, paper_id, total, first_seq = practice_service.create_session(db, me, body.size)
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
