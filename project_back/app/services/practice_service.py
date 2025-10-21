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
    """标准化单选答案：去空格，转大写"""
    return (ans or "").strip().upper()

def _norm_mc(ans: str) -> str:
    """标准化多选答案：去空格，转大写，字母排序，去重
    例如: 'BCA' -> 'ABC', 'AAB' -> 'AB'
    """
    return ''.join(sorted(set((ans or "").strip().upper())))

def _norm_fill(ans: str) -> str:
    """标准化填空答案：去除首尾空格，转小写
    支持多个答案用分号分隔，任意一个匹配即正确
    例如: "北京" -> "北京", " BEIJING " -> "beijing"
    """
    return (ans or "").strip().lower()

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

# ========== 🆕 智能推荐算法（方案2：完整版） ==========

import math
import random

def calculate_time_decay_smooth(last_wrong_time: datetime) -> float:
    """
    平滑的时间衰减系数（基于艾宾浩斯遗忘曲线）
    
    公式: y = 0.6 + 2.0 × e^(-0.12 × days)
    
    Returns:
        float: 衰减系数，范围 0.6 ~ 2.6
    """
    if not last_wrong_time:
        return 1.0
    
    now = datetime.now()
    hours = (now - last_wrong_time).total_seconds() / 3600
    
    # 特殊处理：1小时内权重最高
    if hours < 1:
        return 2.6
    
    days = (now - last_wrong_time).days
    
    # 指数衰减曲线
    return 0.6 + 2.0 * math.exp(-0.12 * days)

def calculate_depth_coefficient(level: int) -> float:
    """
    计算知识点深度系数
    层级越深，权重越高（更具体的知识点）
    
    Args:
        level: 知识点层级 (0=根节点)
    
    Returns:
        float: 深度系数，每深一层增加0.3
    """
    return 1.0 + (level * 0.3)

def get_direct_error_weight(db: Session, user_id: int, knowledge_id: int) -> float:
    """
    获取知识点的直接错误权重（不含继承）
    
    公式: Σ(错误次数 × 时间衰减系数)
    """
    errors = db.query(
        ErrorBook.wrong_count,
        ErrorBook.last_wrong_time
    ).join(
        QuestionKnowledge, QuestionKnowledge.question_id == ErrorBook.question_id
    ).filter(
        ErrorBook.user_id == user_id,
        QuestionKnowledge.knowledge_id == knowledge_id,
        ErrorBook.mastered == False
    ).all()
    
    if not errors:
        return 0.0
    
    total_weight = 0.0
    for wrong_count, last_wrong in errors:
        time_coeff = calculate_time_decay_smooth(last_wrong)
        total_weight += wrong_count * time_coeff
    
    return total_weight

def get_ancestor_ids(db: Session, kp_id: int) -> List[int]:
    """获取知识点的所有祖先ID（向上遍历）"""
    ancestors = []
    current_id = kp_id
    max_depth = 10  # 防止死循环
    
    for _ in range(max_depth):
        kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == current_id).first()
        if not kp or not kp.parent_id:
            break
        ancestors.append(kp.parent_id)
        current_id = kp.parent_id
    
    return ancestors

def calculate_inherited_weight(
    db: Session, 
    user_id: int, 
    knowledge_id: int,
    cache: dict
) -> float:
    """
    计算知识点的继承权重（包含祖先节点影响）
    
    公式: 直接权重 + Σ(祖先权重 × 0.6^距离)
    
    Args:
        cache: 缓存字典，避免重复计算
    """
    # 缓存检查
    cache_key = f"inherited_{user_id}_{knowledge_id}"
    if cache_key in cache:
        return cache[cache_key]
    
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == knowledge_id).first()
    if not kp:
        return 0.0
    
    # 1. 直接权重
    direct_weight = get_direct_error_weight(db, user_id, knowledge_id)
    
    # 2. 继承权重（遍历祖先）
    inherited_weight = 0.0
    current_parent_id = kp.parent_id
    distance = 1
    decay_base = 0.6  # 继承衰减基数
    
    while current_parent_id:
        parent = db.query(KnowledgePoint).filter(
            KnowledgePoint.id == current_parent_id
        ).first()
        
        if not parent:
            break
        
        # 父节点的直接权重
        parent_weight = get_direct_error_weight(db, user_id, current_parent_id)
        
        # 应用距离衰减
        decay_factor = decay_base ** distance
        inherited_weight += parent_weight * decay_factor
        
        # 继续向上
        current_parent_id = parent.parent_id
        distance += 1
        
        if distance > 10:  # 防止无限循环
            break
    
    total_weight = direct_weight + inherited_weight
    
    # 缓存结果
    cache[cache_key] = total_weight
    return total_weight

