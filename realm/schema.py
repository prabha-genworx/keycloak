from typing import Optional

from pydantic import BaseModel


class RealmRequest(BaseModel):
    realm_name: str
    display_name: Optional[str] = None
    enabled: bool = True
    registration_allowed: bool = False
    login_with_email_allowed: bool = True
    duplicate_emails_allowed: bool = False
    reset_password_allowed: bool = True
    edit_username_allowed: bool = False
