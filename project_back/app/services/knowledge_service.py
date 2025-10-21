from typing import Dict, List, Optional, Iterable
from sqlalchemy.orm import Session
from app.core.exceptions import AppException
from app.models.knowledge_point import KnowledgePoint
from app.models.question_knowledge import QuestionKnowledge
from app.models.question import Question
from app.models.user import User

def list_tree(db: Session, user: Optional[User] = None) -> List[Dict]:
    """
    获取知识点树
    🔒 权限控制: 
    - 管理员可以看到所有知识点
    - 普通用户只能看到自己创建的知识点
    """
    # 🚀 优化：只查询必要字段，减少内存占用
    query = db.query(
        KnowledgePoint.id,
        KnowledgePoint.name,
        KnowledgePoint.parent_id,
        KnowledgePoint.depth,
        KnowledgePoint.created_by
    )
    
    # 🔒 权限过滤
    if user:
        is_admin = bool(getattr(user, "is_admin", False))
        if not is_admin:
            # 普通用户只能看到自己创建的知识点
            user_id = getattr(user, "id", None)
            query = query.filter(KnowledgePoint.created_by == user_id)
    
    rows = query.all()
    
    by_parent: Dict[Optional[int], List] = {}
    for row in rows:
        by_parent.setdefault(row.parent_id, []).append(row)

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

def create(db: Session, name: str, parent_id: Optional[int], description: Optional[str], depth: Optional[int], user: Optional[User] = None):
    """
    创建知识点
    🔒 记录创建者ID
    """
    if parent_id:
        parent = db.query(KnowledgePoint).filter(KnowledgePoint.id == parent_id).first()
        if not parent:
            raise AppException("父级知识点不存在", code=400, status_code=400)
        
        # 🔒 权限检查: 普通用户只能在自己创建的父节点下创建子节点
        if user and parent.created_by:
            is_admin = bool(getattr(user, "is_admin", False))
            user_id = getattr(user, "id", None)
            if not is_admin and parent.created_by != user_id:
                raise AppException("无权限在此父节点下创建知识点", code=403, status_code=403)
        
        # 🔥 自动计算 depth：父级的 depth + 1
        calculated_level = (parent.depth or 0) + 1
    else:
        # 🔥 根节点的 depth = 0
        calculated_level = 0
    
    # 🔥 记录创建者
    user_id = getattr(user, "id", None) if user else None
    
    # 🔥 使用计算出的 depth
    node = KnowledgePoint(
        name=name, 
        parent_id=parent_id, 
        description=description, 
        depth=calculated_level,
        created_by=user_id  # 🔒 记录创建者
    )
    db.add(node); db.commit(); db.refresh(node)
    return node

def update(db: Session, kid: int, name: Optional[str], parent_id: Optional[int], description: Optional[str], depth: Optional[int], user: Optional[User] = None):
    """
    更新知识点
    🔒 权限控制: 只能修改自己创建的知识点
    """
    node = db.query(KnowledgePoint).get(kid)
    if not node:
        raise AppException("知识点不存在", code=404, status_code=404)
    
    # 🔒 权限检查
    if user and node.created_by:
        is_admin = bool(getattr(user, "is_admin", False))
        user_id = getattr(user, "id", None)
        if not is_admin and node.created_by != user_id:
            raise AppException("无权限修改此知识点", code=403, status_code=403)
    
    if parent_id == kid:
        raise AppException("父级不能是自身", code=400, status_code=400)
    if parent_id:
        # 防循环
        if kid in descendants_ids(db, parent_id):
            raise AppException("不能将父级设置为自己的子孙节点", code=400, status_code=400)
        
        # 🔒 权限检查: 新父节点必须是自己创建的
        if user:
            new_parent = db.query(KnowledgePoint).filter(KnowledgePoint.id == parent_id).first()
            if new_parent and new_parent.created_by:
                is_admin = bool(getattr(user, "is_admin", False))
                user_id = getattr(user, "id", None)
                if not is_admin and new_parent.created_by != user_id:
                    raise AppException("无权限将知识点移动到此父节点下", code=403, status_code=403)
    
    # 🔥 更新基本字段
    if name is not None: node.name = name
    if description is not None: node.description = description
    
    # 🔥 如果修改了 parent_id，需要重新计算 depth
    if parent_id is not None and parent_id != node.parent_id:
        node.parent_id = parent_id
        if parent_id is None:
            # 变成根节点
            node.depth = 0
        else:
            # 获取新父节点的 depth
            parent = db.query(KnowledgePoint).filter(KnowledgePoint.id == parent_id).first()
            if parent:
                node.depth = (parent.depth or 0) + 1
            else:
                raise AppException("父级知识点不存在", code=400, status_code=400)
        
        # 🔥 递归更新所有子孙节点的 depth
        _update_descendants_level(db, kid)
    
    db.commit(); db.refresh(node)
    return node

def _update_descendants_level(db: Session, parent_id: int):
    """递归更新所有子孙节点的 depth"""
    parent = db.query(KnowledgePoint).filter(KnowledgePoint.id == parent_id).first()
    if not parent:
        return
    
    parent_level = parent.depth or 0
    children = db.query(KnowledgePoint).filter(KnowledgePoint.parent_id == parent_id).all()
    
    for child in children:
        child.depth = parent_level + 1
        db.add(child)
        # 递归更新子节点的子节点
        _update_descendants_level(db, child.id)
    
    db.commit()

def delete(db: Session, kid: int, user: Optional[User] = None):
    """
    删除知识点
    🔒 权限控制: 只能删除自己创建的知识点
    """
    node = db.query(KnowledgePoint).get(kid)
    if not node:
        return
    
    # 🔒 权限检查
    if user and node.created_by:
        is_admin = bool(getattr(user, "is_admin", False))
        user_id = getattr(user, "id", None)
        if not is_admin and node.created_by != user_id:
            raise AppException("无权限删除此知识点", code=403, status_code=403)
    
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

def bind_question_knowledge(db: Session, question_id: int, items: Iterable[dict], user: Optional[User] = None):
    """
    绑定题目与知识点的关系
    🔒 权限控制: 只能绑定自己创建的知识点
    """
    if not db.query(Question.id).filter(Question.id == question_id).first():
        raise AppException("题目不存在", code=404, status_code=404)
    
    # 🔒 权限检查: 验证所有知识点都是用户自己创建的
    if user:
        is_admin = bool(getattr(user, "is_admin", False))
        user_id = getattr(user, "id", None)
        
        for it in items:
            kid = int(it["knowledge_id"])
            kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kid).first()
            
            if not kp:
                raise AppException(f"知识点不存在: {kid}", code=400, status_code=400)
            
            # 🔒 非管理员只能绑定自己创建的知识点
            if not is_admin and kp.created_by and kp.created_by != user_id:
                raise AppException(f"无权限使用知识点: {kp.name}(ID:{kid})", code=403, status_code=403)
    
    # 覆盖式更新（幂等）
    db.query(QuestionKnowledge).filter(QuestionKnowledge.question_id == question_id).delete()
    
    for it in items:
        kid = int(it["knowledge_id"])
        db.add(QuestionKnowledge(question_id=question_id, knowledge_id=kid, weight=it.get("weight")))
    
    db.commit()