from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeNode
from app.services import knowledge_service
from app.models.user import User

router = APIRouter()

@router.get("/tree", response_model=List[KnowledgeNode])
def tree(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    """
    获取知识点树
    🔒 权限控制: 
    - 管理员可以看到所有知识点
    - 普通用户只能看到自己创建的知识点
    """
    return knowledge_service.list_tree(db, user=me)

@router.post("", response_model=KnowledgeNode)
def create(body: KnowledgeCreate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    """
    创建知识点
    🔒 记录创建者
    """
    return knowledge_service.create(db, body.name, body.parent_id, body.description, body.depth, user=me)

@router.put("/{kid}", response_model=KnowledgeNode)
def update(kid: int, body: KnowledgeUpdate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    """
    更新知识点
    🔒 权限控制: 只能修改自己创建的知识点
    """
    return knowledge_service.update(db, kid, body.name, body.parent_id, body.description, body.depth, user=me)

@router.delete("/{kid}")
def remove(kid: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    """
    删除知识点
    🔒 权限控制: 只能删除自己创建的知识点
    """
    knowledge_service.delete(db, kid, user=me)
    return {"ok": True}
