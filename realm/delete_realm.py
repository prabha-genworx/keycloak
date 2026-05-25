from fastapi import APIRouter, HTTPException
import httpx

from config import KEYCLOAK_URL,REALM, ADMIN_PASSWORD, ADMIN_USERNAME
from admin_token import get_admin_token


router = APIRouter()

@router.delete("/realms/{realm_name}", status_code=200)
async def delete_realm(realm_name: str):

    if realm_name == "master":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the 'master' realm."
        )

    token = await get_admin_token(
        ADMIN_USERNAME,
        ADMIN_PASSWORD,
        REALM
    )

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=f"Realm '{realm_name}' not found."
        )

    if response.status_code not in (200, 204):
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return {
        "message": f"Realm '{realm_name}' deleted successfully"
    }