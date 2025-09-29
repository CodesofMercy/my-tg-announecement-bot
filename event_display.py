from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from event_data import get_event_data

async def show_events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ списка мероприятий"""
    query = update.callback_query
    events = get_event_data()
    
    if not events:
        text = "Афиша пуста. Добавьте мероприятия в events.xlsx."
    else:
        text = "Афиша мероприятий:\n"
        keyboard = []
        for i, event in enumerate(events):
            event_id = f"event_details_{i}"
            text += f"{i+1}. {event['Название']} - {event['Цена']} - {event['Дата']}\n"
            keyboard.append([InlineKeyboardButton(event['Название'], callback_data=event_id)])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    if query:
        await query.answer()
        await query.message.edit_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def show_event_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ подробной информации о мероприятии"""
    query = update.callback_query
    if query:
        await query.answer()
        event_id = query.data.replace('event_details_', '')
        events = get_event_data()
        if 0 <= int(event_id) < len(events):
            event = events[int(event_id)]
            text = (
                f"**{event['Название']}**\n"
                f"Дата: {event['Дата']}\n"
                f"Время: {event['Время']}\n"
                f"Место: {event['Место']}\n"
                f"Цена: {event['Цена']}\n"
                f"Описание: {event['Описание']}\n\n"
                f"Готовы зарегистрироваться?"
            )
            keyboard = [
                [InlineKeyboardButton("Регистрация", callback_data=f'register_{event_id}')],
                [InlineKeyboardButton("Назад", callback_data='show_events')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')