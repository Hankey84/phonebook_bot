import asyncio, logging, os

from aiogram import Bot, Dispatcher,types
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv()) # Загружаем наш токен из .env

from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.user_FSM import user_FSM_router

from common.bot_cmds_lst import private


ALLOWED_UPDATES = ['message, edited_message']

bot = Bot(token = os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
# bot.my_admins_list = []
dp = Dispatcher()


dp.include_router(user_FSM_router)
# dp.include_router(user_private_router)
dp.include_router(user_group_router)
    

async def main():
    logging.basicConfig(level=logging.INFO)
    
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats()) # Для удаления меню из бота
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


if __name__ == '__main__':
    asyncio.run(main())
