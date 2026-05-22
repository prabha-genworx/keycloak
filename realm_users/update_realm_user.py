import httpx
from fastapi import APIRouter, HTTPException
from realm_users.schema import UserUpdateRequest
from realm_users.config import REALM, ADMIN_PASSWORD, ADMIN_USERNAME
from config import KEYCLOAK_URL
from admin_token import get_admin_token

router = APIRouter()


async def _get_user_id(token: str, username: str) -> str:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
            params={"username": username, "exact": True},
            headers={"Authorization": f"Bearer {token}"},
        )
    users = res.json()
    if not users:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
    return users[0]["id"]


@router.put("/users/{username}")
async def update_user(username: str, user: UserUpdateRequest):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
    user_id = await _get_user_id(token, username)

    payload = {}
    if user.email is not None:
        payload["email"] = user.email
    if user.first_name is not None:
        payload["firstName"] = user.first_name
    if user.last_name is not None:
        payload["lastName"] = user.last_name
    if user.enabled is not None:
        payload["enabled"] = user.enabled

    async with httpx.AsyncClient() as client:
        r = await client.put(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}",
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )

    if r.status_code not in (200, 204):
        raise HTTPException(status_code=r.status_code, detail=r.text)

    # Update password separately if provided
    if user.password:
        async with httpx.AsyncClient() as client:
            pr = await client.put(
                f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/reset-password",
                json={"type": "password", "value": user.password, "temporary": False},
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            )
        if pr.status_code not in (200, 204):
            raise HTTPException(status_code=pr.status_code, detail=pr.text)

    return {"message": "User updated successfully", "username": username}