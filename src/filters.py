from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import DatabaseManager
from states import RegisterUser

from models import User


# Admin check filter
async def admin_only(msg: Any, user: User) -> bool:
    """Filter to check if user is admin.
    user is taken from outer middleware.
    """
    return user and user.is_admin or False


# Active user check filter
async def active_only(user: User) -> bool:
    """Filter to check if user is admin.
    user is taken from outer middleware.
    """
    return user and user.is_active or False


class FilterIsNotRegistered(BaseFilter):
    async def __call__(self, msg: Message, user: User, state: FSMContext) -> bool:
        if user and user.is_active:
            return False
        if await state.get_state() in RegisterUser:
            return False
        return True
