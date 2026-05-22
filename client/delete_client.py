from fastapi import APIRouter, HTTPException
import httpx
from config import KEYCLOAK_URL
from client.config import ADMIN_USERNAME, ADMIN_PASSWORD, REALM
from admin_token import get_admin_token

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



@router.delete("/{realm}/clients/{client_id}")
async def delete_client(realm: str, client_id: str):
   
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    # Resolve clientId → UUID
    uuid = await _get_client_uuid(token, realm, client_id)

    # Call Keycloak delete API
    async with httpx.AsyncClient() as http_client:
        response = await http_client.delete(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients/{uuid}",
            headers={"Authorization": f"Bearer {token}"},
        )

    # Handle errors
    if response.status_code not in (204, 200):
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to delete client: {response.text}",
        )

    # Response
    return {
        "message": f"Client '{client_id}' deleted successfully",
        "realm": realm,
        "client_id": client_id,
        "uuid": uuid,
    }
