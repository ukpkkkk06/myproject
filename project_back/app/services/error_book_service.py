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


def record_wrong(db: Session, user: User, question_id: int):
    """记录用户答错题目
    
    Args:
        db: 数据库会话
        user: 当前用户
        question_id: 题目ID
    """
    now = datetime.utcnow()
    
    # 查找是否已存在该错题记录
    record = db.query(ErrorBook).filter(
        ErrorBook.user_id == user.id,
        ErrorBook.question_id == question_id
    ).first()
    
    if record:
        # 已存在,更新记录
        record.wrong_count = (record.wrong_count or 0) + 1
        record.last_wrong_time = now
        record.mastered = False  # 重新答错,标记为未掌握
        # 更新下次复习时间(例如:根据错误次数延长复习间隔)
        # 这里简单设置为立即复习
        record.next_review_time = now
    else:
        # 不存在,创建新记录
        record = ErrorBook(
            user_id=user.id,
            question_id=question_id,
            first_wrong_time=now,
            last_wrong_time=now,
            wrong_count=1,
            next_review_time=now,
            mastered=False
        )
        db.add(record)
    
    db.commit()
    db.refresh(record)
    return record


def toggle_mastered(db: Session, user: User, question_id: int, mastered: bool):
    """标记题目为已掌握/未掌握
    
    Args:
        db: 数据库会话
        user: 当前用户
        question_id: 题目ID
        mastered: True表示已掌握,False表示未掌握
    """
    # 查找错题记录
    record = db.query(ErrorBook).filter(
        ErrorBook.user_id == user.id,
        ErrorBook.question_id == question_id
    ).first()
    
    if not record:
        # 如果记录不存在,可以选择创建一个或抛出异常
        # 这里选择抛出异常
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="错题记录不存在")
    
    # 更新掌握状态
    record.mastered = mastered
    
    # 如果标记为已掌握,可以清空下次复习时间
    if mastered:
        record.next_review_time = None
    else:
        # 如果标记为未掌握,设置下次复习时间为当前时间
        record.next_review_time = datetime.utcnow()
    
    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, user: User, question_id: int):
    """删除错题记录
    
    Args:
        db: 数据库会话
        user: 当前用户
        question_id: 题目ID
    """
    # 查找并删除错题记录
    record = db.query(ErrorBook).filter(
        ErrorBook.user_id == user.id,
        ErrorBook.question_id == question_id
    ).first()
    
    if not record:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="错题记录不存在")
    
    db.delete(record)
    db.commit()
    return True