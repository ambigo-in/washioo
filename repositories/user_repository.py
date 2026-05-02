from sqlalchemy.orm import joinedload
from models.user_role import UserRole
from models.user import User
from models.role import Role


def get_user_by_phone(db, phone):
    from models.user import User
    return db.query(User).filter(User.phone == phone).first()

def create_user(db, user_data):
    from models.user import User
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db, user_id):
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db):
    return (
        db.query(User)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
        .all()
    )

def get_users_by_role(db, role_name):
    return (
        db.query(User)
        .join(User.user_roles)
        .join(UserRole.role)
        .filter(Role.role_name == role_name.lower())
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
        .all()
    )

def update_user_details(db, user, update_data):
    if update_data.full_name is not None:
        user.full_name = update_data.full_name
    if update_data.email is not None:
        user.email = update_data.email
    if update_data.phone is not None:
        user.phone = update_data.phone

    db.commit()
    db.refresh(user)
    return user

def delete_user(db, user):
    db.delete(user)
    db.commit()
    return True

def get_user_with_roles(db, user_id):
    return (
        db.query(User)
        .options(
            joinedload(User.user_roles).joinedload(UserRole.role)
        )
        .filter(User.id == user_id)
        .first()
    )