def get_weak_point_questions_smart(
    db: Session, 
    user_id: int, 
    size: int,
    subject_id: Optional[int] = None
) -> List[int]:
    """
    智能推荐抽题（方案2：完整版）
    
    包含：时间衰减 + 深度权重 + 父子继承
    
    Returns:
        List[int]: 题目ID列表
    """
    cache = {}  # 本次请求的临时缓存
    
    # 1. 获取用户错题关联的知识点
    error_kps_query = db.query(QuestionKnowledge.knowledge_id).join(
        ErrorBook, ErrorBook.question_id == QuestionKnowledge.question_id
    ).filter(
        ErrorBook.user_id == user_id,
        ErrorBook.mastered == False
    )
    
    # 如果指定学科，过滤学科
    if subject_id:
        error_kps_query = error_kps_query.join(
            Question, Question.id == QuestionKnowledge.question_id
        ).join(
            QuestionTag, QuestionTag.question_id == Question.id
        ).filter(QuestionTag.tag_id == subject_id)
    
    error_kps = error_kps_query.distinct().all()
    
    if not error_kps:
        return []  # 无错题，返回空
    
    kp_ids = [kp.knowledge_id for kp in error_kps]
    
    # 2. 扩展到祖先节点（考虑层级影响）
    all_kps = set(kp_ids)
    for kp_id in kp_ids:
        ancestors = get_ancestor_ids(db, kp_id)
        all_kps.update(ancestors)
    
    # 3. 计算每个知识点的综合权重
    kp_weights = []
    for kp_id in all_kps:
        kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
        if not kp:
            continue
        
        # 继承权重（含祖先影响）
        inherited = calculate_inherited_weight(db, user_id, kp_id, cache)
        
        # 深度系数（越深越重要）
        depth_coeff = calculate_depth_coefficient(kp.depth or 0)
        
        # 最终权重
        final_weight = inherited * depth_coeff
        
        if final_weight > 0:
            kp_weights.append({
                'kp_id': kp_id,
                'weight': final_weight,
                'level': kp.depth or 0
            })
    
    if not kp_weights:
        return []
    
    # 4. 按权重排序，取top知识点
    kp_weights.sort(key=lambda x: x['weight'], reverse=True)
    top_kps = kp_weights[:10]  # 取前10个薄弱知识点
    
    # 5. 从薄弱知识点中加权抽题
    question_ids = []
    total_weight = sum(kp['weight'] for kp in top_kps)
    
    for kp_info in top_kps:
        # 按权重分配题目数量
        ratio = kp_info['weight'] / total_weight
        limit = max(1, int(size * ratio * 1.5))  # 多抽一些备用
        
        # 🔒 从该知识点抽题（只抽用户自己创建的题目）
        q = db.query(Question.id).join(
            QuestionVersion, QuestionVersion.question_id == Question.id
        ).join(
            QuestionKnowledge, QuestionKnowledge.question_id == Question.id
        ).filter(
            QuestionKnowledge.knowledge_id == kp_info['kp_id'],
            Question.is_active == True,
            QuestionVersion.created_by == user_id  # 🔒 只抽用户自己的题目
        )
        
        # 排除已掌握的题目
        mastered_ids = db.query(ErrorBook.question_id).filter(
            ErrorBook.user_id == user_id,
            ErrorBook.mastered == True
        ).subquery()
        
        q = q.filter(~Question.id.in_(mastered_ids))
        
        # 如果指定学科，过滤学科
        if subject_id:
            q = q.join(QuestionTag).filter(QuestionTag.tag_id == subject_id)
        
        questions = q.order_by(func.rand()).limit(limit).all()
        question_ids.extend([q.id for q in questions])
    
    # 6. 去重、打乱、截取
    question_ids = list(set(question_ids))
    random.shuffle(question_ids)
    return question_ids[:size]

def get_hard_questions(
    db: Session, 
    user_id: int,  # 🔒 添加用户ID参数
    size: int, 
    subject_id: Optional[int] = None
) -> List[int]:
    """
    获取用户的难题（基于difficulty字段）
    """
    # 🔒 只查询用户自己创建的难题
    q = db.query(Question.id).join(
        QuestionVersion, QuestionVersion.question_id == Question.id
    ).filter(
        Question.is_active == True,
        Question.difficulty >= 4,  # 难度>=4的题目
        QuestionVersion.created_by == user_id  # 🔒 只查用户自己的题目
    )
    
    if subject_id:
        q = q.join(QuestionTag).filter(QuestionTag.tag_id == subject_id)
    
    questions = q.order_by(func.rand()).limit(size).all()
    return [q.id for q in questions]

def get_random_questions(
    db: Session, 
    user_id: int,  # 🔒 添加用户ID参数
    size: int, 
    subject_id: Optional[int] = None,
    question_types: Optional[List[str]] = None
) -> List[int]:
    """
    随机抽题（只抽用户自己的题目）
    """
    # 🔒 只查询用户自己创建的题目
    q = db.query(Question.id).join(
        QuestionVersion, QuestionVersion.question_id == Question.id
    ).filter(
        Question.is_active == True,
        QuestionVersion.created_by == user_id  # 🔒 只查用户自己的题目
    )
    
    if subject_id:
        q = q.join(QuestionTag).filter(QuestionTag.tag_id == subject_id)
    
    if question_types:
        q = q.filter(Question.type.in_(question_types))
    
    questions = q.order_by(func.rand()).limit(size).all()
    return [q.id for q in questions]

