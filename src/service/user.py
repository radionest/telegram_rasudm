from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from models import PhoneWhiteListRead
from database import ItemNotFoundException
from service.telegroup import create_invite_link
from database import DatabaseManager
from exceptions import InvalidInputError

async def user_id_str_to_int(user_id: str) -> int:
    
    return int(user_id)



async def delete_user(user_id: int | str, db_manager: DatabaseManager):
    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except ValueError:
            raise InvalidInputError('User id should be integer.')
            
    await db_manager.delete_user(user_id=user_id)        

async def make_admin(user_id: int | str, db_manager: DatabaseManager):
    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except ValueError:
            raise InvalidInputError('User id should be integer.')
            
    await db_manager.make_admin(user_id=user_id)