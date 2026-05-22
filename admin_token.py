from fastapi import HTTPException
import httpx
from config import KEYCLOAK_URL


async def get_admin_token(ADMIN_USERNAME : str, ADMIN_PASSWORD : str, REALM : str) -> str:

    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    payload = {
        "client_id": "admin-cli",
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "grant_type": "password",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=payload)
 
    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to authenticate with Keycloak: {response.text}",
        )
 
    return response.json()["access_token"]

