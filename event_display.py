"""
Events listing and detail display.

Uses Google Sheets via event_data.get_event_data().
Falls back to demo data if Sheets unavailable.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from event_data import get_event_data
import telegram.error

import config


async def show_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display list of upcoming events as inline buttons."""
    query = update.callback_query
    events = await get_event_data()

    keyboard = []
    if not events:
        text = "📅 Пока нет предстоящих мероприятий.\nСледите за обновлениями!"
    else:
        title = "📅 Афиша мероприятий:"
        lines = [title]
        for i, ev in enumerate(events):
            name = ev.get("Название", f"Event {i+1}")
            date = ev.get("Дата", "")
            price = ev.get("Цена", "")
            label = f"{name}"
            if date:
                label += f" — {date}"
            if price:
                label += f" ({price})"
            lines.append(f"  {i+1}. {label}")
            keyboard.append([
                InlineKeyboardButton(f"📌 {name}", callback_data=f"event_show_{i}")
            ])
        text = "\n".join(lines)

        keyboard.append([InlineKeyboardButton("Домой", callback_data="start")])

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    if query:
        await query.answer()
        await _safe_edit_or_reply(query.message, text, reply_markup)
    elif update.message:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


# Handler
show_events_handler = CallbackQueryHandler(show_events, pattern="^show_events$")


async def show_event_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display detailed info for a single event."""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    events = await get_event_data()

    try:
        # Extract index from callback like "event_show_3"
        idx = int(query.data.replace("event_show_", ""))
        if not (0 <= idx < len(events)):
            await query.message.reply_text("Мероприятие не найдено.")
            return
    except (ValueError, IndexError):
        await query.message.reply_text("Мероприятие не найдено.")
        return

    ev = events[idx]
    name = ev.get("Название", "")
    date = ev.get("Дата", "")
    price = ev.get("Цена", "")
    desc = ev.get("Описание", "")
    location = ev.get("Место", "")
    image_url = ev.get("Картинка", "").strip()

    text = f"📌 <b>{name}</b>\n"
    if date:
        text += f"📆 {date}\n"
    if location:
        text += f"📍 {location}\n"
    if price:
        text += f"💰 {price}\n"
    if desc:
        text += f"\n{desc}\n"

    keyboard = [
        [InlineKeyboardButton("✍️ Зарегистрироваться", callback_data=f"register_{idx}")],
        [InlineKeyboardButton("Домой", callback_data="start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send photo if available and URL is valid
    if image_url and image_url.startswith(("http://", "https://")):
        try:
            await query.message.reply_photo(
                photo=image_url, caption=text, parse_mode="HTML", reply_markup=reply_markup
            )
            await query.message.delete()
            return
        except Exception as e:
            import logging
            logging.getLogger(__name__).debug("Image send failed: %s", e)

    await _safe_edit_or_reply(query.message, text, reply_markup)


# Handler
show_event_details_handler = CallbackQueryHandler(show_event_details, pattern="^event_show_")


# ── Helpers ───────────────────────────────────────────────────────
async def _safe_edit_or_reply(message, text: str, reply_markup):
    """Edit existing message; fall back to reply on failure."""
    try:
        await message.edit_text(text, parse_mode="HTML", reply_markup=reply_markup)
    except telegram.error.BadRequest as e:
        err = str(e).lower()
        if "not modified" not in err:
            if "there is no text" in err:
                try:
                    await message.delete()
                except Exception:
                    pass
                await message.chat.send_message(text, parse_mode="HTML", reply_markup=reply_markup)
            else:
                await message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
    except Exception:
        pass
