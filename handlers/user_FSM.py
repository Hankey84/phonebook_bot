from aiogram import F, Router, types
# from asyncio import sleep
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import (
    as_list,
    as_marked_section,
    Bold,
)  # Italic, as_numbered_list и тд
import re

# from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard
from file.engine import save_number, search_records, show_numbers

user_FSM_router = Router()
# user_FSM_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

# Главное меню через функцию-конструктор(модуль kbd.reply)
FSM_KB = get_keyboard(
    "Добавить номер",
    "Изменить номер",
    "Удалить номер",
    "Посмотреть",
    "Найти запись",
    "Добавить свой номер 📱",
    "Отправить локацию 🗺️",
    
    placeholder="Выберите действие",
    request_contact=5,
    request_location=6,
    sizes=(3, 2, 2),
)

@user_FSM_router.message(CommandStart()) # Ловим хендлер /start
async def abonent_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=FSM_KB)

# Перехватываем хэндлер для помощи в разных условиях
@user_FSM_router.message(F.text.lower() == "помощь")
@user_FSM_router.message(Command("help"))
async def help_cmd(message: types.Message, state: FSMContext):
    text = as_list(
        as_marked_section(
            Bold("Варианты общения с ботом:"),
            "через команды /",
            "через меню",
            "через инлайн-кнопки",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("В чате нельзя:"),
            "нецензурно выражаться",
            "тыкать куда-попало",
            marker="❌ "
        ),
        sep="\n-------------------------\n",
    )
    current_state = await state.get_state()

    if current_state is None: # Если не в режиме FSM то этот вариант 
        await message.answer(text.as_html())
        await message.answer("<b>Чтобы начать нажмите /start</b>")
    else: # Иначе - другой
        await message.answer("Чтобы отменить нажмите <b>\"отмена\"</b>\nЧтобы вернуться назад - <b>\"назад\"</b>")

# Тут мы выводим записи на экран в виде карточек
@user_FSM_router.message(F.text == "Посмотреть")
async def starting_at_phonebook(message: types.Message):
    await message.answer("<b><u>ОК, вот список абонентов:</u></b>")
    data = await show_numbers('phonebook.txt')
    for record in data:
        message_text = f"<b>Фамилия:</b> {record['surname']}\n" \
                        f"<b>Имя:</b> {record['firstname']}\n" \
                        f"<b>Отчество:</b> {record['patronymic']}\n" \
                        f"<b>Номер телефона:</b> {record['phonenumber']}\n" \
                        f"<b>Описание:</b> {record['description']}"
        await message.answer(message_text)
        # await sleep(1)

@user_FSM_router.message(F.text == "Изменить номер")
async def change_number(message: types.Message):
    await message.answer("ОК, вот список номеров")

# Удаление номера из списка
@user_FSM_router.message(F.text == "Удалить номер")
async def delete_number(message: types.Message):
    await message.answer("Выберите номер(а) для удаления")

# Получаем из меню в хендлер свой контакт и сохраняем его в словарь
@user_FSM_router.message(F.contact)
async def get_contact(message: types.Message):
    await message.answer(f"<b>номер получен</b>")
    # await message.answer(str(message.contact)) # Выводим данные на экран(временно)
    # Раскладываем полученный контакт на составляющие и кладем в словарь
    contact = message.contact
    phone_number = contact.phone_number
    first_name = contact.first_name
    last_name = contact.last_name
    user_id = contact.user_id

    new_contact = {
        'surname': last_name or '',  # Если фамилия отсутствует, используем пустую строку
        'firstname': first_name,
        'patronymic': '',  # Надо подумать позже что с этим делать...
        'phonenumber': phone_number,
        'description': f'ID пользователя: {user_id}'
    }
    await save_number('phonebook.txt', new_contact) # Добавляем новую запись в на файл

@user_FSM_router.message(F.location)
async def get_location(message: types.Message):
    await message.answer(f"локация получена")
    await message.answer(str(message.location))

class SearchState(StatesGroup):
    searching = State()

# Поиск записи по вхождению
@user_FSM_router.message(StateFilter(None), F.text == "Найти запись")
async def search_number(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите данные, которые вы хотите найти (ФИО, номер телефона):", 
        reply_markup=types.ReplyKeyboardRemove()
        )
    await state.set_state(SearchState.searching)

#Ловим данные для состояние searching
@user_FSM_router.message(SearchState.searching, F.text)
async def get_search(message: types.Message, state: FSMContext):

    search_query = message.text # Получаем введенные данные и ищем записи в словаре
    print(type(search_query))
    search_results = await search_records('phonebook.txt', search_query)
    
    if search_results: # Выводим результаты
        for record in search_results:
            message_text = f"<b>Фамилия:</b> {record['surname']}\n" \
                            f"<b>Имя:</b> {record['firstname']}\n" \
                            f"<b>Отчество:</b> {record['patronymic']}\n" \
                            f"<b>Номер телефона:</b> {record['phonenumber']}\n" \
                            f"<b>Описание:</b> {record['description']}"
        await message.answer(message_text, reply_markup=FSM_KB)
    else:
        await message.answer("Ничего не найдено.", reply_markup=FSM_KB)
    await state.clear()

