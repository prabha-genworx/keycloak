from typing import Optional
from fastapi import APIRouter, HTTPException, Query
import httpx
from config import KEYCLOAK_URL
from admin_token import get_admin_token
from client.config import ADMIN_USERNAME, ADMIN_PASSWORD, REALM
router = APIRouter()
 

@router.get("/{realm}/clients")
async def list_clients(
    realm: str,
    client_id: Optional[str] = Query(None),
    first: int = Query(0),
    max: int = Query(50),
):
    token = await get_admin_token(ADMIN_USERNAME, ADMIN_PASSWORD, REALM)

    params = {
        "first": first,
        "max": max,
    }

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/clients",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )

    clients = response.json()

    # Optional filtering in your backend
    if client_id:
        clients = [
            c for c in clients
            if client_id.lower() in c.get("clientId", "").lower()
        ]

    return {
        "realm": realm,
        "total": len(clients),
        "clients": [
            {
                "uuid": c.get("id"),
                "client_id": c.get("clientId"),
                "name": c.get("name"),
                "enabled": c.get("enabled"),
                "public_client": c.get("publicClient"),
                "protocol": c.get("protocol"),
            }
            for c in clients
        ],
    }