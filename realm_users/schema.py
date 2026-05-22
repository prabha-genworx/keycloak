from typing import Optional
from pydantic import BaseModel


class UserRequest(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str
    enabled: bool = True


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enabled: Optional[bool] = None
    password: Optional[str] = None