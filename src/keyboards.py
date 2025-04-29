"""
Keyboards module for Telegram bot UI components.

This module provides functions to create various keyboard interfaces for the bot,
including command menus, group selection keyboards, and agreement keyboards.

Attributes:
    None
"""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommandScopeChat,
    BotCommand,
)
from aiogram import Bot

from database import DatabaseManager


async def create_menu(bot: Bot, user_id: int, is_admin: bool) -> None:
    """
    Create and set a custom command menu for a specific user.

    Creates a personalized command menu with different commands based on whether
    the user has administrative privileges. Sets the created menu for the specific
    user's chat.

    Args:
        bot: The Bot instance to set commands for
        user_id: The Telegram user ID to create the menu for
        is_admin: Whether the user has administrative privileges

    Returns:
        None
    """
    command_list = [
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/grouplink", description="Получить ссылку на группу"),
    ]
    if is_admin:
        command_list.extend(
            [
                BotCommand(
                    command="/select_group",
                    description="Выбрать группу или канал за доступ к которой отвечает бот.",
                )
            ]
        )
    scope = BotCommandScopeChat(chat_id=user_id)
    await bot.set_my_commands(commands=command_list, scope=scope)


async def get_select_group_kb(
    db_manager: DatabaseManager, bot: Bot
) -> InlineKeyboardMarkup:
    """
    Create an inline keyboard for selecting a Telegram group or channel.

    Fetches all registered channels or groups from the database, retrieves
    their information using the bot API, and creates an inline keyboard with
    buttons for each group and a cancel option.

    Args:
        db_manager: Database manager instance to fetch registered channels
        bot: The Bot instance to get chat information

    Returns:
        InlineKeyboardMarkup: The inline keyboard with group selection buttons
    """
    chanels = await db_manager.get_registered_chanels()
    registered_groups = [await bot.get_chat(chat_id=channel.id) for channel in chanels]
    group_buttons = [
        [
            InlineKeyboardButton(text=group.full_name, callback_data=str(group.id))
            for group in registered_groups
        ]
    ]

    group_buttons.append([InlineKeyboardButton(text="Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(
        inline_keyboard=group_buttons,
        one_time_keyboard=True,
        resize_keyboard=True,
    )


def get_agreement_kb() -> ReplyKeyboardMarkup:
    """
    Create a reply keyboard for user agreement confirmation.

    Creates a keyboard with two buttons: one to agree and share contact information,
    and another to decline. This keyboard is used during the user registration process
    to obtain consent for phone number verification.

    Args:
        None

    Returns:
        ReplyKeyboardMarkup: A keyboard with agree/disagree buttons
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Согласен", request_contact=True),
                KeyboardButton(text="Не согласен"),
            ]
        ],
        one_time_keyboard=True,
        resize_keyboard=True,
        is_persistent=True,
    )
