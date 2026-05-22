from typing import Optional
from fastapi import APIRouter, HTTPException, Query
import httpx

from config import KEYCLOAK_URL
from admin_token import get_admin_token
from organization.config import REALM, ADMIN_USERNAME, ADMIN_PASSWORD

router = APIRouter()


@router.get("/{realm}/organizations", status_code=200)
async def list_organizations(
    realm: str,
    search: Optional[str] = Query(None, description="Filter by name"),
    first: int = Query(0),
    max: int = Query(50),
):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    params = {"first": first, "max": max}
    if search:
        params["search"] = search

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/organizations",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Realm '{realm}' not found.")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    orgs = [
        {
            "id": o["id"],
            "name": o["name"],
            "display_name": o.get("displayName", ""),
            "enabled": o.get("enabled"),
        }
        for o in response.json()
    ]

    return {"realm": realm, "total": len(orgs), "organizations": orgs}


@router.get("/{realm}/organizations/{org_name}", status_code=200)
async def get_organization(realm: str, org_name: str):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/organizations",
            params={"search": org_name},
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    orgs = response.json()
    if not orgs:
        raise HTTPException(status_code=404, detail=f"Organization '{org_name}' not found.")

    o = orgs[0]
    return {
        "id": o["id"],
        "name": o["name"],
        "display_name": o.get("displayName", ""),
        "enabled": o.get("enabled"),
        "realm": realm,
    }