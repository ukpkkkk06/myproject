from typing import List, Optional
from fastapi import APIRouter, Depends, Body, Path, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeNode, QuestionKnowledgeItem
from app.services import knowledge_service
from app.models.user import User
from app.models.knowledge_point import KnowledgePoint
from app.models.question_knowledge import QuestionKnowledge
from app.models.question import Question
from app.models.question_version import QuestionVersion

router = APIRouter()

@router.get("/knowledge/tree", response_model=List[KnowledgeNode])
def tree(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    """
    获取知识点树
    🔒 权限控制: 
    - 管理员可以看到所有知识点
    - 普通用户只能看到自己创建的知识点
    """
    return knowledge_service.list_tree(db, user=me)

@router.post("/knowledge", response_model=KnowledgeNode)
def create(body: KnowledgeCreate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    """
    创建知识点
    🔒 记录创建者
    """
    return knowledge_service.create(db, body.name, body.parent_id, body.description, body.depth, user=me)

@router.put("/knowledge/{kid}", response_model=KnowledgeNode)
def update(kid: int, body: KnowledgeUpdate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    """
    更新知识点
    🔒 权限控制: 只能修改自己创建的知识点
    """
    return knowledge_service.update(db, kid, body.name, body.parent_id, body.description, body.depth, user=me)

@router.delete("/knowledge/{kid}")
def remove(kid: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    """
    删除知识点
    🔒 权限控制: 只能删除自己创建的知识点
    """
    knowledge_service.delete(db, kid, user=me)
    return {"ok": True}

# 🔒 获取题目作者ID辅助函数
def _get_question_owner_id(q: Question, db: Session) -> Optional[int]:
    if hasattr(q, "created_by"):
        return getattr(q, "created_by")
    if hasattr(q, "current_version_id") and q.current_version_id:
        return db.query(QuestionVersion.created_by)\
                 .filter(QuestionVersion.id == q.current_version_id)\
                 .scalar()
    return None

@router.put("/questions/{qid}/knowledge")
def bind_question_knowledge(qid: int = Path(...), items: List[QuestionKnowledgeItem] = Body(...), db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    """
    绑定题目与知识点
    🔒 权限控制：
    1. 验证用户是否有权修改该题目
    2. 验证用户是否有权使用这些知识点
    """
    # 🔒 权限控制：验证用户是否有权修改该题目
    q = db.query(Question).filter(Question.id == qid).first()
    if not q:
        raise HTTPException(404, "题目不存在")
    
    uid = getattr(me, "id", None)
    is_admin = bool(getattr(me, "is_admin", False))
    owner_id = _get_question_owner_id(q, db)
    if not is_admin and (owner_id is not None) and (owner_id != uid):
        raise HTTPException(403, "无权限修改此题目")
    
    # 🔒 传递用户信息以验证知识点权限
    knowledge_service.bind_question_knowledge(db, qid, [i.dict() for i in items], user=me)
    return {"ok": True}

# 构造知识点路径
def _kp_path(db: Session, kid: int) -> str:
    cur = db.query(KnowledgePoint).filter(KnowledgePoint.id == kid).first()
    if not cur:
        return f"#{kid}"
    names = [cur.name]
    while cur.parent_id:
        cur = db.query(KnowledgePoint).filter(KnowledgePoint.id == cur.parent_id).first()
        if not cur: break
        names.append(cur.name)
    names.reverse()
    return "/".join(names)

@router.get("/questions/{qid}/knowledge")
def get_question_knowledge(
    qid: int,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    # 🔒 权限控制:验证用户是否有权访问该题目
    q = db.query(Question).filter(Question.id == qid).first()
    if not q:
        raise HTTPException(404, "题目不存在")
    
    uid = getattr(me, "id", None)
    is_admin = bool(getattr(me, "is_admin", False))
    owner_id = _get_question_owner_id(q, db)
    if not is_admin and (owner_id is not None) and (owner_id != uid):
        raise HTTPException(403, "无权限访问此题目")
    
    links = db.query(QuestionKnowledge).filter(QuestionKnowledge.question_id == qid).all()
    return [
        {"knowledge_id": int(lk.knowledge_id), "weight": lk.weight, "path": _kp_path(db, int(lk.knowledge_id))}
        for lk in links
    ]