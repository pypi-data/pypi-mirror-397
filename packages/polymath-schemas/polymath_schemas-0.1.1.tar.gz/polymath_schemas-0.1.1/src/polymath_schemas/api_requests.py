from pydantic import BaseModel
from typing import Optional, Literal

class CreateNode(BaseModel):
    human_rep: str
    lean_rep: str 
    verification: Optional[int] 

class CreateStatement(CreateNode):
    category: str

class CreateImplication(CreateNode):
    logic_op: Literal['AND', 'OR']
    premises_ids: list[str]
    concludes_ids: list[str]

class NodePatchRequest(BaseModel):
    human_rep: Optional[str] = None
    lean_rep: Optional[str] = None
    verification: Optional[int] = None
