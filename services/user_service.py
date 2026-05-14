from datetime import datetime

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
from utils.datetime_utils import utc_isoformat


def get_user_profile(user: User):
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "phone": user.phone,
        "email": user.email,
        "is_verified": user.is_verified,
        "is_active": user.is_active,
        "terms_accepted": user.terms_accepted,
        "terms_accepted_at": utc_isoformat(user.terms_accepted_at) if user.terms_accepted_at else None,
        "average_rating": float(user.average_rating) if user.average_rating is not None else 0,
        "total_ratings": user.total_ratings or 0,
        "roles": [user_role.role.role_name for user_role in user.user_roles],
        "created_at": utc_isoformat(user.created_at)
    }


def get_user_details_service(db, user_id):
    user = get_user_by_id(db, user_id)
    if not user:
        raise Exception("User not found")
    return get_user_profile(user)


def get_all_users_service(db, limit=50, offset=0):
    users = get_all_users(db, limit, offset)
    return [get_user_profile(user) for user in users]


def update_user_details_service(db, user_id, payload):
    user = get_user_by_id(db, user_id)
    if not user:
        raise Exception("User not found")

    try:
        updated_user = update_user_details(db, user, payload)
    except IntegrityError:
        db.rollback()
        raise Exception("Phone or email already in use")

    return get_user_profile(updated_user)


def delete_user_service(db, user_id):
    user = get_user_by_id(db, user_id)
    if not user:
        raise Exception("User not found")
    delete_user(db, user)
    return True


def accept_terms_service(db, user: User):
    if not user.terms_accepted:
        user.terms_accepted = True
        user.terms_accepted_at = datetime.utcnow()
    elif user.terms_accepted_at is None:
        user.terms_accepted_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return get_user_profile(user)


def get_users_by_role_service(db, role_name, limit=50, offset=0):
    if not get_role_by_name(db, role_name):
        raise Exception("Role not found")

    users = get_users_by_role(db, role_name, limit, offset)
    return [get_user_profile(user) for user in users]

