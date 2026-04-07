"""
Multi-step event / program registration conversation handler.

Flow:
  1. Select event or program
  2. Company
  3. Position
  4. Email (validated)
  5. Code word (optional, event-specific)
  6. Confirmation
"""
import os
import asyncio
import re
import logging
from typing import Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import telegram.error

import config
from support import MANAGER_USERNAME
from event_data import get_event_data
from program_data import get_program_data
from user_handler import save_user_to_gsheets, get_user_data
from bitrix_handler import create_hot_lead
from sheets_client import get_gsheets_client

logger = logging.getLogger(__name__)

# Conversation states
COMPANY, POSITION, EMAIL, CODE_WORD, PROGRAM_CODE = range(5)

# Simple email validator
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Begin registration flow for an event."""
    query = update.callback_query
    if query:
        await query.answer()
        data = query.data

        # Event registration
        if data.startswith("register_") and not data.startswith("register_program_"):
            event_id = data.replace("register_", "")
            events = await get_event_data()
            try:
                idx = int(event_id)
                if 0 <= idx < len(events):
                    context.user_data.update({
                        "event": events[idx],
                        "event_id": event_id,
                        "is_program": False,
                    })
                else:
                    await _safe_edit(query, config.MSG_REG_ERROR_EVENT, None)
                    return ConversationHandler.END
            except ValueError:
                await _safe_edit(query, config.MSG_REG_ERROR_EVENT_ID, None)
                return ConversationHandler.END

        # Program registration
        elif data.startswith("register_program_"):
            program_id = data.replace("register_program_", "")
            programs = await get_program_data()
            try:
                idx = int(program_id)
                if 0 <= idx < len(programs):
                    context.user_data.update({
                        "program": programs[idx],
                        "event_id": program_id,
                        "is_program": True,
                    })
                else:
                    await _safe_edit(query, config.MSG_REG_ERROR_PROGRAM, None)
                    return ConversationHandler.END
            except ValueError:
                await _safe_edit(query, config.MSG_REG_ERROR_PROGRAM_ID, None)
                return ConversationHandler.END

    item = context.user_data.get("event", context.user_data.get("program", {}))
    item_name = item.get("Название", "мероприятие")
    text = config.MSG_REG_COMPANY.format(item_name=item_name)
    await _safe_edit(update.callback_query, text, None)
    return COMPANY


async def register_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text(config.MSG_REG_COMPANY_EMPTY)
        return COMPANY
    if len(text) > 255:
        await update.message.reply_text(config.MSG_REG_COMPANY_LONG)
        return COMPANY
    context.user_data["company"] = text
    await update.message.reply_text(config.MSG_REG_POSITION)
    return POSITION


async def register_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text(config.MSG_REG_POSITION_EMPTY)
        return POSITION
    if len(text) > 255:
        await update.message.reply_text(config.MSG_REG_POSITION_LONG)
        return POSITION
    context.user_data["position"] = text
    await update.message.reply_text(config.MSG_REG_EMAIL)
    return EMAIL


async def register_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text(config.MSG_REG_EMAIL_EMPTY)
        return EMAIL
    if len(text) > 254 or not _EMAIL_RE.match(text):
        await update.message.reply_text(config.MSG_REG_EMAIL_INVALID)
        return EMAIL
    context.user_data["email"] = text
    # Check if event has a code word requirement
    item = context.user_data.get("event", {})
    code_word = item.get("Кодовое слово", "").strip()
    if code_word and code_word != "nan":
        await update.message.reply_text(config.MSG_REG_CODE_WORD)
        return CODE_WORD
    # Save and confirm
    await save_registration(update, context)
    return ConversationHandler.END


async def register_code_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.strip()
    item = context.user_data.get("event", {})
    expected = item.get("Кодовое слово", "").strip()

    # Track attempts
    attempts = context.user_data.get("code_attempts", 0) + 1
    context.user_data["code_attempts"] = attempts

    if user_input == expected:
        await update.message.reply_text(config.MSG_REG_CODE_OK, parse_mode="HTML")
        await save_registration(update, context)
    elif attempts >= 3:
        keyboard = [
            [InlineKeyboardButton(config.BTN_WRITE_MANAGER, url=f"https://t.me/{MANAGER_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton(config.BTN_HOME, callback_data="start")],
        ]
        await update.message.reply_text(
            config.MSG_REG_CODE_FAIL_3,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data.pop("code_attempts", None)
        return ConversationHandler.END
    else:
        remaining = 3 - attempts
        await update.message.reply_text(
            config.MSG_REG_CODE_FAIL_REMAINING.format(remaining=remaining),
        )
    return code_word_retry


# Allow returning to code_word from the inline handler
code_word_retry = CODE_WORD


async def save_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save registration to Google Sheets / Excel, create Bitrix deal, send confirmation."""
    user_data = context.user_data
    item = user_data.get("event", user_data.get("program", {}))
    item_name = item.get("Название", "Неизвестное мероприятие")
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or ""
    last_name = update.effective_user.last_name or ""
    username = update.effective_user.username or ""
    phone = user_data.get("phone_number", "")

    full_user = {
        "user_id": str(user_id),
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone,
        "username": username,
        "email": user_data.get("email", ""),
        "company": user_data.get("company", ""),
        "position": user_data.get("position", ""),
    }

    # Save user
    await save_user_to_gsheets(full_user)

    # Save registration to sheets
    if config.HAS_GOOGLE_SHEETS:
        try:
            client = get_gsheets_client()
            if client:
                ws = client.open_by_key(config.GOOGLE_SHEET_ID_REGISTRATIONS).sheet1
                headers = ["date", "event", "user_id", "name", "email", "phone", "company", "position"]
                values = [
                    async_io_timestamp(), item_name, str(user_id),
                    f"{first_name} {last_name}", user_data.get("email", ""),
                    phone, user_data.get("company", ""), user_data.get("position", "")
                ]
                # Ensure headers exist
                if not ws.row_values(1):
                    ws.append_row(headers)
                ws.append_row(values)
        except Exception as e:
            logger.error("Failed to save registration to Sheets: %s", e)

    # Bitrix lead
    await create_hot_lead(full_user, event_name=item_name)

    # Confirmation
    text = config.MSG_REG_CONFIRM.format(
        item_name=item_name,
        first_name=first_name,
        last_name=last_name,
        email=user_data.get('email', ''),
    )
    keyboard = [
        [InlineKeyboardButton(config.BTN_HOME, callback_data="start")],
    ]
    msg = update.message
    try:
        await msg.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error("Confirmation send failed: %s", e)

    context.user_data.clear()


def async_io_timestamp() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")


# ── Conversation Handler ──────────────────────────────────────────
conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(register_start, pattern="^register_")],
    states={
        COMPANY:  [MessageHandler(filters.TEXT & ~filters.COMMAND, register_company)],
        POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_position)],
        EMAIL:    [MessageHandler(filters.TEXT & ~filters.COMMAND, register_email)],
        CODE_WORD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, register_code_word),
        ],
    },
    fallbacks=[CallbackQueryHandler(_cancel_registration, pattern="^start$")],
)


async def _cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel registration flow and go home."""
    context.user_data.clear()
    from events import start_callback
    await start_callback(update, context)
    return ConversationHandler.END


# ── Helpers ───────────────────────────────────────────────────────
async def _safe_edit(query, text: str, reply_markup):
    """Edit callback message, or reply on failure."""
    if query and text:
        try:
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        except telegram.error.BadRequest:
            try:
                await query.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
            except Exception:
                pass
    elif text and update:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
