import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.database.models import User, Contact
from src.schemas.contacts import ContactBase


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1,
        username="testuser",
        email="test@test.com",
        password="testpassword",
        confirmed_email=True,
        avatar="https://example.com/avatar.jpg",
        role="USER",
    )


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    contact_data = ContactBase(
        first_name="John",
        last_name="Doe",
        email="test@test.com",
        phone="+1234567890",
        birthday="1999-01-01",
        info="Test contact",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.create_contact(contact_data, user)

    assert isinstance(result, Contact)
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "test@test.com"
    assert result.phone == "+1234567890"
    assert result.birthday == datetime(1999, 1, 1)
    assert result.info == "Test contact"
    assert mock_session.execute.call_count == 1


@pytest.mark.asyncio
async def test_create_contact_user_not_fount(contact_repository, mock_session, user):
    contact_data = ContactBase(
        first_name="John",
        last_name="Doe",
        email="test@test.com",
        phone="+1234567890",
        birthday="1999-01-01",
        info="Test contact",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    user.id = None
    result = await contact_repository.create_contact(contact_data, user)

    assert result is None


@pytest.mark.asyncio
async def test_create_contact_already_exists(contact_repository, mock_session, user):
    contact_data = ContactBase(
        first_name="John",
        last_name="Doe",
        email="test@test.com",
        phone="+1234567890",
        birthday="1999-01-01",
        info="Test contact",
    )

    # Simulate user having a valid ID
    user.id = 1

    # Mock that contact with this email already exists
    mock_existing_contact = Contact(
        first_name="John",
        last_name="Doe",
        email="test@test.com",
        phone="+1234567890",
        birthday=datetime(1999, 1, 1),
        info="Existing contact",
        user_id=user.id,
    )

    # Mock `get_contact_by_email` to return an existing contact
    contact_repository.get_contact_by_email = AsyncMock(
        return_value=mock_existing_contact
    )

    result = await contact_repository.create_contact(contact_data, user)

    assert result is None
    contact_repository.get_contact_by_email.assert_awaited_once_with(
        "test@test.com", user
    )


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        ContactBase(
            first_name="John",
            last_name="Doe",
            email="test@test.com",
            phone="+1234567890",
            birthday="1999-01-01",
            info="Test contact",
        )
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(
        0, 10, "John", "Doe", "test@test.com", user
    )
    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    assert contacts[0].last_name == "Doe"
    assert contacts[0].email == "test@test.com"
    assert contacts[0].phone == "+1234567890"
    assert contacts[0].birthday == datetime(1999, 1, 1)
    assert contacts[0].info == "Test contact"
    assert mock_session.execute.call_count == 1


@pytest.mark.asyncio
async def test_get_contact_by_email(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = ContactBase(
        first_name="John",
        last_name="Doe",
        email="test@test.com",
        phone="+1234567890",
        birthday="1999-01-01",
        info="Test contact",
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_contact_by_email("test@test.com", user)

    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "test@test.com"
    assert contact.phone == "+1234567890"
    assert contact.birthday == datetime(1999, 1, 1)
    assert contact.info == "Test contact"
    assert mock_session.execute.call_count == 1


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = ContactBase(
        first_name="John",
        last_name="Doe",
        email="test@test.com",
        phone="+1234567890",
        birthday="1999-01-01",
        info="Test contact",
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_contact_by_id(1, user)

    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "test@test.com"
    assert contact.phone == "+1234567890"
    assert contact.birthday == datetime(1999, 1, 1)
    assert contact.info == "Test contact"
    assert mock_session.execute.call_count == 1


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    existing_contact = Contact(id=1, user_id=1, first_name="John", last_name="Doe")

    contact_data = ContactBase(
        first_name="Alex",
        last_name="Smith",
        email="test@test.com",
        phone="+1234567890",
        birthday="1999-01-01",
        info="Test contact",
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(1, contact_data, user)

    assert result is not None
    assert existing_contact.first_name == "Alex"
    assert existing_contact.last_name == "Smith"
    assert mock_session.execute.call_count == 1
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_contact(contact_repository, mock_session, user):
    existing_contact = Contact(id=1, user_id=1, first_name="John", last_name="Doe")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.delete_contact(1, user)

    assert result is not None
    assert mock_session.execute.call_count == 1
    mock_session.delete.assert_called_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_contact_user_not_fount(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.delete_contact(1, user)

    assert result is None


@pytest.mark.asyncio
async def test_birthdays(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        ContactBase(
            first_name="John",
            last_name="Doe",
            email="test@test.com",
            phone="+1234567890",
            birthday="1999-01-01",
            info="Test contact",
        )
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.birthdays(0, 10, user)
    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    assert contacts[0].last_name == "Doe"
    assert contacts[0].email == "test@test.com"
    assert contacts[0].phone == "+1234567890"
    assert contacts[0].birthday == datetime(1999, 1, 1)
    assert contacts[0].info == "Test contact"
    assert mock_session.execute.call_count == 1
