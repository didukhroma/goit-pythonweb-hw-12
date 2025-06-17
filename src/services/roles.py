from typing import List, Self
from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, UserRole
from src.services.auth import auth_service


class RoleAccess:
    """
    Middleware to check if the current user has the required role.
    """

    def __init__(self: Self, allowed_roles: List[UserRole]):
        """
        Initialize the RoleAccess middleware.

        Args:
            allowed_roles (List[UserRole]): The roles that are allowed to access
                the endpoint. If the current user's role is not in this list, a
                403 error is raised.
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self: Self,
        request: Request,
        current_user: User = Depends(auth_service.get_current_user),
    ):
        """
        This method is called by FastAPI whenever a request is received to
        an endpoint that uses this middleware.

        It checks if the current user's role is in the list of roles that
        are allowed to access the endpoint. If not, a 403 error is raised.

        Args:
            request (Request): The current request object.
            current_user (User): The current user.

        Raises:
            HTTPException: If the current user's role is not in the list of
                allowed roles.
        """

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403, detail="Access denied: insufficient privileges"
            )
