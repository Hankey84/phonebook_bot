from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f

user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Привет, я чат-бот. Чем могу помочь?')

# @user_private_router.message(F.text.lower() == "меню")
@user_private_router.message(or_f(Command("menu"), (F.text.lower() == "меню")))
async def menu_cmd(message: types.Message):
    await message.answer('Вот меню: ')

@user_private_router.message(F.text.lower() == "помощь")
@user_private_router.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer("Помощь:")