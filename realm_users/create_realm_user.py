import httpx
from fastapi import APIRouter, HTTPException
from realm_users.schema import UserRequest
from realm_users.config import REALM , ADMIN_PASSWORD, ADMIN_USERNAME
from config import KEYCLOAK_URL
from admin_token import get_admin_token

router = APIRouter()

@router.post("/users")
async def create_realm_user(user: UserRequest):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"

    payload = {
        "username": user.username,
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "enabled": user.enabled,
        "credentials": [
            {
                "type": "password",
                "value": user.password,
                "temporary": False
            }
        ],
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)

    if r.status_code not in (201, 409):
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return {
        "message": "User created successfully",
        "username": user.username
    }


