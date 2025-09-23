from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.error_book import ErrorBook
from app.models.user import User

def list_error_book(
    db: Session,
    user: User,
    page: int = 1,
    size: int = 10,
    only_due: bool = False,          # 仅到期复习
    include_mastered: bool = False,  # 是否包含已掌握
):
    page = max(1, int(page or 1))
    size = max(1, min(int(size or 10), 100))
    now = datetime.utcnow()

    q = db.query(ErrorBook).filter(ErrorBook.user_id == user.id)
    if not include_mastered:
        q = q.filter(ErrorBook.mastered == False)
    if only_due:
        q = q.filter(
            (ErrorBook.next_review_time == None) | (ErrorBook.next_review_time <= now)
        )

    total = q.count()

    # 关键：替换 NULLS LAST 排序，兼容 MySQL
    rows = (
        q.order_by(
            func.isnull(ErrorBook.last_wrong_time).asc(),  # 非空在前，NULL 在后
            ErrorBook.last_wrong_time.desc(),
            ErrorBook.id.desc(),
        )
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return total, rows