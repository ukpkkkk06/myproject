from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.question_bank import MyQuestionListResp, MyQuestionItem
from app.services import question_bank_service

router = APIRouter()

@router.get("/my-questions", response_model=MyQuestionListResp)
def list_my_questions(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None),
    qtype: str | None = Query(None),
    difficulty: int | None = Query(None),
    active_only: bool = Query(False),
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    total, rows = question_bank_service.list_my_questions(
        db, me, page=page, size=size, keyword=keyword,
        qtype=qtype, difficulty=difficulty, active_only=active_only
    )
    items = [
        MyQuestionItem(
            question_id=r.question_id,
            type=r.type,
            difficulty=r.difficulty,
            stem=r.stem[:120],
            audit_status=r.audit_status,
            is_active=bool(r.is_active),
            created_at=r.created_at,
            updated_at=r.updated_at,
        ) for r in rows
    ]
    return {"total": total, "page": page, "size": size, "items": items}
