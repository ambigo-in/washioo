from sqlalchemy.orm import joinedload
from models.cleaner_profile import CleanerProfile
from models.user import User
from models.user_role import UserRole


def create_cleaner_profile(db, cleaner_data):
    cleaner = CleanerProfile(**cleaner_data)
    db.add(cleaner)
    db.commit()
    db.refresh(cleaner)
    return cleaner


def get_cleaner_profile_by_id(db, cleaner_id):
    return (
        db.query(CleanerProfile)
        .options(joinedload(CleanerProfile.user))
        .filter(CleanerProfile.id == cleaner_id)
        .first()
    )


def get_cleaner_profile_by_user_id(db, user_id):
    return (
        db.query(CleanerProfile)
        .options(joinedload(CleanerProfile.user))
        .filter(CleanerProfile.user_id == user_id)
        .first()
    )


def get_all_cleaner_profiles(db, approval_status=None, availability_status=None, limit=50, offset=0):
    query = db.query(CleanerProfile).options(joinedload(CleanerProfile.user))

    if approval_status:
        query = query.filter(CleanerProfile.approval_status == approval_status)
    if availability_status:
        query = query.filter(CleanerProfile.availability_status == availability_status)

    return query.order_by(CleanerProfile.created_at.desc()).offset(offset).limit(limit).all()


def update_cleaner_profile(db, cleaner_id, cleaner_data):
    cleaner = db.query(CleanerProfile).filter(CleanerProfile.id == cleaner_id).first()
    if cleaner:
        for key, value in cleaner_data.items():
            setattr(cleaner, key, value)
        db.commit()
        db.refresh(cleaner)
    return cleaner


def delete_cleaner_profile(db, cleaner_id):
    cleaner = db.query(CleanerProfile).filter(CleanerProfile.id == cleaner_id).first()
    if cleaner:
        db.delete(cleaner)
        db.commit()
    return cleaner


def user_has_cleaner_role(db, user_id):
    user = (
        db.query(User)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        return False
    return any(user_role.role and user_role.role.role_name == "cleaner" for user_role in user.user_roles)
