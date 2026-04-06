# support.py
"""
Manager link and FAQ display.
Uses config for username, loads FAQ from text file or .env fallback.
"""
import os
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

import config

# ── FAQ ──────────────────────────────────────────────────────────
FAQ_FILE_PATH = "faq.txt"
FAQ_FALLBACK_TEXT = "FAQ временно в разработке, возвращайтесь чуточку позже."


def load_faq() -> str:
    """Load FAQ text from file, or return fallback."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FAQ_FILE_PATH)
    if not os.path.exists(path):
        return FAQ_FALLBACK_TEXT
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        return text if text else FAQ_FALLBACK_TEXT
    except Exception:
        return FAQ_FALLBACK_TEXT


def save_faq(draft: str) -> None:
    """Save FAQ text to file. Path is fixed to prevent traversal."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FAQ_FILE_PATH)
    with open(path, "w", encoding="utf-8") as f:
        f.write(draft)


async def manager_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command /manager — open a link to the manager."""
    mgr_user = config.MANAGER_USERNAME.lstrip("@")
    keyboard = [
        [InlineKeyboardButton("Написать менеджеру", url=f"https://t.me/{mgr_user}")],
        [InlineKeyboardButton("Домой", callback_data="start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"Связаться с менеджером: @{mgr_user}"
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        q = update.callback_query
        await q.answer()
        await _safe_edit_or_reply(q, text, reply_markup)


async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command /faq — show the FAQ."""
    text = load_faq()
    keyboard = [[InlineKeyboardButton("Домой", callback_data="start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        q = update.callback_query
        await q.answer()
        await _safe_edit_or_reply(q, text, reply_markup)


# ── Helpers ──────────────────────────────────────────────────────
async def _safe_edit_or_reply(query, text: str, reply_markup=None) -> None:
    """Edit message if possible. Fall back to reply on failure."""
    import telegram.error

    try:
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except telegram.error.BadRequest as e:
        err = str(e).lower()
        if "not modified" not in err:
            if "there is no text" in err:
                try:
                    await query.message.delete()
                except Exception:
                    pass
                await query.message.chat.send_message(text, reply_markup=reply_markup, parse_mode="HTML")
            else:
                await query.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning("_safe_edit_or_reply error: %s", e)
        await query.message.reply_text(text, reply_markup=reply_markup)
