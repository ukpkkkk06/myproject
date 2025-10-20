from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class KnowledgeCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    depth: Optional[int] = None

class KnowledgeUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    depth: Optional[int] = None

class KnowledgeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    parent_id: int | None = None
    depth: int | None = None
    children: list["KnowledgeNode"] = []

KnowledgeNode.update_forward_refs()

class QuestionKnowledgeItem(BaseModel):
    knowledge_id: int
    weight: Optional[int] = None