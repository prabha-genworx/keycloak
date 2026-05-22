from fastapi import APIRouter, HTTPException
import httpx
from config import KEYCLOAK_URL
from admin_token import get_admin_token
from client.config import ADMIN_USERNAME, ADMIN_PASSWORD, REALM
from client.schema import ClientUpdateRequest

router = APIRouter()


async def _get_client_uuid(token: str, realm: str, client_id: str) -> str:
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients",
            params={"clientId": client_id},
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to fetch clients in realm '{realm}'.",
        )

    clients = response.json()

    if not clients:
        raise HTTPException(
            status_code=404,
            detail=f"Client '{client_id}' not found in realm '{realm}'.",
        )

    return clients[0]["id"]


@router.put("/{realm}/clients/{client_id}")
async def update_client(
    realm: str,
    client_id: str,
    client: ClientUpdateRequest
):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    uuid = await _get_client_uuid(token, realm, client_id)

    update_payload = {}

    # ── Map ONLY your schema fields ──
    if client.enabled is not None:
        update_payload["enabled"] = client.enabled

    if client.public_client is not None:
        update_payload["publicClient"] = client.public_client

    if client.redirect_uris is not None:
        update_payload["redirectUris"] = client.redirect_uris

    if not update_payload:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    async with httpx.AsyncClient() as http_client:
        response = await http_client.put(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients/{uuid}",
            json=update_payload,
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code not in (200, 204):
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to update client: {response.text}",
        )

    return {
        "message": f"Client '{client_id}' updated successfully",
        "realm": realm,
        "client_id": client_id,
        "updated_fields": list(update_payload.keys()),
    }