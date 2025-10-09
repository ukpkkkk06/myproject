from sqlalchemy.orm import Session
from sqlalchemy import exists
from app.models.question import Question
from app.models.question_version import QuestionVersion
from app.models.user import User
from app.models.tag import QuestionTag

def list_my_questions(
    db: Session,
    user: User,
    page: int = 1,
    size: int = 10,
    keyword: str | None = None,
    qtype: str | None = None,
    difficulty: int | None = None,
    active_only: bool = False,
    subject_id: int | None = None,
    level_id: int | None = None,
):
    page = max(1, int(page or 1))
    size = max(1, min(int(size or 10), 100))

    q = (
        db.query(
            Question.id.label("question_id"),
            Question.type,
            Question.difficulty,
            Question.audit_status,
            Question.is_active,
            Question.created_at,
            Question.updated_at,
            QuestionVersion.stem,
        )
        .join(QuestionVersion, Question.current_version_id == QuestionVersion.id)
        .filter(QuestionVersion.created_by == user.id)
    )

    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.filter(QuestionVersion.stem.like(kw))
    if qtype:
        q = q.filter(Question.type == qtype)
    if difficulty is not None:
        q = q.filter(Question.difficulty == difficulty)
    if active_only:
        q = q.filter(Question.is_active == True)
    if subject_id:
        q = q.filter(
            exists().where(
                (QuestionTag.question_id == Question.id) &
                (QuestionTag.tag_id == subject_id)
            )
        )
    if level_id:
        q = q.filter(
            exists().where(
                (QuestionTag.question_id == Question.id) &
                (QuestionTag.tag_id == level_id)
            )
        )

    total = q.count()
    rows = (
        q.order_by(Question.updated_at.desc(), Question.id.desc())
         .offset((page - 1) * size)
         .limit(size)
         .all()
    )
    return total, rows

def get_my_questions(
    db: Session, page: int, size: int,
    keyword: str|None, qtype: str|None, difficulty: int|None, active_only: bool,
    subject_id: int | None = None, level_id: int | None = None
):
    q = (
        db.query(
            Question.id.label("question_id"),
            Question.type,
            Question.difficulty,
            Question.audit_status,
            Question.updated_at,
            Question.created_at,
            QuestionVersion.stem,
        )
        .join(QuestionVersion, QuestionVersion.id == Question.current_version_id, isouter=False)
        .filter(Question.is_active == True)
    )
    if keyword:
        q = q.filter(QuestionVersion.stem.ilike(f"%{keyword}%"))
    if qtype:
        q = q.filter(Question.type == qtype)
    if difficulty:
        q = q.filter(Question.difficulty == difficulty)
    if active_only:
        q = q.filter(Question.audit_status == "APPROVED")
    if subject_id:
        q = q.filter(
            exists().where(
                (QuestionTag.question_id == Question.id) &
                (QuestionTag.tag_id == subject_id)
            )
        )
    if level_id:
        q = q.filter(
            exists().where(
                (QuestionTag.question_id == Question.id) &
                (QuestionTag.tag_id == level_id)
            )
        )

    total = q.count()
    rows = (q
            .order_by(Question.updated_at.desc(), Question.id.desc())
            .offset((page-1)*size).limit(size).all())
    return {
        "total": total,
        "page": page,
        "items": [dict(r._mapping) for r in rows],
    }