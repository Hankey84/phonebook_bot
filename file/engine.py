
async def save_number(filename: str, data: dict):
    # Преобразование словаря в строку
    line = ','.join([str(value) for value in data.values()])

    # Запись строки в файл
    with open(filename, 'a+', encoding='utf-8') as file:
        file.write(line +'\n')
        # file.write(f'{s[:-1]}\n')


async def show_numbers(filename: str):
    pbook=[]
    fields=['surname', 'firstname', 'patronymic', 'phonenumber', 'description']
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            n = line.split(',')
            if n != '': # Проверка на непустую строку
                record = dict(zip(fields, n))
                pbook.append(record)
    return pbook


async def search_records(filename: str, search_query: str):
    pbook=[]
    fields=['surname', 'firstname', 'patronymic', 'phonenumber', 'description']
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            n = line.split(',')
            if n != '': # Проверка на непустую строку
                if search_query.lower().strip() in map(str.lower, n):
                    record = dict(zip(fields, n))
                    pbook.append(record)
    return pbook
