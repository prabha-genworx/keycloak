from http.client import HTTPException

from fastapi import APIRouter
import httpx

from config import KEYCLOAK_URL, REALM, ADMIN_PASSWORD, ADMIN_USERNAME
from admin_token import get_admin_token


router = APIRouter()


@router.get("/realms")
async def list_realms():

    token = await get_admin_token( ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
 
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{KEYCLOAK_URL}/admin/realms",
            headers={"Authorization": f"Bearer {token}"},
        )
 
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
 
    realms = [{"realm": r["realm"], "displayName": r.get("displayName", ""), "enabled": r["enabled"]}
              for r in response.json()]
    return {"realms": realms, "count": len(realms)}