from fastapi import Depends, HTTPException, status
from core.dependencies import get_current_user


def require_roles(allowed_roles: list[str]):
    def role_checker(current_user=Depends(get_current_user)):
        user_roles = [ur.role.role_name for ur in current_user.user_roles]

        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Allowed roles: {', '.join(allowed_roles)}"
            )

        return current_user

    return role_checker


# Single-role
admin_only = require_roles(["admin"])
customer_only = require_roles(["customer"])
cleaner_only = require_roles(["cleaner"])

# Multi-role
admin_or_cleaner = require_roles(["admin", "cleaner"])
admin_or_customer = require_roles(["admin", "customer"])
cleaner_or_customer = require_roles(["cleaner", "customer"])
all_authenticated_users = require_roles(["admin", "customer", "cleaner"])