from typing import List, Self
from datetime import datetime, timedelta

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactBase


class ContactRepository:
    """
    Repository for managing contacts.
    """

    def __init__(self: Self, session: AsyncSession):
        """
        Initializes the contact repository with the given session.

        Args:
            session (AsyncSession): The instance of the database session.
        """
        self.db = session

    async def create_contact(
        self: Self, body: ContactBase, user=User
    ) -> Contact | None:
        """
        Creates a new contact.

        Args:
            body (ContactBase): The contact data.
            user (User): The user who creates the contact.

        Returns:
            Contact | None: The created contact or None if the contact already exists.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)

        exist_contact = await self.get_contact_by_email(contact.email, user)

        if exist_contact:
            return None

        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def get_contact_by_email(
        self: Self, contact_email: str, user: User
    ) -> Contact | None:
        """
        Gets a contact by its email.

        Args:
            contact_email (str): The contact email.
            user (User): The user who owns the contact.

        Returns:
            Contact | None: The contact if found, None otherwise.
        """
        stmt = select(Contact).filter(
            Contact.user_id == user.id, Contact.email == contact_email
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_contacts(
        self: Self,
        skip: int,
        limit: int,
        name: str | None,
        surname: str | None,
        email: str | None,
        user: User,
    ) -> List[Contact]:
        """
        Gets a list of contacts filtered by the given parameters.

        Args:
            skip (int): The number of items to skip.
            limit (int): The number of items to return.
            name (str | None): The contact name to filter by.
            surname (str | None): The contact surname to filter by.
            email (str | None): The contact email to filter by.
            user (User): The user who owns the contacts.

        Returns:
            List[Contact]: The list of filtered contacts.
        """
        stmt = select(Contact).filter(Contact.user_id == user.id)
        if name:
            stmt = stmt.filter(Contact.first_name == name)
        if surname:
            stmt = stmt.filter(Contact.last_name == surname)
        if email:
            stmt = stmt.filter(Contact.email == email)
        stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(
        self: Self, contact_id: int, user: User
    ) -> Contact | None:
        """
        Gets a contact by its ID.

        Args:
            contact_id (int): The contact ID.
            user (User): The user who owns the contact.

        Returns:
            Contact | None: The contact if it exists, None otherwise.
        """
        stmt = select(Contact).filter(
            Contact.user_id == user.id, Contact.id == contact_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_contact(
        self: Self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        """
        Updates an existing contact with new data.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactBase): The new data for the contact.
            user (User): The user who owns the contact.

        Returns:
            Contact | None: The updated contact if it exists, None otherwise.
        """

        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump().items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def delete_contact(self: Self, contact_id: int, user: User) -> None:
        """
        Deletes an existing contact by its ID.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The user who owns the contact.

        Returns:
            None if the contact does not exist, otherwise True.
        """
        exist_contact = await self.get_contact_by_id(contact_id, user)
        if exist_contact is None:
            return None
        await self.db.delete(exist_contact)
        await self.db.commit()
        return True

    async def birthdays(self: Self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Gets all contacts that have their birthday in the next 7 days.

        Args:
            skip (int): The number of items to skip.
            limit (int): The number of items to return.
            user (User): The user who owns the contacts.

        Returns:
            List[Contact]: A list of contacts that have their birthday in the next 7 days.
        """

        today = datetime.now().date()
        end_day = today + timedelta(days=7)
        stmt = (
            select(Contact)
            .filter(
                and_(
                    Contact.user_id == user.id,
                    Contact.birthday >= today,
                    Contact.birthday <= end_day,
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
