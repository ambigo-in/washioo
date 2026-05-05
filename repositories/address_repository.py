from models.address import Address
from models.booking import Booking
from datetime import datetime

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
    return db.query(Address).filter(
        Address.id == address_id,
        Address.is_deleted == False,
    ).first()

def get_user_addresses(db, user_id):
    """Get all active addresses for a user"""
    return db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_deleted == False,
    ).all()

def get_user_default_address(db, user_id):
    """Get default address for a user"""
    return db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_default == True,
        Address.is_deleted == False,
    ).first()

def update_address(db, address_id, address_data):
    """Update address"""
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.is_deleted == False,
    ).first()
    if address:
        if address_data.get("is_default"):
            unset_default_addresses(db, address.user_id, exclude_address_id=address.id, commit=False)
        for key, value in address_data.items():
            setattr(address, key, value)
        db.commit()
        db.refresh(address)
    return address

def unset_default_addresses(db, user_id, exclude_address_id=None, commit=True):
    query = db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_default == True,
        Address.is_deleted == False,
    )
    if exclude_address_id:
        query = query.filter(Address.id != exclude_address_id)
    query.update({"is_default": False}, synchronize_session=False)
    if commit:
        db.commit()

def delete_address(db, address_id):
    """Remove an address from the user's active list.

    Bookings keep a restricted foreign key to addresses for historical/audit
    accuracy. If an address has booking history, soft delete it instead of
    breaking that reference.
    """
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.is_deleted == False,
    ).first()
    if not address:
        return None, "not_found"

    booking_count = db.query(Booking).filter(Booking.address_id == address.id).count()
    if booking_count:
        address.is_deleted = True
        address.deleted_at = datetime.utcnow()
        address.is_default = False
        db.commit()
        db.refresh(address)
        return address, "soft_deleted"

    db.delete(address)
    db.commit()
    return address, "hard_deleted"
