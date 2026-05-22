from fastapi import APIRouter, HTTPException
import httpx

from config import KEYCLOAK_URL,REALM, ADMIN_PASSWORD, ADMIN_USERNAME
from admin_token import get_admin_token
from realm.schema import RealmRequest


router = APIRouter()


@router.post("/realms", status_code=201)
async def create_realm(realm: RealmRequest):

    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
 
    realm_payload = {
        "realm": realm.realm_name,
        "displayName": realm.display_name or realm.realm_name,
        "enabled": realm.enabled,
        "registrationAllowed": realm.registration_allowed,
        "loginWithEmailAllowed": realm.login_with_email_allowed,
        "duplicateEmailsAllowed": realm.duplicate_emails_allowed,
        "resetPasswordAllowed": realm.reset_password_allowed,
        "editUsernameAllowed": realm.edit_username_allowed,
    }
 
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{KEYCLOAK_URL}/admin/realms",
            json=realm_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
 
    if response.status_code == 409:
        raise HTTPException(status_code=409, detail=f"Realm '{realm.realm_name}' already exists.")
 
    if response.status_code not in (201, 204):
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to create realm: {response.text}",
        )
 
    return {
        "message": f"Realm '{realm.realm_name}' created successfully.",
        "realm": realm.realm_name,
        "keycloak_url": f"{KEYCLOAK_URL}/realms/{realm.realm_name}",
    }
 