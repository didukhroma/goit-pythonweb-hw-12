from fastapi import APIRouter, Depends, Request, UploadFile, File


from slowapi import Limiter
from slowapi.util import get_remote_address

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.users import UserModel, UserResponse
from src.services.auth import auth_service
from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.database.db import get_db
from src.conf.config import settings
from src.services.roles import RoleAccess
from src.database.models import UserRole

router = APIRouter(prefix="/users", tags=["Users"])
limiter = Limiter(key_func=get_remote_address)

allowed_operation_avatar = RoleAccess([UserRole.ADMIN])


@router.get(
    "/me",
    response_model=UserResponse,
    description="No more than 10 requests per minute",
)
@limiter.limit("10/minute")
async def get_me(
    request: Request, user: UserModel = Depends(auth_service.get_current_user)
):
    """
    Get the current user.

    Args:
        request (Request): The request object.
        user (UserModel): The current user.

    Returns:
        UserModel: The current user.
    """
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(allowed_operation_avatar)],
)
async def update_avatar(
    file: UploadFile = File(),
    user: UserModel = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the current user's avatar.

    Args:
        file (UploadFile): The new avatar to upload.
        user (UserModel): The current user.
        db (AsyncSession): The database session.

    Returns:
        UserModel: The updated user.
    """

    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.username)
    user_service = UserService(db)
    user = await user_service.update_avatar(user.email, avatar_url)
    return user
