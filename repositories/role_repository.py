from models.role import Role
from models.user_role import UserRole
from repositories.user_repository import get_user_with_roles


def get_role_by_name(db, role_name: str):
    return db.query(Role).filter(Role.role_name == role_name.lower()).first()


def assign_role_to_user(db, user_id, role_id):
    user_role = UserRole(
        user_id=user_id,
        role_id=role_id
    )
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    return user_role

def get_user_roles(db, user_id):
    user = get_user_with_roles(db, user_id)
    if not user:
        return []

    return [ur.role.role_name for ur in user.user_roles]

def user_has_role(db, user_id, role_name: str):
    """Check if user already has a specific role"""
    user = get_user_with_roles(db, user_id)
    if not user:
        return False
    
    return any(ur.role.role_name == role_name.lower() for ur in user.user_roles)