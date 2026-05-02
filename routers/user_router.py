from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.role_dependencies import admin_only, all_authenticated_users
from services.user_service import (
    get_user_details_service,
    update_user_details_service,
    delete_user_service,
    get_users_by_role_service,
    get_all_users_service,
    get_user_profile,
)
from schemas.user_schema import UpdateUserRequest

router = APIRouter(prefix="/users")


@router.get("/me", tags=["Profile APIs"])
def get_my_profile(current_user=Depends(all_authenticated_users)):
    return {
        "message": "Current user profile fetched successfully",
        "user": get_user_profile(current_user)
    }


@router.patch("/me", tags=["Profile APIs"])
def update_my_profile(
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user=Depends(all_authenticated_users)
):
    try:
        updated_user = update_user_details_service(db, current_user.id, payload)
        return {
            "message": "Profile updated successfully",
            "user": updated_user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", tags=["Admin APIs"])
def list_users_by_role(
    db: Session = Depends(get_db),
    role: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_admin=Depends(admin_only)
):
    try:
        if role:
            users = get_users_by_role_service(db, role, limit, offset)
        else:
            users = get_all_users_service(db, limit, offset)
        return {
            "message": "Users fetched successfully",
            "users": users,
            "total": len(users)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", tags=["Admin APIs"])
def get_user_by_id(user_id: str, db: Session = Depends(get_db), current_admin=Depends(admin_only)):
    try:
        user = get_user_details_service(db, user_id)
        return {
            "message": "User fetched successfully",
            "user": user
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{user_id}", tags=["Admin APIs"])
def update_user(
    user_id: str,
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(admin_only)
):
    try:
        updated_user = update_user_details_service(db, user_id, payload)
        return {
            "message": "User updated successfully",
            "user": updated_user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", tags=["Admin APIs"])
def delete_user(user_id: str, db: Session = Depends(get_db), current_admin=Depends(admin_only)):
    try:
        delete_user_service(db, user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
