import logging
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import func
from app.core.exceptions import AppException
from app.models.knowledge_point import KnowledgePoint
from app.models.question_knowledge import QuestionKnowledge
from app.models.user import User
from app.models.question import Question
from app.models.question_version import QuestionVersion
from app.models.user_answer import UserAnswer
from app.models.error_book import ErrorBook
from app.models.tag import Tag, QuestionTag
from app.models.paper import Paper
from app.models.paper_question import PaperQuestion
from app.models.exam_attempt import ExamAttempt

log = logging.getLogger("practice_service")

def _norm_sc(ans: str) -> str:
    return (ans or "").strip().upper()

def _new_title() -> str:
    return f"练习-{datetime.now():%Y%m%d%H%M%S}"

def _err_msg(e: Exception) -> str:
    try:
        if hasattr(e, "orig") and getattr(e.orig, "args", None):
            return " ".join(map(str, e.orig.args)).lower()
        return " ".join(map(str, getattr(e, "args", []) or [])).lower()
    except Exception:
        return str(e).lower()

def _opt_to_list(val) -> list[str]:
    if val is None:
        return []
    # 已是列表
    if isinstance(val, list):
        out = []
        for it in val:
            if isinstance(it, dict):
                out.append((it.get("text") or it.get("content") or "").strip())
            else:
                out.append(str(it))
        return out
    # 可能是 JSON 字符串
    if isinstance(val, str):
        import json
        try:
            parsed = json.loads(val)
            return _opt_to_list(parsed)
        except Exception:
            # 用逗号分隔兜底
            s = val.strip()
            if s.startswith('[') and s.endswith(']'):
                # 看起来像 JSON 但解析失败，去掉引号再尝试简单切分
                s = s.strip('[]')
            parts = [p.strip().strip('"\'') for p in s.split(',') if p.strip()]
            return parts
    # 其它类型兜底
    return [str(val)]

def _kp_descendants(db, root_id: int) -> List[int]:
    rows = db.query(KnowledgePoint.id, KnowledgePoint.parent_id).all()
    by_parent = {}
    for i, p in rows:
        by_parent.setdefault(p, []).append(i)
    res, st = [], [root_id]
    while st:
        cur = st.pop()
        cs = by_parent.get(cur, [])
        res.extend(cs); st.extend(cs)
    return res

def create_session(db: Session, user: User, size: int, subject_id: Optional[int] = None, knowledge_id: Optional[int] = None, include_children: bool = False) -> tuple[int, int, int, int]:
    """创建练习会话；可按学科筛选。异常通过 AppException 抛出，交给统一异常处理器。
    Args:
        db (Session): 数据库会话
        user (User): 用户对象
        size (int): 题目数量
        subject_id (Optional[int], optional): 学科 ID. Defaults to None.
    Raises:
        AppException: 自定义异常
    Returns:
        tuple[int, int, int, int]: 会话 ID, 试卷 ID, 题目总数, 当前题序
    """
    size = max(1, min(int(size or 5), 50))

    # 仅当未指定学科时复用未完成会话；指定学科时强制新建，确保筛选生效
    if subject_id is None:
        existing = (
            db.query(ExamAttempt)
            .filter(ExamAttempt.user_id == user.id, ExamAttempt.status == "IN_PROGRESS")
            .order_by(ExamAttempt.start_time.desc())
            .first()
        )
        if existing:
            total = db.query(PaperQuestion).filter(PaperQuestion.paper_id == existing.paper_id).count()
            return existing.id, existing.paper_id, int(total), 1
    # 若指定学科，校验其存在
    if subject_id is not None:
        tag = db.query(Tag).filter(Tag.id == int(subject_id), Tag.type == "SUBJECT").first()
        if not tag:
            raise AppException("学科不存在", code=400, status_code=400)

    # 按学科抽题
    q = db.query(Question.id).filter(Question.is_active == True, Question.type == "SC")
    if subject_id:
        q = (q.join(QuestionTag, QuestionTag.question_id == Question.id)
              .join(Tag, Tag.id == QuestionTag.tag_id)
              .filter(Tag.type == "SUBJECT", Tag.id == int(subject_id)))
    question_ids = [r.id for r in q.order_by(func.rand()).limit(size).all()]
    if not question_ids:
        raise AppException("该学科暂无可用题目" if subject_id else "暂无可用题目", code=404, status_code=404)

    # 组卷 + 创建会话（失败要回滚并抛出 AppException）
    try:
        paper = Paper(
            title=_new_title(),
            is_public=False,
            status="PRACTICE",
            created_by=user.id,
        )
        db.add(paper); db.flush()
        for i, qid in enumerate(question_ids, start=1):
            db.add(PaperQuestion(paper_id=paper.id, question_id=qid, seq=i))
        db.flush()
        attempt = ExamAttempt(user_id=user.id, paper_id=paper.id, status="IN_PROGRESS", start_time=datetime.now())
        db.add(attempt); db.commit()
        return attempt.id, paper.id, len(question_ids), 1
    except Exception as e:
        db.rollback()
        raise

