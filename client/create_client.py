from fastapi import APIRouter, HTTPException
import httpx
from config import KEYCLOAK_URL
from admin_token import get_admin_token
from client.config import ADMIN_USERNAME, ADMIN_PASSWORD, REALM
from client.schema import ClientRequest

router = APIRouter()


@router.post("/{realm}/clients", status_code=201)
async def create_client(realm: str, client: ClientRequest):
   
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    client_payload = {
        "clientId": client.client_id,
        "enabled": client.enabled,
        "publicClient": client.public_client
    }

    if not client.public_client and client.secret:
        client_payload["secret"] = client.secret

    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients",
            json=client_payload,
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code == 409:
        raise HTTPException(
            status_code=409,
            detail=f"Client '{client.client_id}' already exists in realm '{realm}'.",
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=f"Realm '{realm}' not found.",
        )

    if response.status_code not in (201, 204):
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to create client: {response.text}",
        )

    # Fetch the created client to return its UUID
    async with httpx.AsyncClient() as http_client:
        search_response = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients",
            params={"clientId": client.client_id},
            headers={"Authorization": f"Bearer {token}"},
        )

    client_data = search_response.json()
    client_uuid = client_data[0]["id"] if client_data else None

    return {
        "message": f"Client '{client.client_id}' created successfully in realm '{realm}'.",
        "client_id": client.client_id,
        "uuid": client_uuid,
        "realm": realm,
    }