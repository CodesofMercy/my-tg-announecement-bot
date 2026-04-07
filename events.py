"""
Main event handlers: /start, menu navigation, callback routing.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

import config
from user_registration import request_contact, handle_contact
from user_handler import get_user_data


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start — check contact, then show menu."""
    user_id = update.effective_user.id
    has_data = await get_user_data(user_id)
    if not has_data:
        await request_contact(update, context)
        return
    await start_callback(update, context)


async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /events — show event list."""
    from event_display import show_events
    await show_events(update, context)


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main menu after contact is confirmed."""
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or ""

    keyboard = [
        [InlineKeyboardButton(config.BTN_EVENTS, callback_data="show_events")],
        [InlineKeyboardButton(config.BTN_PROGRAMS, callback_data="show_programs")],
        [InlineKeyboardButton(config.BTN_MANAGER, callback_data="manager")],
        [InlineKeyboardButton(config.BTN_FAQ, callback_data="faq")],
    ]

    # Admin button if applicable
    if user_id in config.ADMIN_IDS:
        keyboard.append([InlineKeyboardButton(config.BTN_ADMIN, callback_data="admin_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome = config.BOT_WELCOME_TEXT

    query = update.callback_query
    if query:
        await query.answer()
        await _safe_edit_or_reply(query.message, f"👋 Привет, {first_name}!\n\n{welcome}", reply_markup)
    elif update.message:
        await update.message.reply_text(f"👋 Привет, {first_name}!\n\n{welcome}", reply_markup=reply_markup)


# ── Handlers for main.py registration ────────────────────────────
start_handler = CallbackQueryHandler(start_callback, pattern="^start$")
manager_button_handler = CallbackQueryHandler(_manager_redirect, pattern="^manager$")
faq_button_handler = CallbackQueryHandler(_faq_redirect, pattern="^faq$")


async def _manager_redirect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redirect /manager button to support handler."""
    from support import manager_handler
    await manager_handler(update, context)


async def _faq_redirect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redirect /faq button to support handler."""
    from support import faq_handler
    await faq_handler(update, context)


async def _safe_edit_or_reply(message, text: str, reply_markup):
    import telegram.error
    try:
        await message.edit_text(text, parse_mode="HTML", reply_markup=reply_markup)
    except telegram.error.BadRequest as e:
        err = str(e).lower()
        if "not modified" not in err:
            try:
                await message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
            except Exception:
                pass
    except Exception:
        pass
