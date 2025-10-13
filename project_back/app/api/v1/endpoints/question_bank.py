import json
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.api import deps
from app.services import question_bank_service
import tempfile
from pathlib import Path
from fastapi.responses import FileResponse
import logging
import os

# ==== 新增导入：Pydantic 响应/请求模型 ====
from app.schemas.question_bank import (
    MyQuestionListResp,
    MyQuestionItem,
    QuestionsBriefResp,
    QuestionBrief,
    QuestionUpdate,
    TagOut,
    QuestionTagsOut,
    SetQuestionTagsIn,
    ImportQuestionsResult,
)
# ==== 新增导入：数据库模型 ====
from app.models.user import User
from app.models.question import Question
from app.models.question_version import QuestionVersion
from app.models.tag import Tag, QuestionTag

# 说明：
# - 上面导入的名称正好对应 Pylance 报“未定义”的符号
# - 若有未使用告警，可以暂时忽略；都在本文件中实际被引用

router = APIRouter()


# parents[4] 才是 project_back 根目录
TEMPLATE_FILE = Path(__file__).resolve().parents[4] / "Import template.xlsx"
logging.getLogger(__name__).debug(f"Import template path: {TEMPLATE_FILE}")

@router.get("/question-bank/import-template")
def download_import_template():
    if not TEMPLATE_FILE.exists():
        raise HTTPException(status_code=404, detail=f"模板不存在: {TEMPLATE_FILE}")
    return FileResponse(
        path=str(TEMPLATE_FILE),
        filename="题目导入模板.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/question-bank/my-questions")
def my_questions(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str | None = None,
    qtype: str | None = None,
    difficulty: int | None = Query(None, ge=1, le=5),
    active_only: bool = False,
    subject_id: int | None = Query(None),
    level_id: int | None = Query(None),
    db: Session = Depends(deps.get_db),
):
    return question_bank_service.get_my_questions(
        db, page, size, keyword, qtype, difficulty, active_only,
        subject_id=subject_id, level_id=level_id
    )

@router.get("/my-questions", response_model=MyQuestionListResp)
def list_my_questions(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None),
    qtype: str | None = Query(None),
    difficulty: int | None = Query(None),
    active_only: bool = Query(False),
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    total, rows = question_bank_service.list_my_questions(
        db, me, page=page, size=size, keyword=keyword,
        qtype=qtype, difficulty=difficulty, active_only=active_only
    )
    items = [
        MyQuestionItem(
            question_id=r.question_id,
            type=r.type,
            difficulty=r.difficulty,
            stem=(r.stem or "")[:120],  # 兜底，避免 None 切片报错
            audit_status=r.audit_status,
            is_active=bool(r.is_active),
            created_at=r.created_at,
            updated_at=r.updated_at,
        ) for r in rows
    ]
    return {"total": total, "page": page, "size": size, "items": items}

def _parse_options(val):
    # to List[{"key":str,"text":str}]
    if val is None:
        return None
    obj = val
    if isinstance(val, str):
        try:
            obj = json.loads(val)
        except Exception:
            obj = []
    res = []
    if isinstance(obj, dict):
        # 形如 {"A":"选项1","B":"选项2"}
        for i, (k, v) in enumerate(obj.items()):
            res.append({"key": k or chr(65+i), "text": str(v)})
    elif isinstance(obj, list):
        for i, it in enumerate(obj):
            if isinstance(it, dict):
                text = it.get("text") or it.get("content") or it.get("label") or ""
                key = it.get("key") or chr(65+i)
                res.append({"key": key, "text": str(text)})
            else:
                res.append({"key": chr(65+i), "text": str(it)})
    return res or None

