from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from models import PhoneWhiteListRead
from exceptions import NotFound
from service.telegroup import create_invite_link
from settings import settings
from database import DatabaseManager


async def answer_registration_succes(message: Message, state: FSMContext, db_manager: DatabaseManager, bot: Bot):
    target_group = await db_manager.find_target_chanel()
    link_to_group = await create_invite_link(
        bot=bot, 
        group_id=target_group[0].id
        )

    await message.answer(
        f"""
        Вы успешно зарегистрированы!
        Пройдите по этой ссылке {link_to_group}
        """,
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()


async def is_phone_in_whitelist(phone: int, db_manager: DatabaseManager): 
    return await db_manager.get_phone(phone) is not None


async def is_another_user_registered(phone: int, db_manager: DatabaseManager):
    phone: PhoneWhiteListRead | None = await db_manager.get_phone(phone)
    if not phone:
        raise NotFound(f"Cant find phone {phone}")
    return phone.user is not None
