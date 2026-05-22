from fastapi import APIRouter, HTTPException
import httpx

from config import KEYCLOAK_URL
from client_roles.config import ADMIN_USERNAME, ADMIN_PASSWORD, REALM
from admin_token import get_admin_token
from client_roles.schema import ClientRoleRequest

router = APIRouter()


@router.post("/{realm}/clients/{client_id}/roles", status_code=201)
async def create_client_role(realm: str, client_id: str, role: ClientRoleRequest):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    # Resolve client UUID
    async with httpx.AsyncClient() as http_client:
        res = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients",
            params={"clientId": client_id},
            headers={"Authorization": f"Bearer {token}"},
        )
    clients = res.json()
    if not clients:
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found.")
    uuid = clients[0]["id"]

    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients/{uuid}/roles",
            json={"name": role.name, "description": role.description or ""},
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code == 409:
        raise HTTPException(status_code=409, detail=f"Role '{role.name}' already exists.")

    if response.status_code not in (201, 204):
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return {
        "message": f"Role '{role.name}' created successfully.",
        "client_id": client_id,
        "role": role.name,
        "realm": realm,
    }