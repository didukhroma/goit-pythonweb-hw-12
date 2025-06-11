from typing import List, Self
from datetime import datetime, timedelta

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactBase


class ContactRepository:
    def __init__(self: Self, session: AsyncSession):
        self.db = session

    async def create_contact(
        self: Self, body: ContactBase, user=User
    ) -> Contact | None:
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
        stmt = select(Contact).filter(
            Contact.user_id == user.id, Contact.id == contact_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_contact(
        self: Self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump().items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def delete_contact(self: Self, contact_id: int, user: User) -> None:
        exist_contact = await self.get_contact_by_id(contact_id, user)
        if exist_contact is None:
            return None
        await self.db.delete(exist_contact)
        await self.db.commit()
        return True

    async def birthdays(self: Self, skip: int, limit: int, user: User) -> List[Contact]:
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
