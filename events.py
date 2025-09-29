from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from event_display import show_events, show_event_details
from user_registration import request_contact

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик /start с меню"""
    # Проверяем и запрашиваем контакт, если нужно
    await request_contact(update, context)
    # Меню будет показано только после обработки контакта

async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /events"""
    await show_events(update, context)

# Обработчик для возврата на главную по кнопке "Домой"
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки 'Домой'"""
    query = update.callback_query
    if query:
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("Афиша мероприятий", callback_data='show_events')],
            [InlineKeyboardButton("Регистрация", callback_data='start_register')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text('Привет! Это бот университета. Выберите действие:', reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton("Афиша мероприятий", callback_data='show_events')],
            [InlineKeyboardButton("Регистрация", callback_data='start_register')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Привет! Это бот университета. Выберите действие:', reply_markup=reply_markup)

# Экспорт обработчиков
start = CommandHandler("start", start)
events_command = CommandHandler("events", events_command)
show_events_handler = CallbackQueryHandler(show_events, pattern='^show_events$')
show_event_details_handler = CallbackQueryHandler(show_event_details, pattern='^event_details_.*$')
start_handler = CallbackQueryHandler(start_callback, pattern='^start$')