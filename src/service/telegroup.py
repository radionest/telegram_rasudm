from loguru import logger

from aiogram import Bot
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner
from aiogram.utils.chat_member import ADMINS, MEMBERS

from settings import settings
from database import DatabaseManager

from exceptions import RestrictedAccessError


async def bot_is_group_admin(bot: Bot, group_id: int) -> bool:
    bot_member = await bot.get_chat_member(chat_id=group_id, user_id=bot.id)
    return isinstance(bot_member, ADMINS)


async def is_user_in_group(bot: Bot, user_id: int, group_id: int) -> bool:
    member = await bot.get_chat_member(chat_id=group_id, user_id=user_id)
    return isinstance(member, MEMBERS)


async def create_invite_link(bot: Bot, group_id: int) -> str:
    link = await bot.create_chat_invite_link(
        chat_id=group_id,
        name="группа РОСУДМ",
        expire_date=None,
        creates_join_request=True,
    )
    return link.invite_link


async def approve_user_invite(
    bot: Bot, user_id: int, group_id: int, db_manager: DatabaseManager
) -> None:
    if not db_manager.is_active(user_id):
        raise RestrictedAccessError(
            f"RESTRICTED ACCESS! User with id {user_id} try to join group via link of another user."
        )
    logger.info(f"User with id {user_id} joined group.")
    await bot.approve_chat_join_request(chat_id=group_id, user_id=user_id)
