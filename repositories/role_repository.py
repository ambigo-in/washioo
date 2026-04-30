from models.role import Role
from models.user_role import UserRole


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