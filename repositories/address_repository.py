from models.address import Address

def create_address(db, address_data):
    """Create a new address"""
    if address_data.get("is_default"):
        unset_default_addresses(db, address_data["user_id"], commit=False)
    address = Address(**address_data)
    db.add(address)
    db.commit()
    db.refresh(address)
    return address

def get_address_by_id(db, address_id):
    """Get address by ID"""
    return db.query(Address).filter(Address.id == address_id).first()

def get_user_addresses(db, user_id):
    """Get all addresses for a user"""
    return db.query(Address).filter(Address.user_id == user_id).all()

def get_user_default_address(db, user_id):
    """Get default address for a user"""
    return db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_default == True
    ).first()

def update_address(db, address_id, address_data):
    """Update address"""
    address = db.query(Address).filter(Address.id == address_id).first()
    if address:
        if address_data.get("is_default"):
            unset_default_addresses(db, address.user_id, exclude_address_id=address.id, commit=False)
        for key, value in address_data.items():
            setattr(address, key, value)
        db.commit()
        db.refresh(address)
    return address

def unset_default_addresses(db, user_id, exclude_address_id=None, commit=True):
    query = db.query(Address).filter(Address.user_id == user_id, Address.is_default == True)
    if exclude_address_id:
        query = query.filter(Address.id != exclude_address_id)
    query.update({"is_default": False}, synchronize_session=False)
    if commit:
        db.commit()

def delete_address(db, address_id):
    """Delete address"""
    address = db.query(Address).filter(Address.id == address_id).first()
    if address:
        db.delete(address)
        db.commit()
    return address
