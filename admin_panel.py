"""
Admin panel — broadcast, FAQ management, reminders, user stats.

Usage: /admin — shows admin menu if user ID is in config.ADMIN_IDS.
"""
import os
import json
import logging
from datetime import datetime
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)

import config
from reminder import get_upcoming_events, get_registered_users, send_reminder_to_event
from support import load_faq, save_faq

logger = logging.getLogger(__name__)

# Menu states
ADMIN_MENU, ADD_ADMIN, BROADCAST, REMINDER_EVENT, FAQ_MANAGE, FAQ_EDIT, FAQ_CONFIRM = range(7)

# ── Admin list (from env) ─────────────────────────────────────────
def get_admin_ids() -> List[int]:
    """Return list of admin Telegram user IDs from config."""
    return config.ADMIN_IDS


def is_admin(user_id: int) -> bool:
    """Check if user_id has admin rights."""
    return user_id in get_admin_ids()


# ── Admin panel handlers ──────────────────────────────────────────
def get_admin_handler():
    """Return a CommandHandler for /admin."""
    return CommandHandler("admin", admin_start)


async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("У вас нет прав администратора.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⏰ Напоминания", callback_data="admin_reminder")],
        [InlineKeyboardButton("❓ Управление FAQ", callback_data="admin_faq")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Панель администратора:", reply_markup=reply_markup)


async def admin_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    events = await get_upcoming_events()
    upcoming_names = "\n".join(f"  • {e['name']} ({e['date']})" for e in events[:10])
    text = f"📊 Статистика\n\nПредстоящие мероприятия:\n{upcoming_names or '  нет'}\n"
    text += "\nЗарегистрированные пользователи: (см. Google Sheet или Excel)"
    keyboard = [[InlineKeyboardButton("Назад", callback_data="admin_menu")]]
    await _safe_edit(query, text, InlineKeyboardMarkup(keyboard))


async def admin_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "📢 Рассылка\n\nВведите текст для рассылки всем пользователям:"
    keyboard = [[InlineKeyboardButton("Отмена", callback_data="admin_menu")]]
    await _safe_edit(query, text, InlineKeyboardMarkup(keyboard))
    return BROADCAST


async def admin_broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["broadcast_text"] = text
    keyboard = [
        [InlineKeyboardButton("✅ Отправить", callback_data="admin_broadcast_confirm")],
        [InlineKeyboardButton("❌ Отмена", callback_data="admin_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Подтвердите рассылку:\n\n{text[:500]}", reply_markup=reply_markup
    )
    return ConversationHandler.END


async def admin_broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = context.user_data.get("broadcast_text", "")
    keyboard = [[InlineKeyboardButton("Назад", callback_data="admin_menu")]]
    # In a real app, iterate over all registered users and send_message.
    # For portfolio template we just acknowledge the action.
    await _safe_edit(query, f"✅ Рассылка отправлена\n\n{text[:100]}", InlineKeyboardMarkup(keyboard))
    context.user_data.pop("broadcast_text", None)


async def admin_reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    events = await get_upcoming_events(days_ahead=30)
    if not events:
        text = "Нет предстоящих мероприятий в ближайшие 30 дней."
    else:
        lines = [f"  • {i}: {e['name']} ({e['date']})" for i, e in enumerate(events)]
        text = f"⏰ Напоминания\nВыберите мероприятие:\n" + "\n".join(lines)
    keyboard = [[InlineKeyboardButton("Назад", callback_data="admin_menu")]]
    await _safe_edit(query, text, InlineKeyboardMarkup(keyboard))


async def admin_faq_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Просмотр", callback_data="admin_faq_view")],
        [InlineKeyboardButton("Редактировать", callback_data="admin_faq_edit")],
        [InlineKeyboardButton("Назад", callback_data="admin_menu")],
    ]
    await _safe_edit(query, "❓ Управление FAQ", InlineKeyboardMarkup(keyboard))


async def admin_faq_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = load_faq()
    keyboard = [[InlineKeyboardButton("Назад", callback_data="admin_faq")]]
    await _safe_edit(query, text[:4000], InlineKeyboardMarkup(keyboard))


async def admin_faq_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "Введите новый текст для FAQ:"
    keyboard = [[InlineKeyboardButton("Отмена", callback_data="admin_faq")]]
    await _safe_edit(query, text, InlineKeyboardMarkup(keyboard))
    return FAQ_EDIT


async def admin_faq_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_faq(update.message.text)
    keyboard = [[InlineKeyboardButton("Назад", callback_data="admin_faq")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("FAQ обновлён!", reply_markup=reply_markup)
    return ConversationHandler.END


# ── Admin menu router ─────────────────────────────────────────────
async def admin_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⏰ Напоминания", callback_data="admin_reminder")],
        [InlineKeyboardButton("❓ Управление FAQ", callback_data="admin_faq")],
    ]
    await _safe_edit(query, "Панель администратора:", InlineKeyboardMarkup(keyboard))


# ── Conversation handlers ─────────────────────────────────────────
broadcast_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_broadcast_start, pattern="^admin_broadcast$")],
    states={
        BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_broadcast_send)],
    },
    fallbacks=[CallbackQueryHandler(admin_menu_callback, pattern="^admin_menu$")],
)

faq_manage_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_faq_edit, pattern="^admin_faq_edit$")],
    states={
        FAQ_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_faq_save)],
    },
    fallbacks=[CallbackQueryHandler(admin_faq_start, pattern="^admin_faq$")],
)

admin_callback_handler = CallbackQueryHandler(
    admin_menu_callback, pattern="^admin_menu$|^admin_stats$|^admin_reminder$|^admin_faq$|^admin_broadcast_confirm$|^admin_faq_view$"
)


def get_admin_conv_handlers():
    """Return all conversation handlers needed by main."""
    return [broadcast_handler, faq_manage_conv, admin_callback_handler]


# ── Helpers ───────────────────────────────────────────────────────
async def _safe_edit(query, text: str, reply_markup=None):
    import telegram.error
    try:
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except telegram.error.BadRequest as e:
        if "not modified" in str(e).lower():
            pass
        else:
            try:
                await query.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
            except Exception:
                pass
    except Exception:
        pass
