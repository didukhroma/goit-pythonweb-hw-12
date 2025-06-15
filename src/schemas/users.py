from pydantic import BaseModel, EmailStr, ConfigDict, Field
from src.database.models import UserRole


class UserModel(BaseModel):
    id: int
    username: str
    password: str
    avatar: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class RequestEmail(BaseModel):
    email: EmailStr


class TokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResetPassword(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=12)
