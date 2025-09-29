import openpyxl
import os

def save_to_excel(data):
    """Сохранение данных в Excel таблицу."""
    file_path = 'registrations.xlsx'
    
    # Загружаем существующий файл или создаём новый
    if os.path.exists(file_path):
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
    else:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['Event', 'Name', 'Company', 'Email', 'Phone'])  # Заголовки

    # Добавляем новую строку
    sheet.append([data['event'], data['name'], data['company'], data['email'], data['phone']])
    workbook.save(file_path)