def _options_to_db(val):
    """
    规范化前端传来的 options，返回 Python 列表[str]，供 JSON 列直接写入。
    - [{text:'A'}, {text:'B'}] -> ['A','B']
    - ['A','B'] -> ['A','B']
    - '{"k":"v"}' 或 其它 -> 尝试解析，最终确保是 list[str]
    """
    if val is None:
        return None
    try:
        # 若是字符串且长得像 JSON，先解析
        if isinstance(val, str):
            parsed = json.loads(val)
            val = parsed
    except Exception:
        pass

    out = []
    if isinstance(val, list):
        for it in val:
            if isinstance(it, dict):
                out.append((it.get("text") or it.get("content") or "").strip())
            else:
                out.append(str(it))
        return out
    # 其它类型：尽量转为单元素列表
    return [str(val)]

def _normalize_options_for_store(opts: Any) -> str:
    if not opts:
        return json.dumps([], ensure_ascii=False)
    arr = []
    if isinstance(opts, list):
        for i, it in enumerate(opts):
            if isinstance(it, dict):
                key = it.get("key") or chr(65 + i)
                text = it.get("text") or it.get("content") or ""
                arr.append({"key": key, "text": text})
            else:
                arr.append({"key": chr(65 + i), "text": str(it)})
    elif isinstance(opts, dict):
        for k, v in opts.items():
            arr.append({"key": str(k), "text": str(v)})
    return json.dumps(arr, ensure_ascii=False)

# 批量获取题目简要
@router.get("/question-bank/questions/brief", response_model=QuestionsBriefResp)
def questions_brief(ids: str = Query(..., description="逗号分隔的题目ID列表"),
                    db: Session = Depends(deps.get_db),
                    me: User = Depends(deps.get_current_user)):
    id_list: List[int] = []
    for s in (ids or "").split(","):
        s = s.strip()
        if s.isdigit():
            id_list.append(int(s))
    id_list = list(dict.fromkeys(id_list))[:100]
    if not id_list:
        return {"items": []}

    # 兼容字段名
    QV = QuestionVersion
    analysis_col = getattr(QV, "analysis", None) or getattr(QV, "explanation", None)
    options_col = getattr(QV, "options", None) or getattr(QV, "choices", None)

    cols = [Question.id.label("id"), QV.stem.label("stem")]
    if options_col is not None: cols.append(options_col.label("options"))
    if analysis_col is not None: cols.append(analysis_col.label("analysis"))

    rows = (
        db.query(*cols)
          .outerjoin(QV, Question.current_version_id == QV.id)
          .filter(Question.id.in_(id_list))
          .all()
    )
    by_id = {r.id: r for r in rows}
    items = []
    for qid in id_list:
        r = by_id.get(qid)
        if not r:
            continue
        items.append(QuestionBrief(
            id=r.id,
            stem=r.stem or f"#{r.id}",
            options=_parse_options(getattr(r, "options", None)),
            analysis=(getattr(r, "analysis", None) or None),
        ))
    return {"items": items}

# 兼容路径
@router.get("/questions/brief", response_model=QuestionsBriefResp)
def questions_brief_alt(ids: str = Query(...),
                        db: Session = Depends(deps.get_db),
                        me: User = Depends(deps.get_current_user)):
    return questions_brief(ids=ids, db=db, me=me)

