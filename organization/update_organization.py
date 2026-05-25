from fastapi import APIRouter, HTTPException
import httpx

from config import KEYCLOAK_URL
from admin_token import get_admin_token
from organization.config import REALM, ADMIN_USERNAME, ADMIN_PASSWORD
from organization.schema import OrganizationUpdateRequest

router = APIRouter()


async def _get_org_id(token: str, realm: str, org_name: str) -> str:
    async with httpx.AsyncClient() as http_client:
        res = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/organizations",
            params={"search": org_name},
            headers={"Authorization": f"Bearer {token}"},
        )
    orgs = res.json()
    if not orgs:
        raise HTTPException(status_code=404, detail=f"Organization '{org_name}' not found.")
    return orgs[0]["id"]


@router.put("/{realm}/organizations/{org_name}", status_code=200)
async def update_organization(realm: str, org_name: str, org: OrganizationUpdateRequest):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
    org_id = await _get_org_id(token, realm, org_name)

    payload = {"name": org_name}
    if org.enabled is not None:
        payload["enabled"] = org.enabled

    async with httpx.AsyncClient() as http_client:
        response = await http_client.put(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/organizations/{org_id}",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code not in (200, 204):
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return {
        "message": f"Organization '{org_name}' updated successfully.",
        "organization": org_name,
        "realm": realm,
    }