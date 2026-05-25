import httpx
from fastapi import APIRouter, HTTPException

from realm_users.config import (
    TARGET_REALM,
    MASTER_REALM,
    REQUIRED_CLIENT_ROLES,
    ADMIN_PASSWORD,
    ADMIN_USERNAME
)

from config import KEYCLOAK_URL
from realm_users.schema import UserRequest
from admin_token import get_admin_token

router = APIRouter()


async def create_realm(
    client: httpx.AsyncClient,
    headers: dict,
    realm_name: str
) -> None:

    r = await client.post(
        f"{KEYCLOAK_URL}/admin/realms",
        json={
            "realm": realm_name,
            "enabled": True
        },
        headers=headers,
    )

    if r.status_code not in (201, 409):
        raise HTTPException(
            status_code=r.status_code,
            detail=f"Realm creation failed: {r.text}"
        )


async def create_user(
    client: httpx.AsyncClient,
    headers: dict,
    user: UserRequest,
    realm: str
) -> None:

    r = await client.post(
        f"{KEYCLOAK_URL}/admin/realms/{realm}/users",
        json={
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
        },
        headers=headers,
    )

    if r.status_code == 409:
        raise HTTPException(
            status_code=409,
            detail=f"User '{user.username}' already exists in realm '{realm}'"
        )

    if r.status_code != 201:
        raise HTTPException(
            status_code=r.status_code,
            detail=f"Create user failed: {r.text}"
        )

async def get_user_id(
    client: httpx.AsyncClient,
    headers: dict,
    username: str,
    realm: str
) -> str:

    r = await client.get(
        f"{KEYCLOAK_URL}/admin/realms/{realm}/users",
        params={
            "username": username,
            "exact": "true"
        },
        headers=headers,
    )

    r.raise_for_status()

    users = r.json()

    if not users:
        raise HTTPException(
            status_code=404,
            detail=f"User '{username}' not found"
        )

    return users[0]["id"]


async def get_mgmt_client_id(
    client: httpx.AsyncClient,
    headers: dict,
    realm: str
) -> str:

    r = await client.get(
        f"{KEYCLOAK_URL}/admin/realms/{realm}/clients",
        params={"clientId": "realm-management"},
        headers=headers,
    )

    r.raise_for_status()

    clients = r.json()

    if not clients:
        raise HTTPException(
            status_code=404,
            detail=f"realm-management client not found in realm '{realm}'"
        )

    return clients[0]["id"]


async def resolve_roles(
    client: httpx.AsyncClient,
    headers: dict,
    realm: str,
    mgmt_client_id: str
) -> list[dict]:

    roles = []

    for role_name in REQUIRED_CLIENT_ROLES:

        r = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients/{mgmt_client_id}/roles/{role_name}",
            headers=headers,
        )

        if r.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail=f"Role '{role_name}' not found"
            )

        role = r.json()

        roles.append({
            "id": role["id"],
            "name": role["name"]
        })

    return roles


async def assign_roles(
    client: httpx.AsyncClient,
    headers: dict,
    realm: str,
    user_id: str,
    mgmt_client_id: str,
    roles: list[dict]
) -> None:

    r = await client.post(
        f"{KEYCLOAK_URL}/admin/realms/{realm}/users/{user_id}/role-mappings/clients/{mgmt_client_id}",
        json=roles,
        headers=headers,
    )

    if r.status_code not in (200, 204):
        raise HTTPException(
            status_code=r.status_code,
            detail=f"Role assignment failed: {r.text}"
        )


@router.post("/users/super_admin", status_code=201)
async def create_user_with_permissions(user: UserRequest):

    # Login using master realm admin
    token = await get_admin_token(
        ADMIN_USERNAME,
        ADMIN_PASSWORD,
        MASTER_REALM
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    realm = TARGET_REALM

    async with httpx.AsyncClient() as client:

        # Create realm if not exists
        await create_realm(
            client,
            headers,
            realm
        )

        # Create super admin user
        await create_user(
            client,
            headers,
            user,
            realm
        )

        # Get user id
        user_id = await get_user_id(
            client,
            headers,
            user.username,
            realm
        )

        # Get realm-management client id
        mgmt_client_id = await get_mgmt_client_id(
            client,
            headers,
            realm
        )

        # Get realm-admin role
        roles = await resolve_roles(
            client,
            headers,
            realm,
            mgmt_client_id
        )

        # Assign role
        await assign_roles(
            client,
            headers,
            realm,
            user_id,
            mgmt_client_id,
            roles
        )

    return {
        "message": "Tenant super admin created successfully",
        "realm": realm,
        "user_id": user_id,
        "roles_assigned": REQUIRED_CLIENT_ROLES
    }