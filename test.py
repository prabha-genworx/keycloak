import uuid
import httpx

from fastapi import APIRouter, HTTPException

from config import KEYCLOAK_URL
from admin_token import get_admin_token
from organization.config import (
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    REALM,
)
from organization.schema import OrganizationRequest


router = APIRouter()


@router.post("/{realm}/organizations", status_code=201)
async def create_organization(
    realm: str,
    org: OrganizationRequest
):
    # Get admin token from master realm
    token = await get_admin_token(
        ADMIN_USERNAME,
        ADMIN_PASSWORD,
        REALM
    )

    tenant_id = str(uuid.uuid4())

    payload = {
        "name": org.name,
        "alias": org.name,
        "enabled": org.enabled,
        "attributes": {
            "tenant_id": [tenant_id]
        }
    }

    async with httpx.AsyncClient() as http_client:

        # Debug: Check realm exists
        realm_check = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        print("Realm Check Status:", realm_check.status_code)
        print("Realm Check Response:", realm_check.text)

        if realm_check.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Realm '{realm}' not found."
            )

        # Create organization
        response = await http_client.post(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/organizations",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
        )

        print("Organization Status:", response.status_code)
        print("Organization Response:", response.text)

    # Error handling
    if response.status_code == 409:
        raise HTTPException(
            status_code=409,
            detail=f"Organization '{org.name}' already exists."
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=response.text
        )

    if response.status_code not in (201, 204):
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return {
        "message": f"Organization '{org.name}' created successfully.",
        "organization": org.name,
        "tenant_id": tenant_id,
        "realm": realm,
    }