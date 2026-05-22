from fastapi import APIRouter, HTTPException
import httpx

from config import KEYCLOAK_URL
from admin_token import get_admin_token
from client_roles.config import ADMIN_USERNAME, ADMIN_PASSWORD, REALM
from client_roles.schema import ClientRoleUpdateRequest

router = APIRouter()


@router.put("/{realm}/clients/{client_id}/roles/{role_name}", status_code=200)
async def update_client_role(realm: str, client_id: str, role_name: str, role: ClientRoleUpdateRequest):
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

    payload = {"name": role.name or role_name}
    if role.description is not None:
        payload["description"] = role.description

    async with httpx.AsyncClient() as http_client:
        response = await http_client.put(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients/{uuid}/roles/{role_name}",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found.")

    if response.status_code not in (200, 204):
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return {
        "message": f"Role '{role_name}' updated successfully.",
        "client_id": client_id,
        "role": role.name or role_name,
        "realm": realm,
    }