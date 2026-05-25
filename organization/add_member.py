import httpx
from fastapi import APIRouter, HTTPException

from config import KEYCLOAK_URL
from organization.config import (
    REALM,
    ADMIN_USERNAME,
    ADMIN_PASSWORD
)
from admin_token import get_admin_token


router = APIRouter()


async def _get_org_id(
    token: str,
    realm: str,
    org_name: str
) -> str:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/organizations",
            params={"search": org_name},
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

    orgs = res.json()

    if not orgs:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Organization "
                f"'{org_name}' not found."
            )
        )

    return orgs[0]["id"]


async def _get_user_id(
    token: str,
    realm: str,
    username: str
) -> str:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/users",
            params={
                "username": username,
                "exact": True
            },
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

    users = res.json()

    if not users:
        raise HTTPException(
            status_code=404,
            detail=f"User '{username}' not found."
        )

    return users[0]["id"]


@router.post(
    "/{realm}/organizations/{org_name}/add-user/{username}",
    status_code=200
)
async def add_user_to_organization(
    realm: str,
    org_name: str,
    username: str
):
    token = await get_admin_token(
        ADMIN_USERNAME,
        ADMIN_PASSWORD,
        REALM
    )

    org_id = await _get_org_id(
        token,
        realm,
        org_name
    )

    user_id = await _get_user_id(
        token,
        realm,
        username
    )

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{KEYCLOAK_URL}/admin/realms/{realm}/organizations/{org_id}/members",
            json=user_id,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
        )

    if r.status_code == 409:
        raise HTTPException(
            status_code=409,
            detail=(
                f"User '{username}' "
                f"is already a member "
                f"of '{org_name}'."
            )
        )

    if r.status_code not in (200, 201, 204):
        raise HTTPException(
            status_code=r.status_code,
            detail=r.text
        )

    return {
        "message": (
            f"User '{username}' added "
            f"to organization "
            f"'{org_name}' successfully."
        ),
        "username": username,
        "organization": org_name,
        "realm": realm,
    }