from typing import Dict, List, Optional, Iterable
from sqlalchemy.orm import Session
from app.core.exceptions import AppException
from app.models.knowledge_point import KnowledgePoint
from app.models.question_knowledge import QuestionKnowledge
from app.models.question import Question

def list_tree(db: Session) -> List[Dict]:
    rows = db.query(KnowledgePoint).all()
    by_parent: Dict[Optional[int], List[KnowledgePoint]] = {}
    for n in rows:
        by_parent.setdefault(n.parent_id, []).append(n)

    def build(pid: Optional[int]) -> List[Dict]:
        result: List[Dict] = []
        for n in sorted(by_parent.get(pid, []), key=lambda x: ((x.depth or 0), x.id)):
            result.append({
                "id": n.id,
                "name": n.name,
                "parent_id": n.parent_id,
                "depth": n.depth,
                "children": build(n.id)
            })
        return result

    return build(None)

def create(db: Session, name: str, parent_id: Optional[int], description: Optional[str], depth: Optional[int]):
    if parent_id:
        if not db.query(KnowledgePoint.id).filter(KnowledgePoint.id == parent_id).first():
            raise AppException("父级知识点不存在", code=400, status_code=400)
    node = KnowledgePoint(name=name, parent_id=parent_id, description=description, depth=depth)
    db.add(node); db.commit(); db.refresh(node)
    return node

def update(db: Session, kid: int, name: Optional[str], parent_id: Optional[int], description: Optional[str], depth: Optional[int]):
    node = db.query(KnowledgePoint).get(kid)
    if not node:
        raise AppException("知识点不存在", code=404, status_code=404)
    if parent_id == kid:
        raise AppException("父级不能是自身", code=400, status_code=400)
    if parent_id:
        # 防循环
        if kid in descendants_ids(db, parent_id):
            raise AppException("不能将父级设置为自己的子孙节点", code=400, status_code=400)
    if name is not None: node.name = name
    if description is not None: node.description = description
    if depth is not None: node.depth = depth
    if parent_id is not None: node.parent_id = parent_id
    db.commit(); db.refresh(node)
    return node

def delete(db: Session, kid: int):
    node = db.query(KnowledgePoint).get(kid)
    if not node:
        return
    # 有子节点禁止删
    if db.query(KnowledgePoint.id).filter(KnowledgePoint.parent_id == kid).first():
        raise AppException("请先删除子节点", code=400, status_code=400)
    # 被题目引用禁止删
    if db.query(QuestionKnowledge.id).filter(QuestionKnowledge.knowledge_id == kid).first():
        raise AppException("有题目绑定该知识点，无法删除", code=400, status_code=400)
    db.delete(node); db.commit()

def descendants_ids(db: Session, root_id: int) -> List[int]:
    rows = db.query(KnowledgePoint.id, KnowledgePoint.parent_id).all()
    by_parent: Dict[Optional[int], List[int]] = {}
    for i, p in rows:
        by_parent.setdefault(p, []).append(i)
    res: List[int] = []
    stack = [root_id]
    while stack:
        cur = stack.pop()
        childs = by_parent.get(cur, [])
        res.extend(childs)
        stack.extend(childs)
    return res

def bind_question_knowledge(db: Session, question_id: int, items: Iterable[dict]):
    if not db.query(Question.id).filter(Question.id == question_id).first():
        raise AppException("题目不存在", code=404, status_code=404)
    # 覆盖式更新（幂等）
    db.query(QuestionKnowledge).filter(QuestionKnowledge.question_id == question_id).delete()
    for it in items:
        kid = int(it["knowledge_id"])
        if not db.query(KnowledgePoint.id).filter(KnowledgePoint.id == kid).first():
            raise AppException(f"知识点不存在: {kid}", code=400, status_code=400)
        db.add(QuestionKnowledge(question_id=question_id, knowledge_id=kid, weight=it.get("weight")))
    db.commit()