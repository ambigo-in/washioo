from models.service_category import ServiceCategory

def get_all_services(db, limit=50, offset=0):
    """Get all active services"""
    return (
        db.query(ServiceCategory)
        .filter(ServiceCategory.is_active == True)
        .order_by(ServiceCategory.service_name.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_service_by_id(db, service_id):
    """Get service by ID"""
    return db.query(ServiceCategory).filter(ServiceCategory.id == service_id).first()

def get_service_by_name(db, service_name):
    """Get service by name"""
    return db.query(ServiceCategory).filter(ServiceCategory.service_name == service_name).first()

def create_service(db, service_data):
    """Create a new service"""
    service = ServiceCategory(**service_data)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

def update_service(db, service_id, service_data):
    """Update service"""
    service = db.query(ServiceCategory).filter(ServiceCategory.id == service_id).first()
    if service:
        for key, value in service_data.items():
            setattr(service, key, value)
        db.commit()
        db.refresh(service)
    return service

def delete_service(db, service_id):
    """Soft delete service by marking it inactive"""
    service = db.query(ServiceCategory).filter(ServiceCategory.id == service_id).first()
    if service:
        service.is_active = False
        db.commit()
        db.refresh(service)
    return service
