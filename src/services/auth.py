import redis
import pickle
from typing import Self
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.conf.config import settings
from src.services.users import UserService
from src.database.db import get_db
from src.database.models import User
from src.database.models import UserRole
from src.conf.config import settings


class Auth:
    """
    Authentication class for handling user authentication and authorization.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies that the provided plain text password matches the hashed password.

        Args:
            plain_password (str): The plain text password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self: Self, password: str):
        """
        Hashes the given password using the configured password hashing context.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: float = 15):
        """
        Creates a JWT access token for authentication.

        Args:
            data (dict): The payload data to include in the token.
            expires_delta (float, optional): The expiration time in minutes for the token. Defaults to 15.

        Returns:
            str: The encoded JWT access token.
        """

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
        to_encode.update(
            {
                "iat": datetime.now(timezone.utc),
                "exp": expire,
                "scope": "access_token",
            }
        )
        encoded_access_token = jwt.encode(
            to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_access_token

    def create_email_token(self, data: dict):
        """
        Creates a JWT token for email verification purposes.

        Args:
            data (dict): The payload data to include in the token.

        Returns:
            str: The encoded JWT email verification token.
        """

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "email_token"}
        )
        token = jwt.encode(
            to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )
        return token

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        Retrieve the current user based on the provided JWT access token.

        This function is a dependency for endpoints that require authentication.
        It verifies the JWT access token and returns the corresponding user model.

        Args:
            token (str, optional): The JWT access token to verify. Defaults to
                the value of the "Authorization" header.
            db (AsyncSession, optional): The database session. Defaults to the
                value of the `get_db` dependency.

        Raises:
            HTTPException: If the provided token is invalid or the user
                associated with the token does not exist.

        Returns:
            User: The user model associated with the provided token.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user_service = UserService(db)

        user = self.r.get(f"user:{email}")
        if user is None:
            user = await user_service.get_user_by_email(email)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)

        if user is None:
            raise credentials_exception
        return user

    def get_email_from_token(self, token: str):
        """
        Retrieves the email associated with a given JWT email verification token.

        Args:
            token (str): The JWT email verification token to decode.

        Returns:
            str: The email associated with the given token.

        Raises:
            HTTPException: If the token is invalid or has an invalid scope.
        """
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload["scope"] == "email_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()
