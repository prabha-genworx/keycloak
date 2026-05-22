from http.client import HTTPException

from fastapi import APIRouter
import httpx

from admin_token import get_admin_token
from realm_roles.config import ADMIN_PASSWORD, ADMIN_USERNAME, REALM
from config import KEYCLOAK_URL


router = APIRouter()


@router.get("/realms/{realm_name}/roles/{role_name}")
async def get_realm_role(realm_name: str, role_name: str):
    """Get details of a specific realm role."""
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
 
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}/roles/{role_name}",
            headers={"Authorization": f"Bearer {token}"},
        )
 
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found in realm '{realm_name}'.")
 
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
 
    r = response.json()
    return {
        "id": r["id"],
        "name": r["name"],
        "description": r.get("description", ""),
    }