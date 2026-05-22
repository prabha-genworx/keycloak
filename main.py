from fastapi import FastAPI
from realm.create_realm import router as create_realm_router
from realm.list_realms import router as list_realms_router
from realm.delete_realm import router as delete_realm_router
from realm_roles.create_realm_role import router as create_realm_role_router
from realm_roles.update_realm_role import router as update_realm_role_router
from realm_roles.list_realm_roles import router as list_realm_roles_router
from realm_roles.get_realm_role import router as get_realm_role_router
from realm_roles.delete_realm_role import router as delete_realm_role_router
from realm_users.create_realm_user import router as create_realm_user_router
from realm_users.create_super_admin import router as create_super_admin_router
from realm_users.update_realm_user import router as update_realm_user_router
from realm_users.delete_realm_user import router as delete_realm_user_router
from realm_users.get_realm_user import router as get_realm_user_router
from client.create_client import router as create_client_router
from client.list_clients import router as list_clients_router
from client.delete_client import router as delete_client_router
from client.update_client import router as update_client_router
from client_roles.get_client_role import router as get_client_role_router
from client_roles.delete_client_role import router as delete_client_role_router
from client_roles.create_client_role import router as create_client_role_router
from client_roles.update_client_role import router as update_client_role_router

app = FastAPI(title="Keycloak Realm Manager")


app.include_router(create_realm_router,prefix="/keycloak",  tags=["realms"])
app.include_router(list_realms_router, prefix="/keycloak", tags=["realms"])
app.include_router(delete_realm_router, prefix="/keycloak", tags=["realms"])
app.include_router(create_realm_role_router, prefix="/keycloak", tags=["realm-roles"])
app.include_router(list_realm_roles_router, prefix="/keycloak", tags=["realm-roles"])
app.include_router(get_realm_role_router, prefix="/keycloak", tags=["realm-roles"])
app.include_router(update_realm_role_router, prefix="/keycloak", tags=["realm-roles"])
app.include_router(delete_realm_role_router, prefix="/keycloak", tags=["realm-roles"])
app.include_router(create_realm_user_router, prefix="/keycloak", tags=["realm-users"])
app.include_router(create_super_admin_router, prefix="/keycloak", tags=["realm-users"])
app.include_router(update_realm_user_router, prefix="/keycloak", tags=["realm-users"])
app.include_router(delete_realm_user_router, prefix="/keycloak", tags=["realm-users"])
app.include_router(get_realm_user_router, prefix="/keycloak", tags=["realm-users"])
app.include_router(create_client_router, prefix="/keycloak", tags=["clients"])
app.include_router(list_clients_router, prefix="/keycloak", tags=["clients"])
app.include_router(delete_client_router, prefix="/keycloak", tags=["clients"])
app.include_router(update_client_router, prefix="/keycloak", tags=["clients"])
app.include_router(get_client_role_router, prefix="/keycloak", tags=["client-roles"])
app.include_router(create_client_role_router, prefix="/keycloak", tags=["client-roles"])
app.include_router(update_client_role_router, prefix="/keycloak", tags=["client-roles"])
app.include_router(delete_client_role_router, prefix="/keycloak", tags=["client-roles"])
