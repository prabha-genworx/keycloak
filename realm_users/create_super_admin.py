import httpx
from fastapi import APIRouter, HTTPException
from realm_users.config import REALM, REQUIRED_CLIENT_ROLES, ADMIN_PASSWORD, ADMIN_USERNAME
from config import KEYCLOAK_URL
from realm_users.schema import UserRequest
from  admin_token import get_admin_token

router = APIRouter()

async def create_user(client: httpx.AsyncClient, headers: dict, user: UserRequest) -> None:
    r = await client.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
        json={
            "username": user.username,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "enabled": user.enabled,
            "credentials": [{"type": "password", "value": user.password, "temporary": False}],
        },
        headers=headers,
    )
    if r.status_code not in (201, 409):
        raise HTTPException(status_code=r.status_code, detail=f"Create user failed: {r.text}")

async def get_user_id(client: httpx.AsyncClient, headers: dict, username: str) -> str:
    r = await client.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
        params={"username": username, "exact": "true"},
        headers=headers,
    )
    r.raise_for_status()
    users = r.json()
    if not users:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found after creation")
    return users[0]["id"]


async def get_mgmt_client_id(client: httpx.AsyncClient, headers: dict) -> str:
    r = await client.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/clients",
        params={"clientId": "realm-management"},
        headers=headers,
    )
    r.raise_for_status()
    clients = r.json()
    if not clients:
        raise HTTPException(status_code=404, detail="realm-management client not found")
    return clients[0]["id"]

async def resolve_roles(client: httpx.AsyncClient, headers: dict, mgmt_client_id: str) -> list[dict]:
    r = await client.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/clients/{mgmt_client_id}/roles",
        headers=headers,
    )
    r.raise_for_status()
    roles = [{"id": role["id"], "name": role["name"]} for role in r.json() if role["name"] in REQUIRED_CLIENT_ROLES]
    missing = set(REQUIRED_CLIENT_ROLES) - {role["name"] for role in roles}
    if missing:
        raise HTTPException(status_code=404, detail=f"Roles not found: {missing}")
    return roles

async def assign_roles(client: httpx.AsyncClient, headers: dict, user_id: str, mgmt_client_id: str, roles: list[dict]) -> None:
    r = await client.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/role-mappings/clients/{mgmt_client_id}",
        json=roles,
        headers=headers,
    )
    if r.status_code not in (200, 204):
        raise HTTPException(status_code=r.status_code, detail=f"Role assignment failed: {r.text}")


@router.post("/users/super_admin", status_code=201)
async def create_user_with_permissions(user: UserRequest):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        await create_user(client, headers, user)
        user_id = await get_user_id(client, headers, user.username)
        mgmt_client_id = await get_mgmt_client_id(client, headers)
        roles = await resolve_roles(client, headers, mgmt_client_id)
        await assign_roles(client, headers, user_id, mgmt_client_id, roles)

    return {"message": "User created and permissions assigned", "user_id": user_id, "roles_assigned": REQUIRED_CLIENT_ROLES}

