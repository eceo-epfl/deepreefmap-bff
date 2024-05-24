from typing import Any
from fastapi import Depends, APIRouter, Query, Response
from app.config import config
from uuid import UUID
from app.models.user import User
from app.auth import require_admin
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
from pydantic import BaseModel
from enum import Enum
import json


router = APIRouter()


class UserRoles(str, Enum):
    admin = "admin"
    user = "user"


class UserUpdate(BaseModel):
    role: UserRoles


def get_keycloak_admin():
    keycloak_connection = KeycloakOpenIDConnection(
        server_url=config.KEYCLOAK_URL,
        realm_name=config.KEYCLOAK_REALM,
        client_id=config.KEYCLOAK_BFF_ID,
        client_secret_key=config.KEYCLOAK_BFF_SECRET,
        verify=True,
    )
    return KeycloakAdmin(connection=keycloak_connection)


class KeycloakUser(BaseModel):
    username: str | None
    firstName: str | None
    lastName: str | None
    email: str | None
    id: str | None
    admin: bool | None
    loginMethod: str | None
    roles: list[dict[str, str]] | None = []


def get_user(
    user_id: str,
    keycloak_admin: KeycloakAdmin,
) -> KeycloakUser:

    user = keycloak_admin.get_user(user_id)

    admin_status = keycloak_admin.get_realm_role_members("admin")
    admin = False
    for admin_user in admin_status:
        if admin_user["username"] == user["username"]:
            admin = True
            break

    # Get all roles foe the user
    roles = keycloak_admin.get_realm_roles_of_user(user_id=user_id)

    # Only include valid roles
    roles = [role for role in roles if role["name"] in config.VALID_ROLES]

    return KeycloakUser(
        email=user.get("email"),
        username=user.get("username"),
        id=user.get("id"),
        firstName=user.get("firstName"),
        lastName=user.get("lastName"),
        admin=admin,
        loginMethod=(
            user.get("attributes", {}).get("login-method", ["EPFL"])[0].upper()
        ),
        roles=[{"name": role["name"]} for role in roles] if roles else None,
    )


@router.get("/{user_id}", response_model=KeycloakUser)
async def get_one_user(
    user_id: str,
    keycloak_admin: KeycloakAdmin = Depends(get_keycloak_admin),
    user: User = Depends(require_admin),
) -> KeycloakUser:
    """Get a user by id"""

    return get_user(user_id, keycloak_admin)


@router.get("", response_model=list[KeycloakUser])
async def get_users(
    response: Response,
    user: User = Depends(require_admin),
    keycloak: KeycloakAdmin = Depends(get_keycloak_admin),
    *,
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
) -> list[KeycloakUser]:
    """Get a list of users

    This endpoint is used to get a list of users from Keycloak. It is used
    to populate the list of users in the admin UI.

    Filtering by username is only supported when the admin filter is set to
    False.
    """

    sort = json.loads(sort) if sort else []
    range = json.loads(range) if range else []
    filter = json.loads(filter) if filter else {}

    # Get admin role users
    admin_users = keycloak.get_realm_role_members("admin")
    print(admin_users)
    for admin_user in admin_users:
        admin_user["admin"] = True

    query = {"first": range[0], "max": range[1] - range[0] + 1}

    # Manage the filter if there is one

    # If admin is False, then handle general users in Keycloak
    # Username filtering is only supported when admin is False, only
    # because we assume the list for admins is much smaller and we can
    # avoid querying the entire user list (all of EPFL LDAP in this case)
    # if "admin" in filter and filter["admin"] is False:
    if "username" in filter:
        query["username"] = filter["username"]

    users = keycloak.get_users(query=query)

    for admin_user in users:
        if admin_user["username"] in [u["username"] for u in admin_users]:
            admin_user["admin"] = True
        else:
            admin_user["admin"] = False

    if "admin" in filter and filter["admin"] is True:
        # Otherwise, return only the admin users
        users = admin_users

    if len(range) == 2:
        start, end = range
    else:
        start, end = [0, len(users) + 1]

    response.headers["Content-Range"] = f"users {start}-{end}/{len(users)}"

    user_objs = [
        KeycloakUser(
            email=user.get("email"),
            username=user.get("username"),
            id=user.get("id"),
            firstName=user.get("firstName"),
            lastName=user.get("lastName"),
            admin=user.get("admin"),
            loginMethod=user.get("attributes", {})
            .get("login-method", ["EPFL"])[0]
            .upper(),
        )
        for user in users[start : end + 1]
    ]

    return user_objs


@router.put("/{user_id}")
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    keycloak_admin: KeycloakAdmin = Depends(get_keycloak_admin),
    user: User = Depends(require_admin),
) -> Any:
    """Updates the role of the user"""

    # Everything here works in list, although we only have one role, let's
    # keep it that way for future-proofing
    roles_to_assign = [user_update.role.value]

    # Get the role objects from keycloak
    realm_roles = keycloak_admin.get_realm_roles(["admin", "user"])
    roles = [role for role in realm_roles if role["name"] in roles_to_assign]
    current_userroles = keycloak_admin.get_realm_roles_of_user(user_id=user_id)

    roles_to_add = []
    roles_to_delete = []

    for role in roles:
        for userrole in current_userroles:
            if role["id"] == userrole["id"]:
                break
        else:
            roles_to_add.append(role)

    for userrole in current_userroles:
        for role in roles:
            if role["id"] == userrole["id"]:
                break
        else:
            roles_to_delete.append(userrole)

    keycloak_admin.assign_realm_roles(
        user_id=user_id,
        roles=roles_to_add,
    )
    keycloak_admin.delete_realm_roles_of_user(
        user_id=user_id,
        roles=roles_to_delete,
    )
    return get_user(user_id, keycloak_admin)
