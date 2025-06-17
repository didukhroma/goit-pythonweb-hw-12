from typing import Self

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.users import UserModel, UserResponse


class UserRepository:
    """
    User repository class.
    """

    def __init__(self: Self, session: AsyncSession):
        self.db = session

    async def get_user_by_email(self: Self, user_email: str) -> User | None:
        """
        Gets a user by its email.

        Args:
            user_email (str): The email to search for.

        Returns:
            User | None: The user if found, None otherwise.
        """

        stmt = select(User).where(User.email == user_email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_name(self: Self, username: str) -> User | None:
        """
        Gets a user by its username.

        Args:
            username (str): The username to search for.

        Returns:
            User | None: The user if found, None otherwise.
        """
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self: Self, user: UserModel, avatar) -> User | None:
        """
        Creates a new user in the database.

        Args:
            user (UserModel): The user data to create the new user.
            avatar (str): The avatar URL to save in the database.

        Returns:
            User | None: The created user if successful, None if the user already exists.
        """
        user = User(
            **user.model_dump(exclude_unset=True, exclude={"password"}),
            password=user.password,
            avatar=avatar,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self: Self, user_email: str) -> None:
        """
        Confirms the email of a user by setting the confirmed_email flag to True.

        Args:
            user_email (str): The email of the user to confirm.

        Returns:
            None
        """
        user = await self.get_user_by_email(user_email)
        user.confirmed_email = True
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar(self: Self, email: str, url: str) -> UserResponse:
        """
        Updates the avatar URL for a user identified by their email.

        Args:
            email (str): The email of the user whose avatar is to be updated.
            url (str): The new avatar URL to be set for the user.

        Returns:
            UserResponse: The updated user with the new avatar URL.
        """

        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def reset_password(self: Self, password: str, email: str) -> UserResponse:
        """
        Resets the password for a user identified by their email.

        Args:
            password (str): The new password to be set for the user.
            email (str): The email of the user whose password is to be reset.

        Returns:
            UserResponse: The updated user with the new password.
        """
        user = await self.get_user_by_email(email)
        user.password = password
        await self.db.commit()
        await self.db.refresh(user)
        return user
