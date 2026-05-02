from sqlalchemy.exc import IntegrityError
from models.user import User
from repositories.user_repository import (
    get_user_by_id,
    get_all_users,
    get_users_by_role,
    update_user_details,
    delete_user,
)
from repositories.role_repository import get_role_by_name


def get_user_profile(user: User):
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "phone": user.phone,
        "email": user.email,
        "is_verified": user.is_verified,
        "is_active": user.is_active,
        "roles": [user_role.role.role_name for user_role in user.user_roles],
        "created_at": user.created_at
    }


def get_user_details_service(db, user_id):
    user = get_user_by_id(db, user_id)
    if not user:
        raise Exception("User not found")
    return get_user_profile(user)


def get_all_users_service(db):
    users = get_all_users(db)
    return [get_user_profile(user) for user in users]


def update_user_details_service(db, user_id, payload):
    user = get_user_by_id(db, user_id)
    if not user:
        raise Exception("User not found")

    try:
        updated_user = update_user_details(db, user, payload)
    except IntegrityError:
        raise Exception("Phone or email already in use")

    return get_user_profile(updated_user)


def delete_user_service(db, user_id):
    user = get_user_by_id(db, user_id)
    if not user:
        raise Exception("User not found")
    delete_user(db, user)
    return True


def get_users_by_role_service(db, role_name):
    if not get_role_by_name(db, role_name):
        raise Exception("Role not found")

    users = get_users_by_role(db, role_name)
    return [get_user_profile(user) for user in users]

