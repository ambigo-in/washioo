from sqlalchemy.orm import joinedload
from models.user_role import UserRole
from models.user import User


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

def get_user_with_roles(db, user_id):
    return (
        db.query(User)
        .options(
            joinedload(User.user_roles).joinedload(UserRole.role)
        )
        .filter(User.id == user_id)
        .first()
    )