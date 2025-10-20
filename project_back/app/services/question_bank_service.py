from openpyxl import load_workbook
from fastapi import HTTPException
from app.models.question import Question
from app.models.question_version import QuestionVersion
from app.models.tag import Tag, QuestionTag
from sqlalchemy.orm import Session
from app.schemas.question_bank import ImportQuestionsResult, ImportErrorItem
from typing import Dict
from sqlalchemy import select, exists
import json
from app.models.user import User  # 修复未定义 User

HEADER_EXPECT = ["题干","选项A","选项B","选项C","选项D","题型(单选/多选/填空)","正确答案（单选多选请填入ABCD,填空直接填入答案，不同方式用;隔开如:BEIJNG;beijng）","解析","学科（数学，英语，化学，物理，语文）","学段（小学，初中，高中，大学）"]
ANSWER_KEYS = ["A","B","C","D"]
QUESTION_TYPES = {"单选": "SC", "多选": "MC", "填空": "FILL"}  # 🆕 添加填空题型

def _get_or_none(tag_map: Dict[str, Tag], name: str):
    if not name:
        return None
    return tag_map.get(name.strip())

def import_questions_from_excel(db: Session, file_path: str, user_id: int) -> ImportQuestionsResult:
    try:
        wb = load_workbook(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无法读取Excel: {e}")
    ws = wb.active
    header = [ (ws.cell(row=1,column=i+1).value or "").strip() for i in range(len(HEADER_EXPECT)) ]
    if header != HEADER_EXPECT:
        raise HTTPException(status_code=400, detail="模板表头不匹配，请下载最新模板")

    tags = db.execute(select(Tag).where(Tag.type.in_(["SUBJECT","LEVEL"]))).scalars().all()
    tag_map = {t.name.strip(): t for t in tags}

    result = ImportQuestionsResult(total_rows=0, success=0, failed=0, errors=[])

    def cell_str(row:int, col:int) -> str:
        return str(ws.cell(row=row, column=col).value or "").strip()

    for r in range(2, ws.max_row+1):
        # 跳过纯空行
        if all((cell_str(r, c) == "") for c in range(1, 6)):
            continue
        result.total_rows += 1
        try:
            stem = cell_str(r, 1)
            if not stem:
                raise ValueError("题干为空")
            
            # 🔥 检查题干是否重复（仅当前用户、仅激活题目）
            # 明确指定 JOIN 条件，避免歧义
            existing = db.query(QuestionVersion).join(
                Question, 
                QuestionVersion.question_id == Question.id
            ).filter(
                QuestionVersion.stem == stem,
                QuestionVersion.created_by == user_id,
                Question.is_active == True,
                QuestionVersion.is_active == 1
            ).first()
            
            if existing:
                raise ValueError(f"题目重复：您已创建过相同题干的题目（题目ID: {existing.question_id}）")
            
            A = cell_str(r, 2)
            B = cell_str(r, 3)
            C = cell_str(r, 4)
            D = cell_str(r, 5)
            qtype_str = cell_str(r, 6)  # 🆕 题型列（单选/多选）
            correct = cell_str(r, 7).upper()  # 🆕 正确答案移到第7列
            analysis = cell_str(r, 8)  # 🆕 解析移到第8列
            subject_name = cell_str(r, 9)  # 🆕 学科移到第9列
            level_name = cell_str(r, 10)  # 🆕 学段移到第10列
            
            # 🆕 验证题型
            if qtype_str not in QUESTION_TYPES:
                raise ValueError(f"题型必须是'单选'、'多选'或'填空'，当前值：{qtype_str}")
            
            qtype = QUESTION_TYPES[qtype_str]  # SC 或 MC 或 FILL
            
            # 🆕 根据题型验证答案
            if qtype == "SC":
                if not all([A, B, C, D]):
                    raise ValueError("单选题必须填写所有选项A/B/C/D")
                if correct not in ANSWER_KEYS:
                    raise ValueError("单选题正确选项必须是 A/B/C/D 之一")
            elif qtype == "MC":
                if not all([A, B, C, D]):
                    raise ValueError("多选题必须填写所有选项A/B/C/D")
                if not correct or len(correct) < 2:
                    raise ValueError("多选题至少要有2个正确答案")
                if not all(c in ANSWER_KEYS for c in correct):
                    raise ValueError(f"多选题正确选项必须是 A/B/C/D 的组合，如 ABC，当前值：{correct}")
                # 标准化多选答案：去重并排序（例如 "BCA" -> "ABC"）
                correct = "".join(sorted(set(correct)))
            elif qtype == "FILL":
                # 🆕 填空题验证
                if not correct:
                    raise ValueError("填空题答案不能为空，请在'正确答案'列填写文本答案（支持用分号分隔多个答案，如：北京;beijing）")
                # 🆕 提示用户：填空题不需要填写选项
                if any([A, B, C, D]):
                    raise ValueError("填空题不需要填写选项A/B/C/D，请将这些列留空")

            # 🆕 根据题型设置选项
            if qtype == "FILL":
                # 填空题不需要选项
                options = None
            else:
                # 单选题和多选题需要选项
                options = [
                    {"key":"A","text":A},
                    {"key":"B","text":B},
                    {"key":"C","text":C},
                    {"key":"D","text":D},
                ]

            # 🆕 根据题型创建 Question
            q = Question(type=qtype, is_active=True)
            if hasattr(q, "created_by"):
                setattr(q, "created_by", user_id)
            db.add(q)
            db.flush()  # 拿到 q.id

            # 关键：设置 version_no=1，并置 is_active
            qv = QuestionVersion(question_id=q.id, version_no=1, is_active=1)
            setattr(qv, "stem", stem)
            
            # 🆕 根据题型设置 options
            if qtype == "FILL":
                # 填空题不设置 options
                if hasattr(qv, "options"):
                    qv.options = None
            else:
                # 单选题和多选题设置 options
                if hasattr(qv, "options"):
                    qv.options = options
                elif hasattr(qv, "choices"):
                    qv.choices = json.dumps([o["text"] for o in options], ensure_ascii=False)

            if hasattr(qv, "analysis"):
                qv.analysis = analysis
            elif hasattr(qv, "explanation"):
                qv.explanation = analysis

            if hasattr(qv, "correct_answer"):
                qv.correct_answer = correct
            elif hasattr(qv, "answer"):
                qv.answer = correct

            if hasattr(qv, "created_by"):
                qv.created_by = user_id

            db.add(qv)
            db.flush()  # 拿到 qv.id

            if hasattr(q, "current_version_id"):
                q.current_version_id = qv.id
                db.add(q)

            # 关联标签
            subj_tag = _get_or_none(tag_map, subject_name)
            level_tag = _get_or_none(tag_map, level_name)
            if subj_tag:
                db.add(QuestionTag(question_id=q.id, tag_id=subj_tag.id))
            if level_tag:
                db.add(QuestionTag(question_id=q.id, tag_id=level_tag.id))

            # 每行成功后提交
            db.commit()
            result.success += 1

        except Exception as e:
            # 本行失败回滚并记录
            db.rollback()
            result.failed += 1
            result.errors.append(ImportErrorItem(row=r, reason=str(e)))

    # 末尾不再统一 commit
    return result

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
        q.order_by(Question.id.asc())
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
            .order_by(Question.id.asc())
            .offset((page-1)*size).limit(size).all())
    return {
        "total": total,
        "page": page,
        "items": [dict(r._mapping) for r in rows],
    }