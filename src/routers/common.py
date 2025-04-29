from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, Message, ChatMemberUpdated
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    IS_NOT_MEMBER,
    IS_MEMBER,
)

from states import RegisterUser
from models import User
from keyboards import create_menu
from database import DatabaseManager

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user: User, bot: Bot) -> None:
    """Start command handler - register user if not registered"""
    await create_menu(bot=bot, is_admin=user.is_admin, user_id=user.id)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER)
)
async def save_group(event: ChatMemberUpdated, db_manager: DatabaseManager):
    await db_manager.add_channel(event.chat.id)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER>>IS_NOT_MEMBER)
)
async def delete_group(event: ChatMemberUpdated, db_manager: DatabaseManager):
    await db_manager.delete_channel(event.chat.id)