# ========== 智能推荐算法结束 ==========

def create_session(
    db: Session, 
    user: User, 
    size: int, 
    subject_id: Optional[int] = None, 
    knowledge_id: Optional[int] = None, 
    include_children: bool = False,
    question_types: Optional[List[str]] = None,
    practice_mode: str = 'RANDOM'  # 🆕 练习模式
) -> tuple[int, int, int, int]:
    """创建练习会话；支持三种练习模式。异常通过 AppException 抛出，交给统一异常处理器。
    Args:
        db (Session): 数据库会话
        user (User): 用户对象
        size (int): 题目数量
        subject_id (Optional[int], optional): 学科 ID. Defaults to None.
        knowledge_id (Optional[int], optional): 知识点 ID. Defaults to None.
        include_children (bool, optional): 是否包含子知识点. Defaults to False.
        question_types (Optional[List[str]], optional): 题型列表 ['SC', 'MC', 'FILL']. Defaults to None (全部题型).
        practice_mode (str, optional): 练习模式 'RANDOM'|'SMART'|'WEAK_POINT'. Defaults to 'RANDOM'.
    Raises:
        AppException: 自定义异常
    Returns:
        tuple[int, int, int, int]: 会话 ID, 试卷 ID, 题目总数, 当前题序
    """
    size = max(1, min(int(size or 5), 50))
    
    # 默认支持所有题型
    if question_types is None or not question_types:
        question_types = ["SC", "MC", "FILL"]

    # 仅当未指定学科和题型且为随机模式时复用未完成会话
    if practice_mode == 'RANDOM' and subject_id is None and (question_types == ["SC", "MC", "FILL"] or question_types is None):
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

    # 🆕 根据练习模式选择抽题策略
    question_ids = []
    
    if practice_mode == 'SMART':
        # 🤖 智能推荐：60% 错题知识点 + 30% 全局难题 + 10% 随机题
        log.info(f"[SMART模式] 用户{user.id}开始智能推荐抽题")
        
        weak_size = int(size * 0.6)
        hard_size = int(size * 0.3)
        rand_size = size - weak_size - hard_size  # 剩余部分
        
        # 🔒 从错题知识点抽题（只抽用户自己的题目）
        weak_ids = get_weak_point_questions_smart(db, user.id, weak_size, subject_id)
        log.info(f"[SMART模式] 从薄弱知识点抽取 {len(weak_ids)} 题")
        
        # 🔒 从全局难题抽题（只抽用户自己的题目）
        hard_ids = get_hard_questions(db, user.id, hard_size, subject_id)
        log.info(f"[SMART模式] 从全局难题抽取 {len(hard_ids)} 题")
        
        # 🔒 随机题补充（只抽用户自己的题目）
        rand_ids = get_random_questions(db, user.id, rand_size, subject_id, question_types)
        log.info(f"[SMART模式] 随机抽取 {len(rand_ids)} 题")
        
        question_ids = weak_ids + hard_ids + rand_ids
        
        # 如果题目不足，用随机题补充
        if len(question_ids) < size:
            log.warning(f"[SMART模式] 题目不足，补充随机题")
            extra = get_random_questions(db, user.id, size - len(question_ids), subject_id, question_types)
            question_ids.extend(extra)
        
        # 打乱顺序
        random.shuffle(question_ids)
        question_ids = question_ids[:size]
    
    elif practice_mode == 'WEAK_POINT':
        # 🎯 薄弱专项：100% 错题知识点
        log.info(f"[WEAK_POINT模式] 用户{user.id}开始薄弱专项抽题")
        
        # 🔒 只抽用户自己的题目
        question_ids = get_weak_point_questions_smart(db, user.id, size, subject_id)
        log.info(f"[WEAK_POINT模式] 从薄弱知识点抽取 {len(question_ids)} 题")
        
        # 如果错题不足，降级为随机模式
        if len(question_ids) < size:
            log.warning(f"[WEAK_POINT模式] 错题不足，补充随机题")
            extra = get_random_questions(db, user.id, size - len(question_ids), subject_id, question_types)
            question_ids.extend(extra)
    
    else:  # RANDOM
        # 🎲 随机练习（原有逻辑）
        log.info(f"[RANDOM模式] 用户{user.id}开始随机抽题")
        # 🔒 只抽用户自己的题目
        question_ids = get_random_questions(db, user.id, size, subject_id, question_types)
    
    if not question_ids:
        raise AppException("暂无可用题目", code=404, status_code=404)

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

    # 🔥 根据题型选择不同的验证方式
    if q.type == "MC":
        # 多选题：比较排序后的字母集合
        correct = _norm_mc(user_answer) == _norm_mc(qv.correct_answer)
    elif q.type == "FILL":
        # 🆕 填空题：支持多答案(分号分隔),任一匹配即正确
        correct_answers = [_norm_fill(a) for a in qv.correct_answer.split(';')]
        user_ans = _norm_fill(user_answer)
        correct = user_ans in correct_answers
    else:
        # 单选题：比较单个字母
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
