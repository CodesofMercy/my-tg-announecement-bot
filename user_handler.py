import openpyxl
import os

def save_user_to_excel(user_data):
    """Сохранение данных пользователя в Excel."""
    file_path = 'users.xlsx'
    
    # Загружаем существующий файл или создаём новый
    if os.path.exists(file_path):
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
    else:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['user_id', 'first_name', 'last_name', 'phone_number', 'username'])  # Заголовки

    # Добавляем новую строку
    sheet.append([
        user_data.get('user_id', ''),
        user_data.get('first_name', ''),
        user_data.get('last_name', ''),
        user_data.get('phone_number', ''),
        user_data.get('username', '')
    ])
    workbook.save(file_path)

def get_users():
    """Получение списка пользователей из Excel."""
    file_path = 'users.xlsx'
    users = []
    
    if os.path.exists(file_path):
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        headers = [cell.value for cell in sheet[1]]  # Первая строка — заголовки
        for row in sheet.iter_rows(min_row=2, values_only=True):
            user = dict(zip(headers, row))
            users.append(user)
    return users

def is_user_registered(user_id):
    """Проверка, зарегистрирован ли пользователь по user_id."""
    users = get_users()
    for user in users:
        if user.get('user_id') == user_id:
            return True
    return False