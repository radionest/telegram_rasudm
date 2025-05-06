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
from filters import active_only
from routers.registration import give_agreement

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user: User, bot: Bot) -> None:
    """Start command handler - register user if not registered"""
    if user:
        await create_menu(bot=bot, is_admin=user.is_admin, user_id=user.id)
    if not await active_only(user):
        await give_agreement(message, state)


@router.message(Command("id"))
async def give_user_id(message: Message) -> None:
    await message.answer(text=f"Ваш ID {message.from_user.id}")


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER)
)
async def save_group(event: ChatMemberUpdated, db_manager: DatabaseManager):
    await db_manager.add_channel(event.chat.id)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> IS_NOT_MEMBER)
)
async def delete_group(event: ChatMemberUpdated, db_manager: DatabaseManager):
    await db_manager.delete_channel(event.chat.id)
