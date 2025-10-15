from typing import List, Optional
from fastapi import APIRouter, Depends, Body, Path
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeNode, QuestionKnowledgeItem
from app.services import knowledge_service
from app.models.user import User
from app.models.knowledge_point import KnowledgePoint
from app.models.question_knowledge import QuestionKnowledge

router = APIRouter()

@router.get("/knowledge/tree", response_model=List[KnowledgeNode])
def tree(db: Session = Depends(get_db)):
    return knowledge_service.list_tree(db)

@router.post("/knowledge", response_model=KnowledgeNode)
def create(body: KnowledgeCreate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    return knowledge_service.create(db, body.name, body.parent_id, body.description, body.level)

@router.put("/knowledge/{kid}", response_model=KnowledgeNode)
def update(kid: int, body: KnowledgeUpdate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    return knowledge_service.update(db, kid, body.name, body.parent_id, body.description, body.level)

@router.delete("/knowledge/{kid}")
def remove(kid: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    knowledge_service.delete(db, kid)
    return {"ok": True}

@router.put("/questions/{qid}/knowledge")
def bind_question_knowledge(qid: int = Path(...), items: List[QuestionKnowledgeItem] = Body(...), db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    knowledge_service.bind_question_knowledge(db, qid, [i.dict() for i in items])
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
    links = db.query(QuestionKnowledge).filter(QuestionKnowledge.question_id == qid).all()
    return [
        {"knowledge_id": int(lk.knowledge_id), "weight": lk.weight, "path": _kp_path(db, int(lk.knowledge_id))}
        for lk in links
    ]