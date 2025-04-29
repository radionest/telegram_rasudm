from typing import Callable, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.dispatcher.middlewares.data import MiddlewareData
from aiogram.types import Message, CallbackQuery

from database import DatabaseManager
from models import User


class UserMiddlewareData(MiddlewareData):
    """Class for middleware data injection."""

    user: User


class GetUserMiddleware(BaseMiddleware):
    """
    Middleware that fetches the user from the database and adds it to the handler data.

    This middleware intercepts incoming events (messages or callback queries),
    extracts the user ID from the event, fetches the corresponding user record
    from the database, and adds it to the handler's data dictionary.
    """

    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialize the middleware with a database manager.

        Args:
            db_manager: Database manager instance used to fetch user data
        """
        self.db = db_manager
        super().__init__()

    async def __call__(
        self,
        handler: Callable[  # type: ignore
            [Union[Message, CallbackQuery], UserMiddlewareData], Awaitable[Any]
        ],
        event: Union[Message, CallbackQuery],  # type: ignore
        data: UserMiddlewareData,  # type: ignore
    ) -> Any:
        """
        Process the incoming event before passing it to the handler.

        Args:
            handler: The next handler in the processing chain
            event: The incoming event (message or callback query)
            data: Dictionary for passing data between middleware and handlers

        Returns:
            The result of the next handler's execution

        Note:
            This middleware extracts the user ID from the event if available,
            fetches the corresponding user from the database, and adds it to
            the data dictionary with the key "user". If no user ID is found,
            None is stored instead.
        """
        user_id = event.from_user and event.from_user.id
        if user_id and (user := await self.db.get_user(user_id)):
            data["user"] = user
        else:
            data["user"] = None
        
        return await handler(event, data)
        

