from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.api import deps
from app.models.tag import Tag
from app.models.user import User

router = APIRouter()

@router.get("/tags")
def list_tags(
    type: Optional[str] = Query(None, pattern="^(SUBJECT|LEVEL)$"),
    db: Session = Depends(deps.get_db),
    me: User = Depends(deps.get_current_user),  # 需要身份验证
):
    """获取标签列表 - 需要登录"""
    q = db.query(Tag).filter(Tag.is_active == True)
    if type:
        q = q.filter(Tag.type == type)
    rows = q.order_by(Tag.type.asc(), Tag.id.asc()).all()
    return [{"id": t.id, "type": t.type, "name": t.name} for t in rows]
