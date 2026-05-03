from models.customer_vehicle import CustomerVehicle


def create_vehicle(db, vehicle_data):
    vehicle = CustomerVehicle(**vehicle_data)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def get_customer_vehicles(db, customer_id):
    return (
        db.query(CustomerVehicle)
        .filter(CustomerVehicle.customer_id == customer_id)
        .order_by(CustomerVehicle.is_default.desc(), CustomerVehicle.created_at.desc())
        .all()
    )


def get_customer_vehicle_by_id(db, customer_id, vehicle_id):
    return (
        db.query(CustomerVehicle)
        .filter(
            CustomerVehicle.id == vehicle_id,
            CustomerVehicle.customer_id == customer_id,
        )
        .first()
    )


def get_customer_default_vehicle(db, customer_id):
    return (
        db.query(CustomerVehicle)
        .filter(
            CustomerVehicle.customer_id == customer_id,
            CustomerVehicle.is_default.is_(True),
        )
        .first()
    )


def unset_customer_default_vehicles(db, customer_id):
    (
        db.query(CustomerVehicle)
        .filter(CustomerVehicle.customer_id == customer_id)
        .update({"is_default": False}, synchronize_session=False)
    )
    db.commit()


def update_vehicle(db, vehicle, vehicle_data):
    for key, value in vehicle_data.items():
        setattr(vehicle, key, value)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def delete_vehicle(db, vehicle):
    db.delete(vehicle)
    db.commit()
