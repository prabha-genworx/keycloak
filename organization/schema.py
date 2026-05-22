from typing import Optional
from pydantic import BaseModel


class OrganizationRequest(BaseModel):
    name: str
    display_name: Optional[str] = None
    enabled: bool = True


class OrganizationUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    enabled: Optional[bool] = None
    