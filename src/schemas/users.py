from pydantic import BaseModel, EmailStr, ConfigDict


class UserModel(BaseModel):
    id: int
    username: str
    password: str
    avatar: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)


class RequestEmail(BaseModel):
    email: EmailStr


class TokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"
