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