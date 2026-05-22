from fastapi import APIRouter, HTTPException
import httpx

from admin_token import get_admin_token
from realm_roles.config import ADMIN_PASSWORD, ADMIN_USERNAME, REALM
from config import KEYCLOAK_URL
from realm_roles.schema import RoleRequest



router = APIRouter()

@router.put("/realms/{realm_name}/roles/{role_name}")
async def update_realm_role(realm_name: str, role_name: str, role: RoleRequest):

    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
 
    role_payload = {
        "name": role.name,
        "description": role.description or "",
        "clientRole": False,
    }
 
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}/roles/{role_name}",
            json=role_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
 
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found in realm '{realm_name}'.")
 
    if response.status_code not in (200, 204):
        raise HTTPException(status_code=response.status_code, detail=response.text)
 
    return {"message": f"Role '{role_name}' updated successfully.", "realm": realm_name}