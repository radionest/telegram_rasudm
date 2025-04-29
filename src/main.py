import asyncio
from zoneinfo import ZoneInfo


from aiogram import Bot, Dispatcher

from service.logger import setup_logging, logger
from database import DatabaseManager
from settings import settings
from middlewares import GetUserMiddleware
from routers import admin, registration, common

setup_logging(settings.LOG_LEVEL)

MOSCOW_TZ = ZoneInfo("Europe/Moscow")

bot_instance = Bot(token=settings.BOT_TOKEN)
db_manager = DatabaseManager()

dp = Dispatcher(db_manager=db_manager)


dp.message.outer_middleware(GetUserMiddleware(db_manager=db_manager))
dp.callback_query.outer_middleware(GetUserMiddleware(db_manager=db_manager))

dp.include_router(admin.router)
dp.include_router(registration.router)
dp.include_router(common.router)


async def main() -> None:
    """Run bot."""
    logger.info('Creating default superadmin....')

    default_admin = await db_manager.get_user(settings.BOT_ADMIN_ID)
    if not default_admin:
        default_admin = await db_manager.add_user(user_id=settings.BOT_ADMIN_ID)
    if not default_admin.is_admin:
        await db_manager.make_admin(default_admin.id)
    if not default_admin.is_active:
        await db_manager.activate_user(default_admin.id)
    logger.info('Superadmin created')
    
    logger.info('Starting bot')
    
    await dp.start_polling(bot_instance)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
