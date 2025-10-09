from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.api import deps
from app.models.tag import Tag

router = APIRouter()

@router.get("/tags")
def list_tags(
    type: Optional[str] = Query(None, pattern="^(SUBJECT|LEVEL)$"),
    db: Session = Depends(deps.get_db),
):
    q = db.query(Tag).filter(Tag.is_active == True)
    if type:
        q = q.filter(Tag.type == type)
    rows = q.order_by(Tag.type.asc(), Tag.id.asc()).all()
    return [{"id": t.id, "type": t.type, "name": t.name} for t in rows]
