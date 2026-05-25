import httpx
from fastapi import APIRouter, HTTPException
from realm_users.config import ADMIN_USERNAME,ADMIN_PASSWORD, REALM
from config import KEYCLOAK_URL
from admin_token import get_admin_token

router = APIRouter()


@router.delete("/users/{username}")
async def delete_user(username: str):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    # Resolve username → user_id
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
            params={"username": username, "exact": True},
            headers={"Authorization": f"Bearer {token}"},
        )
    users = res.json()
    if not users:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
    user_id = users[0]["id"]

    async with httpx.AsyncClient() as client:
        r = await client.delete(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    if r.status_code not in (200, 204):
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return {"message": "User deleted successfully", "username": username}