# 单题详情（题干/选项/解析）
@router.get("/question-bank/questions/{qid:int}", response_model=QuestionBrief)
def question_detail(
    qid: int,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    QV = QuestionVersion
    analysis_col = getattr(QV, "analysis", None) or getattr(QV, "explanation", None)
    options_col = getattr(QV, "options", None) or getattr(QV, "choices", None)

    cols = [Question.id.label("id"), QV.stem.label("stem")]
    if options_col is not None: cols.append(options_col.label("options"))
    if analysis_col is not None: cols.append(analysis_col.label("analysis"))

    r = (db.query(*cols)
            .outerjoin(QV, Question.current_version_id == QV.id)
            .filter(Question.id == qid)
            .first())
    if not r:
        raise HTTPException(status_code=404, detail="题目不存在")
    return QuestionBrief(
        id=r.id,
        stem=r.stem or f"#{qid}",
        options=_parse_options(getattr(r, "options", None)),
        analysis=(getattr(r, "analysis", None) or None),
    )

@router.get("/questions/{qid:int}", response_model=QuestionBrief)
def question_detail_alt(
    qid: int,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    return question_detail(qid=qid, db=db, me=me)

# 兼容获取题目作者ID
def _get_question_owner_id(q: Question, db) -> Optional[int]:
    # 1) Question.created_by 优先
    if hasattr(q, "created_by"):
        return getattr(q, "created_by")
    # 2) 回退到版本表的 created_by
    if hasattr(q, "current_version_id") and q.current_version_id:
        return db.query(QuestionVersion.created_by)\
                 .filter(QuestionVersion.id == q.current_version_id)\
                 .scalar()
    return None

@router.put("/question-bank/questions/{qid:int}")
def update_question(
    qid: int,
    body: QuestionUpdate,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    q = db.query(Question).filter(Question.id == qid).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")

    uid = getattr(me, "id", None)
    is_admin = bool(getattr(me, "is_admin", False))
    owner_id = _get_question_owner_id(q, db)
    if not is_admin and (owner_id is not None) and (owner_id != uid):
        raise HTTPException(status_code=403, detail="无权限")

    # 获取题目版本（优先 current_version_id，其次按最新一条兜底）
    QV = QuestionVersion
    qv = None
    if hasattr(q, "current_version_id") and q.current_version_id:
        qv = db.query(QV).filter(QV.id == q.current_version_id).first()
    if not qv:
        qv = db.query(QV).filter(QV.question_id == q.id).order_by(QV.id.desc()).first()
    if not qv:
        raise HTTPException(status_code=404, detail="题目版本不存在")

    # 更新字段
    if body.stem is not None:
        qv.stem = body.stem.strip()

    if body.options is not None:
        val_list = _options_to_db(body.options)  # 这里返回 Python 列表[str]
        if val_list is not None:
            if hasattr(qv, "options"):            # JSON 列：直接写列表
                qv.options = val_list
            elif hasattr(qv, "choices"):          # 文本列：写 JSON 字符串
                qv.choices = json.dumps(val_list, ensure_ascii=False)

    if body.analysis is not None:
        if hasattr(qv, "analysis"):
            qv.analysis = body.analysis
        elif hasattr(qv, "explanation"):
            qv.explanation = body.analysis

    if body.correct_answer is not None:
        ca = (body.correct_answer or "").strip().upper()[:8]
        if hasattr(qv, "correct_answer"):
            qv.correct_answer = ca
        elif hasattr(qv, "answer"):
            qv.answer = ca

    if body.is_active is not None:
        if hasattr(qv, "is_active"):
            qv.is_active = bool(body.is_active)
        elif hasattr(q, "is_active"):
            q.is_active = bool(body.is_active)

    db.commit()
    return {"ok": True}

@router.put("/questions/{qid:int}")
def update_question_alt(
    qid: int,
    body: QuestionUpdate,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    # 兼容路由
    return update_question(qid=qid, body=body, db=db, me=me)

# 获取标签列表（按类型过滤：SUBJECT/LEVEL）
@router.get("/tags", response_model=List[TagOut])
def list_tags(
    type: Optional[str] = Query(default=None, description="SUBJECT/LEVEL/..."),
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    q = db.query(Tag)
    if type:
        q = q.filter(Tag.type == type)
    rows = q.order_by(Tag.type.asc(), Tag.name.asc()).all()
    return [
        TagOut(
            id=t.id,
            name=t.name,
            type=getattr(t, "type", None),
            parent_id=getattr(t, "parent_id", None),
            is_active=bool(getattr(t, "is_active", 1)),
        ) for t in rows
    ]

# 查询题目的标签
@router.get("/question-bank/questions/{qid:int}/tags", response_model=QuestionTagsOut)
def get_question_tags(
    qid: int,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    rows = (
        db.query(QuestionTag.tag_id, Tag.type)
        .join(Tag, Tag.id == QuestionTag.tag_id)
        .filter(QuestionTag.question_id == qid)
        .all()
    )
    subject_id = next((tid for tid, tp in rows if tp == "SUBJECT"), None)
    level_id = next((tid for tid, tp in rows if tp == "LEVEL"), None)
    return QuestionTagsOut(
        subject_id=subject_id,
        level_id=level_id,
        tag_ids=[tid for tid, _ in rows],
    )

# 设置题目的标签
@router.put("/question-bank/questions/{qid:int}/tags")
def set_question_tags(
    qid: int,
    body: SetQuestionTagsIn,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    q = db.query(Question).filter(Question.id == qid).first()
    if not q:
        raise HTTPException(404, "题目不存在")

    uid = getattr(me, "id", None)
    is_admin = bool(getattr(me, "is_admin", False))
    owner_id = _get_question_owner_id(q, db)
    if not is_admin and (owner_id is not None) and (owner_id != uid):
        raise HTTPException(403, "无权限")

    # SUBJECT 互斥
    if body.subject_id is not None:
        old_sids = [
            tid for (tid,) in db.query(QuestionTag.tag_id)
            .join(Tag, Tag.id == QuestionTag.tag_id)
            .filter(QuestionTag.question_id == qid, Tag.type == "SUBJECT").all()
        ]
        if old_sids:
            db.query(QuestionTag).filter(
                QuestionTag.question_id == qid,
                QuestionTag.tag_id.in_(old_sids)
            ).delete(synchronize_session=False)
        if body.subject_id:
            ok = db.query(Tag.id).filter(Tag.id == body.subject_id, Tag.type == "SUBJECT").first()
            if not ok:
                raise HTTPException(400, "subject_id 非法")
            exists = db.query(QuestionTag).filter(
                QuestionTag.question_id == qid, QuestionTag.tag_id == body.subject_id
            ).first()
            if not exists:
                db.add(QuestionTag(question_id=qid, tag_id=body.subject_id))

    # LEVEL 互斥
    if body.level_id is not None:
        old_lids = [
            tid for (tid,) in db.query(QuestionTag.tag_id)
            .join(Tag, Tag.id == QuestionTag.tag_id)
            .filter(QuestionTag.question_id == qid, Tag.type == "LEVEL").all()
        ]
        if old_lids:
            db.query(QuestionTag).filter(
                QuestionTag.question_id == qid,
                QuestionTag.tag_id.in_(old_lids)
            ).delete(synchronize_session=False)
        if body.level_id:
            ok = db.query(Tag.id).filter(Tag.id == body.level_id, Tag.type == "LEVEL").first()
            if not ok:
                raise HTTPException(400, "level_id 非法")
            exists = db.query(QuestionTag).filter(
                QuestionTag.question_id == qid, QuestionTag.tag_id == body.level_id
            ).first()
            if not exists:
                db.add(QuestionTag(question_id=qid, tag_id=body.level_id))

    # 可选批量增删
    if body.remove_ids:
        db.query(QuestionTag).filter(
            QuestionTag.question_id == qid,
            QuestionTag.tag_id.in_(body.remove_ids)
        ).delete(synchronize_session=False)
    if body.add_ids:
        for tid in body.add_ids:
            exists = db.query(QuestionTag).filter(
                QuestionTag.question_id == qid, QuestionTag.tag_id == tid
            ).first()
            if not exists:
                db.add(QuestionTag(question_id=qid, tag_id=tid))

    db.commit()
    return {"ok": True}

@router.post("/question-bank/import-excel", response_model=ImportQuestionsResult)
def import_excel(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user)
):
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx 文件")
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            content = file.file.read()
            tmp.write(content)
            tmp_path = tmp.name
        return question_bank_service.import_questions_from_excel(db, tmp_path, current_user.id)
    finally:
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
