from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.schemas import PackageOut, VehicleType
from app.database.session import SessionLocal
from app.models.models import Package

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[PackageOut])
def list_packages(vehicle_type: VehicleType = None, db: Session = Depends(get_db)):
    """List all packages, optionally filtered by vehicle type"""
    query = db.query(Package)
    if vehicle_type:
        query = query.filter(Package.vehicle_type == vehicle_type)
    return query.all()

@router.get("/{package_id}", response_model=PackageOut)
def get_package(package_id: str, db: Session = Depends(get_db)):
    """Get details of a specific package"""
    return db.query(Package).filter(Package.id == package_id).first()
