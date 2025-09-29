from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from excel_handler import save_to_excel
from payment_handler import send_payment_button
from user_handler import is_user_registered, get_users

# Состояния для ConversationHandler
NAME, COMPANY, EMAIL, PHONE = range(4)

async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало регистрации (шаг 1: ФИО или пропуск, если контакт есть) с предупреждением и кнопкой отмены"""
    query = update.callback_query
    if query:
        await query.answer()
        context.user_data['event'] = query.data.replace('register_', '')  # Сохраняем событие
    else:
        context.user_data['event'] = 'manual_register'

    user_id = update.effective_user.id
    if is_user_registered(user_id):
        users = get_users()
        for user in users:
            if user.get('user_id') == user_id:
                context.user_data['name'] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or 'Не указано'
                context.user_data['phone'] = user.get('phone_number', '')
                break
        # Пропускаем шаг ФИО, переходим к компании
        keyboard = [[InlineKeyboardButton("Отмена", callback_data='cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if query:
            await query.message.edit_text('Введите название компании:', reply_markup=reply_markup)
        else:
            await update.message.reply_text('Введите название компании:', reply_markup=reply_markup)
        return COMPANY
    else:
        text = 'Регистрация на событие. Введите ваше ФИО.\n(Для отмены введите /cancel или нажмите "Отмена")'
        keyboard = [[InlineKeyboardButton("Отмена", callback_data='cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if query:
            await query.message.edit_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
        return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение ФИО"""
    context.user_data['name'] = update.message.text.strip()
    keyboard = [[InlineKeyboardButton("Отмена", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Введите название компании:', reply_markup=reply_markup)
    return COMPANY

async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение компании"""
    context.user_data['company'] = update.message.text.strip()
    keyboard = [[InlineKeyboardButton("Отмена", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Введите email:', reply_markup=reply_markup)
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение email с проверкой"""
    email = update.message.text.strip()
    if len(email) < 8 or '@' not in email or '.' not in email:
        keyboard = [[InlineKeyboardButton("Отмена", callback_data='cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Неверный формат email (минимум 8 символов, должен содержать @ и .). Попробуйте ещё раз.', reply_markup=reply_markup)
        return EMAIL
    context.user_data['email'] = email
    keyboard = [[InlineKeyboardButton("Отмена", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Введите номер телефона:', reply_markup=reply_markup)
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение телефона с проверкой и завершение"""
    phone = update.message.text.strip()
    if not phone.isdigit() or len(phone) < 10:
        if not context.user_data.get('phone'):  # Если телефон из контакта нет, проверяем ввод
            keyboard = [[InlineKeyboardButton("Отмена", callback_data='cancel')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('Неверный формат телефона (только цифры, минимум 10). Попробуйте ещё раз.', reply_markup=reply_markup)
            return PHONE
    else:
        context.user_data['phone'] = phone
    
    # Собираем данные для сохранения
    data = {
        'event': context.user_data.get('event', ''),
        'name': context.user_data.get('name', ''),
        'company': context.user_data.get('company', ''),
        'email': context.user_data.get('email', ''),
        'phone': context.user_data.get('phone', '')  # Используем телефон из контекста (из контакта или ввода)
    }
    
    # Сохранение в Excel
    from excel_handler import save_to_excel
    save_to_excel(data)
    
    # Отправка кнопки оплаты
    await send_payment_button(update, context)
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена регистрации с возвратом на главную"""
    query = update.callback_query
    if query:
        await query.answer()
        await query.message.edit_text('Регистрация отменена. Вы вернулись на главную.')
        # Вызываем меню /start с правильным контекстом
        from events import start_callback
        await start_callback(update, context)
    else:
        await update.message.reply_text('Регистрация отменена. Вы вернулись на главную.')
        # Вызываем меню /start с правильным контекстом
        from events import start_callback
        await start_callback(update, context)
    return ConversationHandler.END

# ConversationHandler для регистрации с настройкой per_message
conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('register', register_start),
        CallbackQueryHandler(register_start, pattern='^(start_register|register_.*)$')
    ],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)]
    },
    fallbacks=[CommandHandler('cancel', cancel), CallbackQueryHandler(cancel, pattern='^cancel$')],
    per_message=False
)