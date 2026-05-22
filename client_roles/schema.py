from typing import Optional
from pydantic import BaseModel


class ClientRoleRequest(BaseModel):
    name: str
    description: Optional[str] = None


class ClientRoleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None