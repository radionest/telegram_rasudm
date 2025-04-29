from loguru import logger

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ChatJoinRequest
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext

from database import DatabaseManager
from exceptions import RestrictedAccessError
from states import RegisterUser
from keyboards import get_agreement_kb
from service.registration import (
    answer_registration_succes,
    is_another_user_registered,
    is_phone_in_whitelist,
)
from service.telegroup import approve_user_invite
from commons import TEXT_CALL_ADMIN, TEXT_AGREEMENT
from filters import FilterIsNotRegistered


router = Router()
db_manager = DatabaseManager()


@router.message(FilterIsNotRegistered())
async def give_agreement(message: Message, state: FSMContext):
    await message.answer(text=TEXT_AGREEMENT, reply_markup=get_agreement_kb())
    await state.set_state(RegisterUser.wait_agreement)


@router.message(RegisterUser.wait_agreement, F.text == "Не согласен")
async def ask_to_register(message: Message, state: FSMContext) -> None:
    """Start user registration process"""
    await message.answer(
        "К сожалению мы не можем в автоматическом режиме зарегистрировать вас в группе без номера телефона. \n"
        + TEXT_CALL_ADMIN
    )

    await state.clear()


@router.message(RegisterUser.wait_agreement, F.contact)
async def register_user(
    message: Message, state: FSMContext, db_manager: DatabaseManager
) -> None:
    """Register user"""
    phone = int(message.contact.phone_number[-10:])
    user_id = message.from_user
    if not await is_phone_in_whitelist(phone, db_manager):
        logger.warning(f"""User with id {user_id} try to register on phone {phone}. \n
                       No such phone in database.""")
        await message.answer(
            """Такой номер не зарегистрирован. Если вы действующий член зайдите в личный кабинет на сайте общества.\n
            Укажите ваш номер телефона в соответствующем поле. После этого обратитесь к администратору.
            """
        )
        await state.clear()
        return
    if await is_another_user_registered(phone, db_manager):
        phone_instance = await db_manager.get_phone(phone)
        logger.warning(f"""User with id {user_id} try to register on phone {phone}. \n
                       But this phone number is already registered on user id {phone_instance.user.id}""")

        await message.answer(
            """По такому номеру уже зарегистрирован другой пользователь.
            Мы не знаем как это произошло. Возможно у вас к этому номеру был привязан другой телеграмм-аккаунт.
            Подтвердите, что вы хотите зарегистрироваться в группе с этого аккаунта.
            """
        )
        await state.set_data({"phone": phone})
        await state.set_state(RegisterUser.waiting_phone_changed_user)
        return
    else:
        await answer_registration_succes(message, state)


@router.message(RegisterUser.waiting_phone_changed_user)
async def renew_user_phone(message: Message, state: FSMContext):
    match message:
        case "Да":
            await answer_registration_succes(message, state)
        case "Нет":
            await message.answer(
                "Хорошо. Вы можете продолжать пользоваться группой с ранее зарегистрированного аккаунта."
            )
        case _:
            await message.answer("Вы должны ответить либо **Да**, либо **Нет**.")
    state.clear()


@router.chat_join_request()
async def approve_chat_join_request(
    update: ChatJoinRequest, bot: Bot, db_manager: DatabaseManager
):
    target_group = await db_manager.get_target_channel()
    if update.chat.id != target_group.id:
        return
    try:
        await approve_user_invite(
            bot,
            user_id=update.from_user.id,
            group_id=update.chat.id,
            db_manager=db_manager,
        )
    except RestrictedAccessError:
        if update.user_chat_id:
            await bot.send_message(
                chat_id=update.user_chat_id,
                text="Я не могу принять вас в группу так как ваш номер телефона не зарегистрирован. Обратитесь к администратору. Контакты администратора есть в разделе /help.",
            )


@router.message(Command("grouplink"))
async def give_link_to_group(
    message: Message, bot: Bot, db_manager: DatabaseManager, state: FSMContext
):
    await answer_registration_succes(
        message=message, db_manager=db_manager, bot=bot, state=state
    )
