from fastapi import APIRouter, HTTPException
import httpx

from config import KEYCLOAK_URL
from admin_token import get_admin_token
from client_roles.config import ADMIN_USERNAME, ADMIN_PASSWORD, REALM
router = APIRouter()


async def _resolve_uuid(token: str, realm: str, client_id: str) -> str:
    async with httpx.AsyncClient() as http_client:
        res = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients",
            params={"clientId": client_id},
            headers={"Authorization": f"Bearer {token}"},
        )
    clients = res.json()
    if not clients:
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found.")
    return clients[0]["id"]


@router.get("/{realm}/clients/{client_id}/roles", status_code=200)
async def list_client_roles(realm: str, client_id: str):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
    uuid = await _resolve_uuid(token, realm, client_id)

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients/{uuid}/roles",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    roles = [
        {"name": r["name"], "description": r.get("description", "")}
        for r in response.json()
    ]

    return {"realm": realm, "client_id": client_id, "total": len(roles), "roles": roles}


@router.get("/{realm}/clients/{client_id}/roles/{role_name}", status_code=200)
async def get_client_role(realm: str, client_id: str, role_name: str):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)
    uuid = await _resolve_uuid(token, realm, client_id)

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients/{uuid}/roles/{role_name}",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found.")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    r = response.json()
    return {"name": r["name"], "description": r.get("description", ""), "realm": realm, "client_id": client_id}