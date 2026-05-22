import uuid
from fastapi import APIRouter, HTTPException
import httpx

from config import KEYCLOAK_URL
from admin_token import get_admin_token
from organization.config import ADMIN_PASSWORD, ADMIN_USERNAME, REALM
from organization.schema import OrganizationRequest

router = APIRouter()


@router.post("/{realm}/organizations", status_code=201)
async def create_organization(realm: str, org: OrganizationRequest):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    tenant_id = str(uuid.uuid4())

    payload = {
        "name": org.name,
        "alias": org.name,
        "displayName": org.display_name or org.name,
        "enabled": org.enabled,
        "attributes": {
            "tenant_id": [tenant_id]
        },
    }

    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/organizations",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code == 409:
        raise HTTPException(status_code=409, detail=f"Organization '{org.name}' already exists.")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Realm '{realm}' not found.")

    if response.status_code not in (201, 204):
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return {
        "message": f"Organization '{org.name}' created successfully.",
        "organization": org.name,
        "tenant_id": tenant_id,
        "realm": realm,
    }