#Код ниже для машины состояний (FSM) для добавления номера

class AddPhonebook(StatesGroup):
    #Шаги состояний
    surname = State()
    firstname = State()
    patronymic = State()
    phonenumber = State()
    description = State()

    texts = {
        'AddPhonebook:surname': 'Введите фамилию заново:',
        'AddPhonebook:firstname': 'Введите имя заново:',
        'AddPhonebook:patronymic': 'Введите отчество заново:',
        'AddPhonebook:phonenumber': 'Введите номер заново:',
        'AddPhonebook:description': 'Этот стейт последний, поэтому...',
    }


#Становимся в состояние ожидания самого первого ввода surname
@user_FSM_router.message(StateFilter(None), F.text == "Добавить номер")
async def add_abonent(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите фамилию абонента", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddPhonebook.surname)

 
#Хендлер отмены и сброса состояния должен быть всегда именно хдесь,
#после того как только встали в состояние номер 1 (элементарная очередность фильтров)
@user_FSM_router.message(StateFilter('*'), Command("отмена"))
@user_FSM_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("<b>Действия отменены</b>", reply_markup=FSM_KB)

#Вернутся на шаг назад (на прошлое состояние)
@user_FSM_router.message(StateFilter('*'), Command("назад"))
@user_FSM_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == AddPhonebook.surname:
        await message.answer('Предыдущего шага нет, или введите фамилию или напишите "отмена"')
        return

    previous = None
    for step in AddPhonebook.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Ок, вы вернулись к прошлому шагу \n {AddPhonebook.texts[previous.state]}")
            return
        previous = step


#Ловим данные для состояние surname и в конце функции меняем состояние на firstname
@user_FSM_router.message(AddPhonebook.surname, F.text)
async def add_surname(message: types.Message, state: FSMContext):
    # Здесь можно сделать какую либо дополнительную проверку
    #и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
    #например:
    if len(message.text) >= 50:
        await message.answer("Название фамилии не должно превышать 50 символов. \n Введите заново")
        return
    
    await state.update_data(surname=message.text)
    await message.answer("Введите имя")
    await state.set_state(AddPhonebook.firstname) # Переводим FSM на 2 стадию

#Хендлер для отлова некорректных вводов для состояния surname
@user_FSM_router.message(AddPhonebook.surname)
async def add_surname2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите правильный текст")


#Ловим данные для состояние firstname и потом меняем состояние на patronymic
@user_FSM_router.message(AddPhonebook.firstname, F.text)
async def add_firstname(message: types.Message, state: FSMContext):
    if len(message.text) >= 50:
        await message.answer("Название имени не должно превышать 50 символов. \n Введите заново")
        return
    await state.update_data(firstname=message.text)
    await message.answer("Введите отчество")
    await state.set_state(AddPhonebook.patronymic) # Переводим FSM на 3 стадию

#Хендлер для отлова некорректных вводов для состояния firstname
@user_FSM_router.message(AddPhonebook.firstname)
async def add_firstname2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите правильный текст")


#Ловим данные для состояние patronymic и потом меняем состояние на phonenumber
@user_FSM_router.message(AddPhonebook.patronymic, F.text)
async def add_patronymic(message: types.Message, state: FSMContext):
    if len(message.text) >= 50:
        await message.answer("Название отчества не должно превышать 50 символов. \n Введите заново")
        return
    
    await state.update_data(patronymic=message.text)
    await message.answer("Введите номер телефона")
    await state.set_state(AddPhonebook.phonenumber) # Переводим FSM на 4 стадию

#Хендлер для отлова некорректных ввода для состояния patronymic
@user_FSM_router.message(AddPhonebook.patronymic)
async def add_patronymic2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите правильный текст")


#Ловим данные для состояние phonenumber и потом меняем состояние на description
@user_FSM_router.message(AddPhonebook.phonenumber, F.text)
async def add_phonenumber(message: types.Message, state: FSMContext):
    try:
        phone_pattern = re.compile(r"^((8|\+?)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$")
        # int(message.text)
        if not phone_pattern.match(message.text):
            await message.answer("Введите корректный номер телефона")
            return
    except ValueError:
        await message.answer("Введите корректный номер телефона")
        return
    
    await state.update_data(phonenumber=message.text)
    await message.answer("Введите описание абонента")
    await state.set_state(AddPhonebook.description) # Переводим FSM на 5 стадию

#Хендлер для отлова некорректных ввода для состояния phonenumber
@user_FSM_router.message(AddPhonebook.phonenumber)
async def add_phonenumber2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите корректый номер телефона")


#Ловим данные для состояние description и потом выходим из состояний
@user_FSM_router.message(AddPhonebook.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("<b>Абонент добавлен</b>", reply_markup=FSM_KB)
    data = await state.get_data()
    # await message.answer(str(data)) # Тестовый вывод абонента
    await save_number('phonebook.txt', data)
    await state.clear()

#Хендлер для отлова некорректных ввода для состояния descripton
@user_FSM_router.message(AddPhonebook.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте описание")
