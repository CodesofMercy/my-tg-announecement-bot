"""
User registration — request phone contact, save to Sheets/Excel.
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters
from user_handler import save_user_to_gsheets, get_user_data
import logging

logger = logging.getLogger(__name__)


async def request_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a request for phone contact if user not registered."""
    user_id = update.effective_user.id
    if await get_user_data(user_id):
        # Already registered — proceed to menu
        from events import start_callback
        await start_callback(update, context)
        return

    text = "Мы хотим вас запомнить и будем рады, если вы поделитесь контактом, нажав кнопку ниже."
    keyboard = [[KeyboardButton("Поделиться контактом", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    query = update.callback_query
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the shared contact and save user data."""
    contact = update.message.contact
    if not contact:
        return

    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or ""
    last_name = update.effective_user.last_name or ""
    username = update.effective_user.username or ""
    phone = contact.phone_number or ""

    user_data = {
        "user_id": str(user_id),
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone,
        "username": username,
    }

    await save_user_to_gsheets(user_data)

    # Remove reply keyboard
    await update.message.reply_text(
        f"Спасибо, {first_name}! Мы вас запомнили.",
        reply_markup=ReplyKeyboardMarkup([], resize_keyboard=True),
    )

    # Show main menu
    from events import start_callback
    await start_callback(update, context)


request_contact_handler = MessageHandler(
    filters.CONTACT, handle_contact
)
