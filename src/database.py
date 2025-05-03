"""
Database management module for Telegram group access bot.

This module provides a DatabaseManager class that handles all database operations
for the Telegram bot, including user management, channel management, and phone
whitelist operations.

Attributes:
    DatabaseError: Base exception for database-related errors
    ItemNotFoundException: Exception raised when an item is not found in the database
"""

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import Union, Sequence
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from loguru import logger

from settings import settings
from models import User, PhoneWhiteList, TelegramGroup


class DatabaseError(Exception):
    """Base exception for database-related errors."""

    ...


class ItemNotFoundException(DatabaseError):
    """Exception raised when an item is not found in the database."""

    ...


class DatabaseManager:
    """
    Database manager for the Telegram bot.

    This class handles all database operations, including user management,
    channel management, and phone whitelist operations. It uses SQLModel and
    asyncio to provide async database access.

    Attributes:
        engine: The SQLAlchemy async engine instance

    Examples:
        >>> db_manager = DatabaseManager()
        >>> user = await db_manager.get_user(12345678)
    """

    def __init__(self) -> None:
        """
        Initialize the database manager with an async engine.

        The engine is created using the DATABASE_URL from settings.

        Returns:
            None

        Examples:
            >>> db_manager = DatabaseManager()
        """
        self.engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async def get_user(self, user_id: int) -> Union[User, None]:
        """
        Get a user by their Telegram ID.

        Args:
            user_id: The Telegram user ID

        Returns:
            User: The user record if found
            None: If no user with the given ID exists

        Examples:
            >>> user = await db_manager.get_user(12345678)
            >>> if user:
            ...     print(f"User {user.id} is {'active' if user.is_active else 'inactive'}")
        """  # noqa: E501
        async with AsyncSession(self.engine) as session:
            result = await session.get(User, user_id)
            return result

    async def add_user(self, user_id: int) -> User:
        """
        Add a new user to the database.

        Args:
            user_id: The Telegram user ID

        Returns:
            User: The newly created user record

        Examples:
            >>> new_user = await db_manager.add_user(12345678)
            >>> print(f"Added user {new_user.id}")
        """
        async with AsyncSession(self.engine) as session:
            user = User(id=user_id)
            session.add(user)
            try:
                await session.commit()
            except IntegrityError as e:
                logger.warning(e)
                return user
            await session.refresh(user)
            return user

    async def bind_phone_to_user(self, user_id: int, phone_num: int) -> User:
        async with AsyncSession(self.engine) as session:
            user = await session.get(User, user_id)
            phone = await session.get(PhoneWhiteList, phone_num)
            if not phone:
                raise ItemNotFoundException("There is no phone {phone_num} in database")
            if not user:
                user = await self.add_user(user_id)
            user.phone = phone
            await session.commit()
            await session.refresh(user)
            return user

    async def add_channel(self, channel_id: int) -> TelegramGroup:
        """
        Add a new Telegram channel or group to the database.

        Args:
            channel_id: The Telegram channel/group ID

        Returns:
            TelegramGroup: The newly created channel record

        Examples:
            >>> channel = await db_manager.add_chanel(-1001234567890)
            >>> print(f"Added channel {channel.id}")
        """
        async with AsyncSession(self.engine) as session:
            channel = TelegramGroup(id=channel_id)
            session.add(channel)
            await session.commit()
            await session.refresh(channel)
            return channel

    async def delete_channel(self, channel_id: int) -> TelegramGroup:
        """
        Delete a Telegram channel or group from the database.

        Args:
            channel_id: The Telegram channel/group ID

        Returns:
            TelegramGroup: The deleted channel record

        Examples:
            >>> deleted = await db_manager.delete_chanel(-1001234567890)
            >>> print(f"Deleted channel {deleted.id}")
        """
        async with AsyncSession(self.engine) as session:
            channel = TelegramGroup(id=channel_id)
            await session.delete(channel)
            await session.commit()
            await session.refresh(channel)
            return channel

    async def get_registered_channels(self) -> Sequence[TelegramGroup]:
        """
        Get all registered Telegram channels and groups.

        Returns:
            Sequence[TelegramGroup]: A sequence of all registered channels

        Examples:
            >>> channels = await db_manager.get_registered_channels()
            >>> for channel in channels:
            ...     print(f"Channel ID: {channel.id}, Target: {channel.target}")
        """
        async with AsyncSession(self.engine) as session:
            query = select(TelegramGroup)
            channel = await session.exec(query)
            return channel.all()

    async def get_target_channel(self) -> Sequence[TelegramGroup]:
        """
        Find the target channel (the channel the bot is currently managing).


        Returns:
            Sequence[TelegramGroup]: A sequence containing the target channel

        Examples:
            >>> target_channels = await db_manager.get_target_chanel()
            >>> if target_channels:
            ...     print(f"Target channel ID: {target_channels[0].id}")
        """
        async with AsyncSession(self.engine) as session:
            query = select(TelegramGroup).where(TelegramGroup.target == True)  # noqa: E712, E501
            channel = await session.exec(query)
            return channel.all()

    async def make_channel_target(self, channel_id: int) -> TelegramGroup:
        """
        Set a specific channel as the target channel for the bot.

        This method unsets the target flag for any previously targeted channels
        and sets it for the specified channel.

        Args:
            chanel_id: The ID of the channel to set as target

        Returns:
            TelegramGroup: The newly targeted channel

        Examples:
            >>> target = await db_manager.make_chanel_target(-1001234567890)
            >>> print(f"Set channel {target.id} as target")
        """
        async with AsyncSession(self.engine) as session:
            target_chanel = await self.get_target_channel()
            for c in target_chanel:
                c.target = False
                session.add(c)

            channel = await session.get(TelegramGroup, channel_id)
            if channel is None:
                raise ItemNotFoundException(
                    f"Cant find group with id {channel_id} in database!"
                )
            channel.target = True
            await session.commit()
            await session.refresh(channel)
            return channel

    async def make_admin(self, user_id: int) -> User:
        """
        Grant administrative privileges to a user.

        Args:
            user_id: The Telegram user ID

        Returns:
            User: The updated user record

        Raises:
            DatabaseError: If the user does not exist

        Examples:
            >>> admin = await db_manager.make_admin(12345678)
            >>> print(f"User {admin.id} is now an admin")
        """
        async with AsyncSession(self.engine) as session:
            user = await session.get(User, user_id)
            if not user:
                raise DatabaseError(
                    "Cant make admin, because there is no user with such ID."
                )
            user.is_admin = True
            await session.commit()
            await session.refresh(user)
            return user

    async def activate_user(self, user_id: int) -> User:
        """
        Activate a user account.

        Args:
            user_id: The Telegram user ID

        Returns:
            User: The updated user record

        Raises:
            DatabaseError: If the user does not exist

        Examples:
            >>> active_user = await db_manager.activate_user(12345678)
            >>> print(f"User {active_user.id} is now active")
        """
        async with AsyncSession(self.engine) as session:
            user = await session.get(User, user_id)
            if not user:
                raise DatabaseError(
                    "Cant activate user, because there is no user with such ID."
                )
            user.is_active = True
            await session.commit()
            await session.refresh(user)
            return user

    async def deactivate_user(self, user_id: int) -> User:
        """
        Deactivate a user account.

        Args:
            user_id: The Telegram user ID

        Returns:
            User: The updated user record

        Raises:
            DatabaseError: If the user does not exist

        Examples:
            >>> inactive_user = await db_manager.deactivate_user(12345678)
            >>> print(f"User {inactive_user.id} is now inactive")
        """
        async with AsyncSession(self.engine) as session:
            user = await session.get(User, user_id)
            if not user:
                raise DatabaseError(
                    "Cant deactivate user, because there is no user with such ID."
                )
            user.is_active = False
            await session.commit()
            await session.refresh(user)
            return user

    async def is_active(self, user_id: int) -> bool:
        """
        Check if a user account is active.

        Args:
            user_id: The Telegram user ID

        Returns:
            bool: True if the user is active, False otherwise

        Raises:
            DatabaseError: If the user does not exist

        Examples:
            >>> is_active = await db_manager.is_active(12345678)
            >>> print(f"User is {'active' if is_active else 'inactive'}")
        """
        async with AsyncSession(self.engine) as session:
            user = await session.get(User, user_id)
            if not user:
                raise DatabaseError(
                    "Cant check user is active, because there is no user with such ID."
                )
            return user.is_active

    async def revoke_admin(self, user_id: int) -> User:
        """
        Revoke administrative privileges from a user.

        Args:
            user_id: The Telegram user ID

        Returns:
            User: The updated user record

        Raises:
            DatabaseError: If the user does not exist

        Examples:
            >>> user = await db_manager.revoke_admin(12345678)
            >>> print(f"User {user.id} is no longer an admin")
        """
        async with AsyncSession(self.engine) as session:
            user = await session.get(User, user_id)
            if not user:
                raise DatabaseError(
                    "Cant make admin, because there is no user with such ID."
                )
            user.is_admin = False
            await session.commit()
            await session.refresh(user)
            return user

    async def is_admin(self, user_id: int) -> bool:
        """
        Check if a user has administrative privileges.

        Args:
            user_id: The Telegram user ID

        Returns:
            bool: True if the user is an admin, False otherwise

        Examples:
            >>> is_admin = await db_manager.is_admin(12345678)
            >>> print(f"User is {'an admin' if is_admin else 'not an admin'}")
        """
        user = await self.get_user(user_id)
        if user:
            return user.is_admin  # type: ignore
        return False

    async def get_all_users(self) -> Sequence[User]:
        """
        Get all registered users.

        Returns:
            Sequence[User]: A sequence of all user records

        Examples:
            >>> users = await db_manager.get_all_users()
            >>> print(f"Total users: {len(users)}")
            >>> admins = [u for u in users if u.is_admin]
            >>> print(f"Admin count: {len(admins)}")
        """
        async with AsyncSession(self.engine) as session:
            query = select(User)
            result = await session.exec(query)
            users = result.all()
            return users

    async def get_phone(self, phone_num: int) -> PhoneWhiteList | None:
        """
        Get a phone number from the whitelist.

        Args:
            phone_num: The phone number to look for

        Returns:
            PhoneWhiteList: The phone whitelist record if found
            None: If the phone number is not in the whitelist

        Examples:
            >>> phone = await db_manager.get_phone(9123456789)
            >>> if phone:
            ...     print(f"Phone {phone.phone} is whitelisted")
            ...     if phone.user:
            ...         print(f"Associated with user {phone.user.id}")
        """
        async with AsyncSession(self.engine) as session:
            phone = await session.get(
                PhoneWhiteList, phone_num, options=[selectinload(PhoneWhiteList.user)]
            )
            return phone

    async def add_phone(self, phone_num: int) -> PhoneWhiteList:
        """
        Add a phone number to the whitelist.

        Args:
            phone_num: The phone number to add

        Returns:
            PhoneWhiteList: The newly created phone whitelist record

        Examples:
            >>> phone = await db_manager.add_phone(9123456789)
            >>> print(f"Added phone {phone.phone} to whitelist")
        """
        async with AsyncSession(self.engine) as session:
            phone = PhoneWhiteList(phone=phone_num)
            session.add(phone)
            await session.commit()
            await session.refresh(phone)
        return phone
