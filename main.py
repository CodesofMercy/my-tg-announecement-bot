"""
Telegram Bot — Event Registration & Announcement

Entry point. Loads configuration, registers handlers, starts polling.
External services (Google Sheets, Bitrix) are optional — the bot
degrades gracefully if they are not configured.
"""
import logging

import config
from config import BOT_TOKEN, print_startup_diagnostics

from events import (
    start_command,
    events_command,
    show_events_handler,
    show_event_details_handler,
    start_handler,
    manager_button_handler,
    faq_button_handler,
)
from registration import conv_handler
from user_registration import request_contact_handler, handle_contact_handler
from support import manager_handler, faq_handler
from program_display import show_programs_handler, show_program_details_handler
from admin_panel import get_admin_handler


def setup_logging() -> None:
    """Configure root logger from LOG_LEVEL config."""
    logging.basicConfig(
        format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    )


def main() -> None:
    """Build application, register handlers, start polling."""
    setup_logging()
    print_startup_diagnostics()

    from telegram.ext import Application, CommandHandler, MessageHandler, filters

    app = Application.builder().token(BOT_TOKEN).build()

    # ── Commands ──────────────────────────────────────────────────
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("events", events_command))
    app.add_handler(CommandHandler("register", request_contact_handler))
    app.add_handler(CommandHandler("admin", get_admin_handler()))

    # ── Conversation handlers ─────────────────────────────────────
    app.add_handler(conv_handler)

    # ── Callback query handlers ───────────────────────────────────
    app.add_handler(show_events_handler)
    app.add_handler(show_event_details_handler)
    app.add_handler(start_handler)
    app.add_handler(manager_button_handler)
    app.add_handler(faq_button_handler)
    app.add_handler(show_programs_handler)
    app.add_handler(show_program_details_handler)

    # ── Message handlers (contact share) ──────────────────────────
    app.add_handler(handle_contact_handler)

    # ── Support ───────────────────────────────────────────────────
    app.add_handler(manager_handler)
    app.add_handler(faq_handler)

    # ── Catch-all for unknown text ────────────────────────────────
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _unknown_command))

    # ── Start ─────────────────────────────────────────────────────
    app.run_polling(allowed_updates=["message", "callback_query", "inline_query"])


def _unknown_command(update, context):
    """Fallback for messages that don't match any handler."""
    text = update.message.text.strip()
    logging.getLogger(__name__).info("Unknown text from %s: %s", update.effective_user.id, text)


if __name__ == "__main__":
    main()
