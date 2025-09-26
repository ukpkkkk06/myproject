from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.question_bank import MyQuestionListResp, MyQuestionItem, QuestionsBriefResp, QuestionBrief
from app.services import question_bank_service
from typing import List
from app.models.question import Question
from app.models.question_version import QuestionVersion
import json

router = APIRouter()

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
            stem=r.stem[:120],
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
