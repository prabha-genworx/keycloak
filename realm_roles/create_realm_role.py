from http.client import HTTPException

from fastapi import APIRouter
import httpx

from admin_token import get_admin_token
from realm_roles.config import ADMIN_PASSWORD, ADMIN_USERNAME, REALM
from config import KEYCLOAK_URL
from realm_roles.schema import RoleRequest

router = APIRouter()


@router.post("/realms/{realm_name}/roles", status_code=201)
async def create_realm_role(realm_name: str, role: RoleRequest):

    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
 
    role_payload = {
        "name": role.name,
        "description": role.description or "",
        "clientRole": False,
    }
 
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}/roles",
            json=role_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
 
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Realm '{realm_name}' not found.")

    if response.status_code == 409:
        raise HTTPException(status_code=409, detail=f"Role '{role.name}' already exists in realm '{realm_name}'.")

    if response.status_code not in (201, 204):
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to create role: {response.text}",
        )

    return {
        "message": f"Role '{role.name}' created successfully in realm '{realm_name}'.",
        "realm": realm_name,
        "role": role.name,
    }