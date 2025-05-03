from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from models import PhoneWhiteListRead
from database import ItemNotFoundException
from service.telegroup import create_invite_link
from database import DatabaseManager


async def answer_registration_succes(
    message: Message, state: FSMContext, db_manager: DatabaseManager, bot: Bot
):
    target_group = await db_manager.get_target_channel()
    link_to_group = await create_invite_link(bot=bot, group_id=target_group[0].id)

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
        raise ItemNotFoundException(f"Cant find phone {phone}")
    return phone.user is not None


async def register_user(user_id: int, db_manager: DatabaseManager):
    await db_manager.add_user(user_id)
    await db_manager.activate_user(user_id)


async def register_user_and_answer(
    message: Message, state: FSMContext, db_manager: DatabaseManager, bot: Bot
):
    await register_user(message.from_user.id, db_manager)
    await answer_registration_succes(message, state, db_manager, bot)


async def bind_phone_to_user(user_id: int, phone_num: int, db_manager: DatabaseManager):
    await db_manager.bind_phone_to_user(user_id, phone_num)


async def user_id_str_to_int(user_id: str) -> int:
    
    return int(user_id)
        