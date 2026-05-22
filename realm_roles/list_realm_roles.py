from fastapi import APIRouter, HTTPException
import httpx

from admin_token import get_admin_token
from realm_roles.config import ADMIN_PASSWORD, ADMIN_USERNAME, REALM
from config import KEYCLOAK_URL


router = APIRouter()


@router.get("/realms/{realm_name}/roles")
async def list_realm_roles(realm_name: str):

    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
 
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}/roles",
            headers={"Authorization": f"Bearer {token}"},
        )
 
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Realm '{realm_name}' not found.")
 
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
 
    roles = [
        {
            "id": r["id"],
            "name": r["name"],
            "description": r.get("description", ""),
        }
        for r in response.json()
    ]
    return {"realm": realm_name, "roles": roles, "count": len(roles)}
 