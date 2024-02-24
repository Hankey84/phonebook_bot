from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f

from kbds.reply import get_keyboard
user_private_router = Router()
# user_private_router.message.filter(ChatTypeFilter(['Private']))

# @user_private_router.message(CommandStart())
# async def start_cmd(message: types.Message):
#     await message.answer(
#         "Привет, я виртуальный помощник",
#         reply_markup=get_keyboard(
#             "Меню",
#             "Помощь",
#             "Отправить номер 📱",
#             "Отправить локацию 🗺️",
#             placeholder="Что вас интересует?",
#             request_contact=2,
#             request_location=3,
#             sizes=(2, 2)
#         ),
#     )

# @user_private_router.message(F.text.lower() == "меню")
@user_private_router.message(or_f(Command("menu"), (F.text.lower() == "меню")))
async def menu_cmd(message: types.Message):
    await message.answer('Вот меню: ')

@user_private_router.message(F.text.lower() == "помощь")
@user_private_router.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer("Помощь:")


# @user_private_router.message(F.contact)
# async def get_contact(message: types.Message):
#     await message.answer(f"номер получен")
#     await message.answer(str(message.contact))

# @user_private_router.message(F.location)
# async def get_location(message: types.Message):
#     await message.answer(f"локация получена")
#     await message.answer(str(message.location))