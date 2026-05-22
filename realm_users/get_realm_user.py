from typing import Optional
import httpx
from fastapi import APIRouter, HTTPException, Query
from realm_users.config import REALM,ADMIN_PASSWORD, ADMIN_USERNAME
from config import KEYCLOAK_URL
from admin_token import get_admin_token

router = APIRouter()


@router.get("/users")
async def list_users(
    search: Optional[str] = Query(None, description="Filter by username or email"),
    first: int = Query(0),
    max: int = Query(50),
):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    params = {"first": first, "max": max}
    if search:
        params["search"] = search

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )

    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    users = [
        {
            "id": u["id"],
            "username": u["username"],
            "email": u.get("email", ""),
            "first_name": u.get("firstName", ""),
            "last_name": u.get("lastName", ""),
            "enabled": u.get("enabled"),
        }
        for u in r.json()
    ]

    return {"total": len(users), "users": users}


@router.get("/users/{username}")
async def get_user(username: str):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
            params={"username": username, "exact": True},
            headers={"Authorization": f"Bearer {token}"},
        )

    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    users = r.json()
    if not users:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found.")

    u = users[0]
    return {
        "id": u["id"],
        "username": u["username"],
        "email": u.get("email", ""),
        "first_name": u.get("firstName", ""),
        "last_name": u.get("lastName", ""),
        "enabled": u.get("enabled"),
    }


