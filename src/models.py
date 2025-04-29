from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import DateTime
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo


# Define Moscow timezone for use across the application
MOSCOW_TZ = ZoneInfo("Europe/Moscow")


class UserBase(SQLModel):
    """
    Base model for User entities with common attributes.

    This base class defines the core attributes that both the database model
    and the read model for users share.

    Attributes:
        id: The Telegram user ID
        phone_id: Optional reference to a whitelisted phone number
        is_admin: Whether the user has administrative privileges
        is_active: Whether the user's account is active
    """

    id: int
    phone_id: Optional[int]
    is_admin: bool = False
    is_active: bool = False


class User(UserBase, table=True):
    """
    User table for storing Telegram user information.

    This model represents users in the database and tracks their registration status,
    administrative privileges, and phone number verification.

    Attributes:
        id: The Telegram user ID (primary key)
        phone_id: Foreign key to the PhoneWhiteList table
        is_admin: Whether the user has administrative privileges
        is_active: Whether the user is verified and active
        phone: Relationship to the PhoneWhiteList model
        time_registered: When the user first registered
        time_updated: When the user was last updated
    """

    id: int = Field(primary_key=True)  # Telegram ID
    phone_id: Optional[int] = Field(
        default=None, unique=True, foreign_key="phonewhitelist.phone"
    )
    is_admin: bool = False
    is_active: bool = False

    phone: "PhoneWhiteList" = Relationship(back_populates="user")

    time_registered: datetime = Field(default_factory=lambda: datetime.now(MOSCOW_TZ))
    time_updated: datetime = Field(
        default_factory=lambda: datetime.now(MOSCOW_TZ),
        sa_column=Column(
            DateTime(timezone=False), onupdate=lambda: datetime.now(MOSCOW_TZ)
        )
    )


class UserRead(UserBase):
    """
    Read model for User entities.

    This model is used for API responses and data transfer without exposing
    database-specific attributes.
    """
    ...


class PhoneWhiteListBase(SQLModel):
    """
    Base model for PhoneWhiteList entities with common attributes.

    This base class defines the core attributes that both the database model
    and the read model for whitelisted phone numbers share.

    Attributes:
        phone: The whitelisted phone number (must be a valid Russian mobile number)
    """

    phone: int = Field(gt=9000000000, lt=9999999999)


class PhoneWhiteList(PhoneWhiteListBase, table=True):
    """
    PhoneWhiteList table for storing authorized phone numbers.

    This model represents whitelisted phone numbers in the database which are
    allowed to register with the bot. Only users with a whitelisted phone
    number can activate their accounts.

    Attributes:
        phone: The whitelisted phone number (primary key)
        user: Relationship to the User model
    """

    phone: int = Field(primary_key=True, gt=9000000000, lt=9999999999)

    user: User = Relationship(back_populates="phone")


class PhoneWhiteListRead(PhoneWhiteListBase):
    """
    Read model for PhoneWhiteList entities.

    This model is used for API responses and data transfer, including
    the associated user if any.

    Attributes:
        user: Optional related User entity
    """

    user: Optional[UserRead]


class TelegramGroup(SQLModel, table=True):
    """
    Chanel table for storing Telegram channels or group chats.

    This model represents Telegram channels or groups that the bot manages.
    Only one channel can be marked as the target channel at a time.

    Attributes:
        id: The Telegram channel or group ID (primary key)
        target: Whether this is the currently targeted channel
    """

    id: int = Field(primary_key=True)
    target: bool = Field(default=False)
