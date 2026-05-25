from typing import Optional
from pydantic import BaseModel


class OrganizationRequest(BaseModel):
    name: str
    enabled: bool = True


class OrganizationUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    