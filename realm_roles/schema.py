from typing import Optional

from pydantic import BaseModel


class RoleRequest(BaseModel):
    name: str
    description: Optional[str] = None