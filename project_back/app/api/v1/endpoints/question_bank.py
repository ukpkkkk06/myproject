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

@router.get("/question-bank/my-questions", response_model=MyQuestionListResp)
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
    me: User = Depends(deps.get_current_user),  # 🔒 添加用户认证
):
    # 🔒 只返回当前用户创建的题目
    total, rows = question_bank_service.list_my_questions(
        db, me, page, size, keyword, qtype, difficulty, active_only,
        subject_id=subject_id, level_id=level_id
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
    
    # 调用 service 层
    uid = getattr(me, "id", None)
    is_admin = bool(getattr(me, "is_admin", False))
    rows = question_bank_service.get_questions_brief(db, id_list, uid, is_admin)
    
    items = []
    for r in rows:
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
    # 调用 service 层
    uid = getattr(me, "id", None)
    is_admin = bool(getattr(me, "is_admin", False))
    r = question_bank_service.get_question_detail(db, qid, uid, is_admin)
    
    # 构建返回对象
    result = {
        "id": r.id,
        "stem": r.stem or f"#{qid}",
        "options": _parse_options(getattr(r, "options", None)),
        "analysis": getattr(r, "analysis", None) or None,
    }
    
    # 添加 type、correct_answer 和 is_active 字段(如果存在)
    if hasattr(r, "type"):
        result["type"] = r.type
    if hasattr(r, "correct_answer"):
        result["correct_answer"] = r.correct_answer
    if hasattr(r, "is_active"):
        result["is_active"] = bool(r.is_active)
    
    return QuestionBrief(**result)

@router.get("/questions/{qid:int}", response_model=QuestionBrief)
def question_detail_alt(
    qid: int,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    return question_detail(qid=qid, db=db, me=me)

@router.put("/question-bank/questions/{qid:int}")
def update_question(
    qid: int,
    body: QuestionUpdate,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    # 调用 service 层
    uid = getattr(me, "id", None)
    is_admin = bool(getattr(me, "is_admin", False))
    return question_bank_service.update_question(db, qid, body, uid, is_admin)

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
    # 调用 service 层
    rows = question_bank_service.list_tags(db, type)
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
    # 调用 service 层
    uid = getattr(me, "id", None)
    is_admin = bool(getattr(me, "is_admin", False))
    result = question_bank_service.get_question_tags(db, qid, uid, is_admin)
    return QuestionTagsOut(**result)

# 设置题目的标签
@router.put("/question-bank/questions/{qid:int}/tags")
def set_question_tags(
    qid: int,
    body: SetQuestionTagsIn,
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),
):
    # 调用 service 层
    uid = getattr(me, "id", None)
    is_admin = bool(getattr(me, "is_admin", False))
    return question_bank_service.set_question_tags(db, qid, body, uid, is_admin)

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
