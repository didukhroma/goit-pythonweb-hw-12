from pydantic import BaseModel, EmailStr, ConfigDict, Field
from src.database.models import UserRole


class UserModel(BaseModel):
    """User model."""

    id: int
    username: str
    password: str
    avatar: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """User create model."""

    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model."""

    id: int
    username: str
    email: str
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class RequestEmail(BaseModel):
    """Request email model."""

    email: EmailStr


class RefreshTokenResponse(BaseModel):
    """Refresh token model."""

    refresh_token: str


class TokenModel(BaseModel):
    """Token model."""

    refresh_token: str
    access_token: str
    token_type: str = "bearer"


class ResetPassword(BaseModel):
    """Reset password model."""

    new_password: str = Field(..., min_length=6, max_length=12)
