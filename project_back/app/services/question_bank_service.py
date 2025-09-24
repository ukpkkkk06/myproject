from sqlalchemy.orm import Session
from app.models.question import Question
from app.models.question_version import QuestionVersion
from app.models.user import User

def list_my_questions(
    db: Session,
    user: User,
    page: int = 1,
    size: int = 10,
    keyword: str | None = None,
    qtype: str | None = None,
    difficulty: int | None = None,
    active_only: bool = False,
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

    total = q.count()
    rows = (
        q.order_by(Question.updated_at.desc(), Question.id.desc())
         .offset((page - 1) * size)
         .limit(size)
         .all()
    )
    return total, rows