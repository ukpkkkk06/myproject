from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.error_book import ErrorBookItem, ErrorBookListResp
from app.services import error_book_service

router = APIRouter()

@router.get("/error-book", response_model=ErrorBookListResp)
def list_my_error_book(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    only_due: bool = Query(False),
    include_mastered: bool = Query(False),
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    total, rows = error_book_service.list_error_book(
        db, me, page=page, size=size, only_due=only_due, include_mastered=include_mastered
    )
    items = [
        ErrorBookItem(
            id=r.id,
            question_id=r.question_id,
            wrong_count=r.wrong_count or 0,
            first_wrong_time=r.first_wrong_time,
            last_wrong_time=r.last_wrong_time,
            next_review_time=r.next_review_time,
            mastered=bool(r.mastered),
        )
        for r in rows
    ]
    return {"total": total, "page": page, "size": size, "items": items}