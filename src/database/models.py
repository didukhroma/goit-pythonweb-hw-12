from enum import Enum

from sqlalchemy import (
    create_engine,
    Integer,
    String,
    Boolean,
    func,
    ForeignKey,
    Enum as SqlEnum,
)
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.sql.sqltypes import DateTime
from datetime import date


class Base(DeclarativeBase):
    """
    Base class for declarative models
    """

    pass


class UserRole(str, Enum):
    """
    Represents the different roles a user can have within the application.

    These roles determine the level of access and permissions granted to a user.

    :cvar USER: Standard user role with basic access privileges.
    :cvar ADMIN: Administrator role with full access and management capabilities.
    """

    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """
    Represents contact information associated with a user.

    This model stores details about individual contacts, including personal data,
    contact information, birth date, and additional notes. Each contact belongs to a single user.

    :ivar id: Unique identifier for the contact.
    :vartype id: int
    :ivar first_name: The first name of the contact.
    :vartype first_name: str (max 50 chars)
    :ivar last_name: The last name of the contact.
    :vartype last_name: str (max 50 chars)
    :ivar email: The unique email address of the contact.
    :vartype email: str (max 100 chars)
    :ivar phone: The phone number of the contact.
    :vartype phone: str (max 12 chars)
    :ivar birthday: The birth date of the contact.
    :vartype birthday: datetime.date
    :ivar info: Additional information or notes about the contact.
    :vartype info: str
    :ivar user_id: The ID of the user to whom this contact belongs (foreign key to :class:`User.id`).
    :vartype user_id: int
    :ivar user: The user object to whom this contact belongs (relationship).
    :vartype user: :class:`User`
    :ivar created_at: Timestamp of when the contact record was created (UTC with timezone).
    :vartype created_at: datetime
    :ivar updated_at: Timestamp of the last update to the contact record (UTC with timezone).
    :vartype updated_at: datetime

    # Blank line!
    :raises sqlalchemy.exc.IntegrityError: If a new contact violates unique constraints (email)
    or foreign key constraints (user_id).
    """

    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(12), nullable=False)
    birthday: Mapped[date] = mapped_column(DateTime(timezone=True), nullable=False)
    info: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship("User", backref="contacts")
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class User(Base):
    """
    Represents a user in the application.

    This model stores core user information including authentication credentials,
    contact details, profile specifics, and role-based access control.

    :ivar id: Unique identifier for the user.
    :vartype id: int
    :ivar username: Unique username for login and display.
    :vartype username: str (max 50 chars)
    :ivar email: Unique email address for contact and recovery.
    :vartype email: str (max 100 chars)
    :ivar password: Hashed password for secure authentication.
    :vartype password: str (max 255 chars)
    :ivar confirmed_email: Flag indicating if the user's email has been verified.
    :vartype confirmed_email: bool
    :ivar avatar: Optional URL or path to the user's profile picture.
    :vartype avatar: str or None
    :ivar role: User's role determining access permissions.
    :vartype role: UserRole (Enum: USER, ADMIN, MODERATOR)
    :ivar created_at: Timestamp of when the user account was created (UTC with timezone).
    :vartype created_at: datetime
    :ivar updated_at: Timestamp of the last update to the user account (UTC with timezone).
    :vartype updated_at: datetime

    # Blank line!
    :raises sqlalchemy.exc.IntegrityError: If a new user violates unique constraints (username, email).
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    confirmed_email: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole), default=UserRole.USER, nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
