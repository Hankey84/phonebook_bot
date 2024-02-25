
async def save_number(filename: str, data: dict):
    # Преобразование словаря в строку
    line = ','.join([str(value) for value in data.values()])

    # Запись строки в файл
    async with open(filename, 'a+', encoding='utf-8') as file:
        file.write(line +'\n')
        # file.write(f'{s[:-1]}\n')

async def save_your_number(filename: str, contact):
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
    await save_number(filename, new_contact) # Добавляем новую запись в на файл

async def show_numbers(filename: str):
    pbook=[]
    fields=['surname', 'firstname', 'patronymic', 'phonenumber', 'description']
    async with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            n = line.split(',')
            if n != '': # Проверка на непустую строку
                record = dict(zip(fields, n))
                pbook.append(record)
    return pbook


async def search_records(filename: str, search_query: str):
    pbook=[]
    fields=['surname', 'firstname', 'patronymic', 'phonenumber', 'description']
    async with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            n = line.split(',')
            if n != '': # Проверка на непустую строку
                if search_query.lower().strip() in map(str.lower, n):
                    record = dict(zip(fields, n))
                    pbook.append(record)
    return pbook
