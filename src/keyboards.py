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
