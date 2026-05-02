from models.payment import Payment
from models.booking import Booking
from sqlalchemy.orm import joinedload


def get_payment_by_id(db, payment_id):
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_payment_by_booking_id(db, booking_id):
    return db.query(Payment).filter(Payment.booking_id == booking_id).first()


def get_all_payments(db, limit=50, offset=0):
    return (
        db.query(Payment)
        .options(joinedload(Payment.booking))
        .order_by(Payment.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_payments_by_status(db, status, limit=50, offset=0):
    return (
        db.query(Payment)
        .filter(Payment.payment_status == status)
        .options(joinedload(Payment.booking))
        .order_by(Payment.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_payments_by_customer(db, customer_id, limit=50, offset=0):
    return (
        db.query(Payment)
        .filter(Payment.customer_id == customer_id)
        .options(joinedload(Payment.booking))
        .order_by(Payment.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_payment_stats(db):
    total = db.query(Payment).count()
    pending = db.query(Payment).filter(Payment.payment_status == "pending").count()
    paid = db.query(Payment).filter(Payment.payment_status == "paid").count()
    failed = db.query(Payment).filter(Payment.payment_status == "failed").count()
    
    return {
        "total": total,
        "pending": pending,
        "paid": paid,
        "failed": failed
    }


def create_payment(db, payment_data):
    payment = Payment(**payment_data)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def update_payment(db, payment_id, update_data):
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        return None
    
    for key, value in update_data.items():
        if value is not None:
            setattr(payment, key, value)
    
    db.commit()
    db.refresh(payment)
    return payment


def delete_payment(db, payment_id):
    payment = get_payment_by_id(db, payment_id)
    if payment:
        db.delete(payment)
        db.commit()
        return True
    return False


def get_payment_total_amount(db, status=None):
    query = db.query(Payment)
    if status:
        query = query.filter(Payment.payment_status == status)
    
    total = sum(float(p.amount) for p in query.all() if p.amount)
    return total
