import logging
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.exceptions import AppException
from app.models.user import User
from app.models.question import Question
from app.models.question_version import QuestionVersion
from app.models.paper import Paper
from app.models.paper_question import PaperQuestion
from app.models.exam_attempt import ExamAttempt
from app.models.user_answer import UserAnswer
from app.models.error_book import ErrorBook

log = logging.getLogger("practice_service")

def _norm_sc(ans: str) -> str:
    return (ans or "").strip().upper()

def _new_title() -> str:
    return f"练习_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:6].upper()}"

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

def create_session(db: Session, user: User, size: int) -> tuple[int, int, int, int]:
    size = max(1, min(int(size or 5), 50))

    # 1) 复用未完成会话
    existing = (
        db.query(ExamAttempt)
        .filter(ExamAttempt.user_id == user.id, ExamAttempt.status == "IN_PROGRESS")
        .order_by(ExamAttempt.start_time.desc())
        .first()
    )
    if existing:
        total = db.query(PaperQuestion).filter(PaperQuestion.paper_id == existing.paper_id).count()
        return existing.id, existing.paper_id, int(total), 1

    # 2) 抽题
    q_rows = (
        db.query(Question.id)
        .filter(Question.is_active == True, Question.type == "SC")
        .order_by(func.rand())
        .limit(size)
        .all()
    )
    question_ids = [r.id for r in q_rows]
    if not question_ids:
        raise AppException("暂无可用题目", code=404, status_code=404)

    # 3) 创建 Paper、PAPER_QUESTION、EXAM_ATTEMPT
    try:
        now = datetime.utcnow()
        paper = Paper(
            title=_new_title(),
            is_public=False,
            status="PRACTICE",
            created_by=user.id,
            created_at=now,
            updated_at=now,
        )
        db.add(paper); db.flush()

        for i, qid in enumerate(question_ids, start=1):
            db.add(PaperQuestion(paper_id=paper.id, question_id=qid, seq=i, score=1))
        db.flush()

        next_idx = (
            db.query(func.coalesce(func.max(ExamAttempt.attempt_index), 0))
            .filter(ExamAttempt.user_id == user.id, ExamAttempt.paper_id == paper.id)
            .scalar() or 0
        ) + 1

        attempt = ExamAttempt(
            user_id=user.id,
            paper_id=paper.id,
            attempt_index=int(next_idx),
            start_time=now,
            status="IN_PROGRESS",
            created_at=now,  # 关键：补上创建时间
        )
        db.add(attempt); db.commit()

    except IntegrityError as e:
        db.rollback()
        log.exception("create_session IntegrityError")
        msg = _err_msg(e)

        if "created_at" in msg:
            raise AppException("创建练习失败：时间戳为空", code=400, status_code=400)

        if "uk_attempt_user_paper_idx" in msg:
            existed = (
                db.query(ExamAttempt)
                .filter(ExamAttempt.user_id == user.id, ExamAttempt.paper_id == paper.id)
                .order_by(ExamAttempt.attempt_index.desc())
                .first()
            )
            if existed:
                total = db.query(PaperQuestion).filter(PaperQuestion.paper_id == existed.paper_id).count()
                return existed.id, existed.paper_id, int(total), 1
            raise AppException("会话冲突，请稍后重试", code=409, status_code=409)

        if "uk_paper_seq" in msg or "uk_paper_question" in msg:
            # 极小概率冲突，换一张试卷重试一次
            now = datetime.utcnow()
            paper = Paper(
                title=_new_title(), is_public=False, status="PRACTICE",
                created_by=user.id, created_at=now, updated_at=now
            )
            db.add(paper); db.flush()
            for i, qid in enumerate(question_ids, start=1):
                db.add(PaperQuestion(paper_id=paper.id, question_id=qid, seq=i, score=1))
            db.flush()
            attempt = ExamAttempt(
                user_id=user.id, paper_id=paper.id, attempt_index=1,
                start_time=now, status="IN_PROGRESS",
                created_at=now,  # 关键：补上创建时间
            )
            db.add(attempt); db.commit()
        else:
            raise AppException("唯一约束冲突，请稍后重试", code=409, status_code=409)

    total = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper.id).count()
    return attempt.id, paper.id, int(total), 1

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
