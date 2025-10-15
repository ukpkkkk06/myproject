from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.models.question import Question
from app.models.question_version import QuestionVersion
from app.schemas.error_book import ErrorBookItem, ErrorBookListResp
from app.services import error_book_service

router = APIRouter()

@router.get("", response_model=ErrorBookListResp)
def list_my_error_book(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    only_due: bool = Query(False),
    include_mastered: bool = Query(False),
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    """获取当前用户的错题本（带题干）"""
    total, rows = error_book_service.list_error_book(
        db, me, page=page, size=size, only_due=only_due, include_mastered=include_mastered
    )
    
    # 🔥 批量查询题干（通过 current_version_id）
    question_ids = [r.question_id for r in rows]
    if question_ids:
        # 先查 Question 表，获取 current_version_id
        questions = db.query(Question.id, Question.current_version_id).filter(
            Question.id.in_(question_ids)
        ).all()
        
        version_ids = [q.current_version_id for q in questions if q.current_version_id]
        
        if version_ids:
            # 再查 QuestionVersion 表，获取题干
            versions = db.query(
                QuestionVersion.id, 
                QuestionVersion.question_id, 
                QuestionVersion.stem
            ).filter(
                QuestionVersion.id.in_(version_ids)
            ).all()
            
            # 构建 question_id -> stem 的映射
            version_map = {v.id: v for v in versions}
            stem_map = {}
            for q in questions:
                if q.current_version_id and q.current_version_id in version_map:
                    stem_map[q.id] = version_map[q.current_version_id].stem or ""
        else:
            stem_map = {}
    else:
        stem_map = {}
    
    # 🔥 构建返回结果（包含题干）
    items = [
        ErrorBookItem(
            id=r.id,
            question_id=r.question_id,
            wrong_count=r.wrong_count or 0,
            first_wrong_time=r.first_wrong_time,
            last_wrong_time=r.last_wrong_time,
            next_review_time=r.next_review_time,
            mastered=bool(r.mastered),
            stem=stem_map.get(r.question_id, "")
        )
        for r in rows
    ]
    
    return ErrorBookListResp(total=total, page=page, size=size, items=items)


@router.post("/{question_id}/record")
def record_wrong_answer(
    question_id: int,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    """记录错误答案"""
    error_book_service.record_wrong(db, me, question_id)
    return {"message": "已记录错误"}


@router.patch("/{question_id}/master")
def mark_as_mastered(
    question_id: int,
    mastered: bool = True,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    """标记为已掌握/未掌握"""
    error_book_service.toggle_mastered(db, me, question_id, mastered)
    return {"message": "已更新"}


@router.delete("/{question_id}")
def delete_error_record(
    question_id: int,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    """删除错题记录"""
    error_book_service.delete_record(db, me, question_id)
    return {"message": "已删除"}