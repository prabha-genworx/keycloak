from fastapi import APIRouter, HTTPException
import httpx

from admin_token import get_admin_token
from realm_roles.config import ADMIN_PASSWORD, ADMIN_USERNAME, REALM
from config import KEYCLOAK_URL


router = APIRouter()

@router.delete("/realms/{realm_name}/roles/{role_name}", status_code=204)
async def delete_realm_role(realm_name: str, role_name: str):

    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
 
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}/roles/{role_name}",
            headers={"Authorization": f"Bearer {token}"},
        )
 
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found in realm '{realm_name}'.")
 
    if response.status_code not in (200, 204):
        raise HTTPException(status_code=response.status_code, detail=response.text)