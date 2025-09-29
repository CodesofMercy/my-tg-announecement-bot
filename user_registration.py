from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters
from user_handler import save_user_to_excel, is_user_registered

async def request_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка сообщения с запросом контакта."""
    user_id = update.effective_user.id
    if is_user_registered(user_id):
        if update.callback_query:
            await update.callback_query.edit_message_text("Вы уже зарегистрированы в боте!")
        else:
            await update.message.reply_text("Вы уже зарегистрированы в боте!")
        # Добавляем вызов меню
        from events import start_callback
        await start_callback(update, context)
        return

    text = "Мы хотим вас запомнить и будем рады, если вы поделитесь с нами сразу своим контактом, нажав на кнопку ниже."
    keyboard = [[KeyboardButton("Поделиться контактом", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка полученного контакта и сохранение."""
    contact = update.message.contact
    user_data = {
        'user_id': contact.user_id,
        'first_name': contact.first_name,
        'last_name': contact.last_name or '',
        'phone_number': contact.phone_number,
        'username': update.effective_user.username or ''
    }
    save_user_to_excel(user_data)
    await update.message.reply_text("Спасибо! Ваш контакт сохранён. Теперь вы зарегистрированы в боте и не нужно вводить данные каждый раз.")
    # Убираем клавиатуру и показываем меню
    await update.message.reply_text("Готовы к действиям?", reply_markup=ReplyKeyboardMarkup([]))
    try:
        from events import start_callback
        await start_callback(update, context)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при показе меню: {str(e)}. Попробуйте /start.")