from typing import Self
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas.users import UserCreate


class UserService:
    """Service class for user operations."""

    def __init__(self: Self, db: AsyncSession):
        """
        Initializes the user service with the given database session.

        Args:
            db (AsyncSession): The instance of the database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self: Self, user: UserCreate):
        """
        Creates a new user in the database.

        Args:
            user (UserCreate): The user data to create the new user.

        Returns:
            User | None: The created user if successful, None if the user already exists.
        """

        avatar = None
        try:
            g = Gravatar(user.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        return await self.repository.create_user(user, avatar)

    async def get_user_by_email(self: Self, email: str):
        """
        Retrieves a user by their email address.

        Args:
            email (str): The email address to search for.

        Returns:
            User | None: The user if found, None otherwise.
        """
        return await self.repository.get_user_by_email(email)

    async def get_user_by_name(self: Self, username: str):
        """
        Retrieves a user by their username.

        Args:
            username (str): The username to search for.

        Returns:
            User | None: The user if found, None otherwise.
        """

        return await self.repository.get_user_by_name(username)

    async def confirmed_email(self: Self, email: str):
        """
        Confirms the email of a user by setting the confirmed_email flag to True.

        Args:
            email (str): The email of the user to confirm.

        Returns:
            None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar(self: Self, email: str, avatar_url: str):
        """
        Updates the avatar URL for a user identified by their email.

        Args:
            email (str): The email of the user whose avatar is to be updated.
            avatar_url (str): The new avatar URL to be set for the user.

        Returns:
            UserResponse: The updated user with the new avatar URL.
        """

        return await self.repository.update_avatar(email, avatar_url)

    async def reset_password(self: Self, password: str, email: str):
        """
        Resets the password for a user identified by their email.

        Args:
            password (str): The new password to be set for the user.
            email (str): The email of the user whose password is to be reset.

        Returns:
            UserResponse: The updated user with the new password.
        """

        return await self.repository.reset_password(password, email)
