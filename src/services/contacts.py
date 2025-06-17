from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactBase
from src.database.models import User

from typing import Self


class ContactService:
    """Service class for handling contact operations."""

    def __init__(self: Self, db: AsyncSession):
        """
        Initializes the contact service with the given database session.

        Args:
            db (AsyncSession): The instance of the database session.
        """

        self.repository = ContactRepository(db)

    async def create_contact(self: Self, body: ContactBase, user: User):
        """
        Creates a new contact.

        Args:
            body (ContactBase): The contact data.
            user (User): The user who creates the contact.

        Returns:
            Contact | None: The created contact or None if the contact already exists.
        """
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self: Self,
        skip: int,
        limit: int,
        name: str | None,
        surname: str | None,
        email: str | None,
        user: User,
    ):
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
        return await self.repository.get_contacts(
            skip, limit, name, surname, email, user
        )

    async def get_contact_by_id(self: Self, contact_id: int, user: User):
        """
        Gets a contact by its ID.

        Args:
            contact_id (int): The contact ID.
            user (User): The user who owns the contact.

        Returns:
            Contact | None: The contact if it exists, None otherwise.
        """

        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(
        self: Self, contact_id: int, body: ContactBase, user: User
    ):
        """
        Updates an existing contact with new data.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactBase): The new data for the contact.
            user (User): The user who owns the contact.

        Returns:
            Contact | None: The updated contact if it exists, None otherwise.
        """

        return await self.repository.update_contact(contact_id, body, user)

    async def delete_contact(self: Self, contact_id: int, user: User):
        """
        Deletes an existing contact by its ID.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The user who owns the contact.

        Returns:
            None if the contact does not exist, otherwise True.
        """

        return await self.repository.delete_contact(contact_id, user)

    async def birthdays(self: Self, skip: int, limit: int, user: User):
        """
        Gets all contacts that have their birthday in the next 7 days.

        Args:
            skip (int): The number of items to skip.
            limit (int): The number of items to return.
            user (User): The user who owns the contacts.

        Returns:
            List[Contact]: A list of contacts that have their birthday in the next 7 days.
        """
        return await self.repository.birthdays(skip, limit, user)
