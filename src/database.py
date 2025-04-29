from sqlalchemy.ext.asyncio import create_async_engine
from typing import Union, Sequence
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from settings import settings
from models import User, PhoneWhiteList, TelegramGroup


class DatabaseError(Exception): ...


class ItemNotFoundException(DatabaseError): ...


class DatabaseManager:
    def __init__(self):
        self.engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async def get_user(self, user_id: int) -> Union[User, None]:
        async with AsyncSession(self.engine) as session:
            result = await session.get(User, user_id)
            return result

    async def add_user(self, user_id: int) -> User:
        async with AsyncSession(self.engine) as session:
            user = User(id=user_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def add_chanel(self, chanel_id: int):
        async with AsyncSession(self.engine) as session:
            chanel = TelegramGroup(id=chanel_id)
            session.add(chanel)
            await session.commit()
            await session.refresh(chanel)
            return chanel

    async def delete_chanel(self, chanel_id: int):
        async with AsyncSession(self.engine) as session:
            chanel = TelegramGroup(id=chanel_id)
            await session.delete(chanel)
            await session.commit()
            await session.refresh(chanel)
            return chanel

    async def get_registered_chanels(self):
        async with AsyncSession(self.engine) as session:
            query = select(TelegramGroup)
            chanel = await session.exec(query)
            return chanel.all()

    async def find_target_chanel(self):
        async with AsyncSession(self.engine) as session:
            query = select(TelegramGroup).where(TelegramGroup.target == True)
            chanel = await session.exec(query)
            return chanel.all()

    async def make_chanel_target(self, chanel_id: int):
        async with AsyncSession(self.engine) as session:
            target_chanel = await self.find_target_chanel()
            for c in target_chanel:
                c.target = False
                session.add(c)

            chanel = await session.get(TelegramGroup, chanel_id)
            chanel.target = True
            await session.commit()
            await session.refresh(chanel)
            return chanel

    async def make_admin(self, user_id: int):
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

    async def activate_user(self, user_id: int):
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

    async def deactivate_user(self, user_id: int):
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
        async with AsyncSession(self.engine) as session:
            user = await session.get(User, user_id)
            if not user:
                raise DatabaseError(
                    "Cant check user is active, because there is no user with such ID."
                )
            return user.is_active

    async def revoke_admin(self, user_id: int) -> User:
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
        user = await self.get_user(user_id)
        if user:
            return user.is_admin  # type: ignore
        return False

    async def get_all_users(self) -> Sequence[User]:
        async with AsyncSession(self.engine) as session:
            query = select(User)
            result = await session.exec(query)
            users = result.all()
            return users

    async def get_phone(self, phone_num) -> PhoneWhiteList:
        async with AsyncSession(self.engine) as session:
            return await session.get(PhoneWhiteList, phone_num)

    async def add_phone(self, phone_num) -> PhoneWhiteList:
        async with AsyncSession(self.engine) as session:
            phone = PhoneWhiteList(phone=phone_num)
            await session.add(phone)
            await session.refresh(phone)
            await session.commit()
        return phone
