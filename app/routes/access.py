
from fastapi import APIRouter, Depends

from app.database.models import User
from app.routes.auth import require_roles


router = APIRouter(
    prefix="/access",
    tags=["Role Permissions"]
)


# ADMIN ONLY
@router.get("/admin")
def admin_access(
    current_user: User = Depends(require_roles("admin"))
):
    return {
        "message": "Welcome Admin! You have admin access.",
        "user": current_user.full_name,
        "role": current_user.role
    }


# GATE STAFF ONLY
@router.get("/staff")
def staff_access(
    current_user: User = Depends(require_roles("gate_staff"))
):
    return {
        "message": "Welcome Gate Staff! You have ticket scanning access.",
        "user": current_user.full_name,
        "role": current_user.role
    }


# ATTENDEE ONLY
@router.get("/attendee")
def attendee_access(
    current_user: User = Depends(require_roles("attendee"))
):
    return {
        "message": "Welcome Attendee! You have attendee access.",
        "user": current_user.full_name,
        "role": current_user.role
    }
