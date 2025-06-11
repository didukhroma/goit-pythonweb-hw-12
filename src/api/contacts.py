from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.auth import auth_service
from src.schemas.contacts import ContactBase, ContactResponse
from src.services.contacts import ContactService
from src.database.models import User

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("/", response_model=List[ContactResponse], status_code=status.HTTP_200_OK)
async def get_contacts(
    name: str = Query(None),
    surname: str = Query(None),
    email: str = Query(None),
    skip: int = 0,
    limit: int = Query(10, le=1000),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(
        skip, limit, name, surname, email, user
    )
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactBase,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.create_contact(body, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email in use")
    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact_by_id(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactBase,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.delete_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )


@router.get(
    "/birthdays/", response_model=List[ContactResponse], status_code=status.HTTP_200_OK
)
async def get_upcomming_birthdays(
    skip: int = 0,
    limit: int = Query(10, le=1000),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact_service = ContactService(db)
    contacts = await contact_service.birthdays(skip, limit, user)
    return contacts