def get_question(db: Session, user: User, attempt_id: int, seq: int):
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id, ExamAttempt.user_id == user.id).first()
    if not attempt or attempt.status != "IN_PROGRESS":
        raise AppException("会话不存在或已结束", code=404, status_code=404)

    pq = db.query(PaperQuestion).filter(PaperQuestion.paper_id == attempt.paper_id, PaperQuestion.seq == seq).first()
    if not pq:
        raise AppException("题目不存在", code=404, status_code=404)

    q = db.query(Question).filter(Question.id == pq.question_id, Question.is_active == True).first()
    if not q:
        raise AppException("题目不可用", code=404, status_code=404)
    qv = db.query(QuestionVersion).filter(QuestionVersion.id == q.current_version_id, QuestionVersion.is_active == 1).first()
    if not qv:
        raise AppException("题目版本不存在", code=404, status_code=404)

    return {
        "seq": seq,
        "question_id": q.id,
        "type": q.type,
        "difficulty": q.difficulty,
        "stem": qv.stem,
        "options": _opt_to_list(getattr(qv, "options", None) or getattr(qv, "choices", None)),  # 关键：强转为 List[str]
        "explanation": getattr(qv, "explanation", None) or None,
    }

def submit_answer(db: Session, user: User, attempt_id: int, seq: int, user_answer: str, time_spent_ms: int | None = None):
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id, ExamAttempt.user_id == user.id).first()
    if not attempt or attempt.status != "IN_PROGRESS":
        raise AppException("会话不存在或已结束", code=404, status_code=404)

    pq = db.query(PaperQuestion).filter(PaperQuestion.paper_id == attempt.paper_id, PaperQuestion.seq == seq).first()
    if not pq:
        raise AppException("题目不存在", code=404, status_code=404)

    q = db.query(Question).filter(Question.id == pq.question_id).first()
    qv = db.query(QuestionVersion).filter(QuestionVersion.id == q.current_version_id).first()

    correct = _norm_sc(user_answer) == _norm_sc(qv.correct_answer)

    ua = db.query(UserAnswer).filter(
        UserAnswer.attempt_id == attempt.id, UserAnswer.question_id == q.id
    ).first()
    now = datetime.utcnow()
    if ua:
        ua.user_answer = user_answer
        ua.is_correct = correct
        ua.time_spent_ms = time_spent_ms
        ua.answer_time = now
    else:
        ua = UserAnswer(
            attempt_id=attempt.id, user_id=user.id, question_id=q.id, paper_id=attempt.paper_id,
            user_answer=user_answer, is_correct=correct, time_spent_ms=time_spent_ms,
            answer_time=now, first_flag=True
        )
        db.add(ua)

    # 新增：答错则写入/更新错题本
    if not correct:
        eb = db.query(ErrorBook).filter(
            ErrorBook.user_id == user.id,          # 按用户维度
            ErrorBook.question_id == q.id
        ).first()
        if eb:
            eb.wrong_count = (eb.wrong_count or 0) + 1
            eb.last_wrong_time = now
            eb.next_review_time = now + timedelta(days=min(7, max(1, eb.wrong_count)))
        else:
            eb = ErrorBook(
                user_id=user.id,                   # 写入 user_id
                question_id=q.id,
                first_wrong_time=now,
                last_wrong_time=now,
                wrong_count=1,
                next_review_time=now + timedelta(days=1),
                mastered=False,
            )
            db.add(eb)

    db.commit()

    total = db.query(PaperQuestion).filter(PaperQuestion.paper_id == attempt.paper_id).count()
    return {
        "seq": seq,
        "correct": bool(correct),
        "correct_answer": qv.correct_answer or "",
        "total": int(total),
    }

def finish(db: Session, user: User, attempt_id: int):
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id, ExamAttempt.user_id == user.id).first()
    if not attempt:
        raise AppException("会话不存在", code=404, status_code=404)

    total = db.query(PaperQuestion).filter(PaperQuestion.paper_id == attempt.paper_id).count()
    answered = db.query(UserAnswer).filter(UserAnswer.attempt_id == attempt.id).count()
    correct_count = db.query(UserAnswer).filter(UserAnswer.attempt_id == attempt.id, UserAnswer.is_correct == True).count()

    if attempt.status != "FINISHED":
        attempt.status = "FINISHED"
        attempt.submit_time = datetime.utcnow()
        attempt.duration_seconds = int((attempt.submit_time - attempt.start_time).total_seconds()) if attempt.start_time else 0
        attempt.calculated_accuracy = (correct_count / total) if total else 0
        db.add(attempt); db.commit()

    return {
        "total": int(total),
        "answered": int(answered),
        "correct_count": int(correct_count),
        "accuracy": float(attempt.calculated_accuracy or 0),
        "duration_seconds": int(attempt.duration_seconds or 0),
    }
