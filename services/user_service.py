from models.user import User

def get_user_profile(user: User):
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "phone": user.phone,
        "email": user.email,
        "is_verified": user.is_verified,
        "is_active": user.is_active,
        "created_at": user.created_at
    }