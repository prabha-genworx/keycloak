from typing import List, Optional
from pydantic import BaseModel


class ClientRequest(BaseModel):
    client_id: str
    enabled: bool = True
    public_client: bool = False
    secret: Optional[str] = None

class ClientUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    public_client: Optional[bool] = None
    secret: Optional[str] = None


    