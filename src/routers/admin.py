"""
Admin router module for Telegram group access bot.

This module provides administrative functionality for the bot, including
user management, channel management, and phone whitelist operations.
The router has filters to ensure only administrators can access these functions.
"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from filters import admin_only
from database import DatabaseManager
from service.excel import add_phones_from_file
import keyboards as kb
import states

router = Router()

router.message.filter(admin_only)
router.callback_query.filter(admin_only)


@router.message(F.text == "Отмена")
@router.callback_query(F.data == "cancel")
async def cancel(event: Message | CallbackQuery, state: FSMContext, bot: Bot):
    """
    Universal cancel the current operation and reset state.

    Handles both message with text "Отмена" and callback query with data "cancel".
    If triggered by a callback query, removes the inline keyboard.
    """
    if isinstance(event, CallbackQuery):
        await bot.edit_message_reply_markup(
            chat_id=event.from_user.id,
            message_id=event.message.message_id,
            reply_markup=None,
        )
    await event.answer("Действие отменено")
    await state.clear()


@router.message(F.content_type == ContentType.DOCUMENT)
async def parse_phone_list(
    message: Message, state: FSMContext, bot: Bot, db_manager: DatabaseManager
):
    """
    Process uploaded document for phone numbers.

    Try to extract all phone numbers and add them to the whitelist.
    """
    file_id = message.document.file_id

    phones_list_file = await bot.get_file(file_id)
    dowloaded_file = await bot.download_file(file_path=phones_list_file.file_path)

    try:
        added_phones = await add_phones_from_file(dowloaded_file)
    except:
        logger.warning(f'Error in extracting phones from file {message.document.file_name}')
        await message.answer("При обработке файла возникла ошибка.")
    finally:
        dowloaded_file.close()

    await message.answer(f"В базу данных добавлено {len(added_phones)} телефонов.")


@router.message(Command("select_group"))
async def ask_to_select_target_group(
    message: Message, db_manager: DatabaseManager, bot: Bot, state: FSMContext
):
    """
    Display the list of groups for the admin to select as target.

    Creates and displays a keyboard with available groups that the bot
    can administer.
    """
    kb_w_groups = await kb.get_select_group_kb(db_manager=db_manager, bot=bot)

    await message.answer(
        text="Выберете группу, которую будет администрировать бот.",
        reply_markup=kb_w_groups,
    )
    await state.set_state(states.TargetGroupSelection.target_selected)


@router.callback_query(states.TargetGroupSelection.target_selected)
async def select_target_group(
    callback: CallbackQuery, db_manager: DatabaseManager, state: FSMContext, bot: Bot
):
    """
    Process the selection of a target group.

    Sets the selected group as the target for bot administration
    based on the admin's selection.
    """
    await db_manager.make_channel_target(int(callback.data))
    await callback.answer(text="Целевая группа для администрирования изменена.")
    await state.clear()
