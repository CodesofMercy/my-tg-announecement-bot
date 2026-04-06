"""
Programs listing and detail display.

Uses Google Sheets via program_data.get_program_data().
Falls back to demo data if Sheets unavailable.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from program_data import get_program_data
import telegram.error


async def show_programs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display list of programs as inline buttons."""
    query = update.callback_query
    programs = await get_program_data()

    keyboard = []
    if not programs:
        text = "📚 Пока нет доступных программ.\nСледите за обновлениями!"
    else:
        title = "📚 Программы обучения:"
        lines = [title]
        for i, prog in enumerate(programs):
            name = prog.get("Название", f"Program {i+1}")
            duration = prog.get("Продолжительность", "")
            price = prog.get("Стоимость", "")
            label = f"{name}"
            if duration:
                label += f" — {duration}"
            if price:
                label += f" ({price})"
            lines.append(f"  {i+1}. {label}")
            keyboard.append([
                InlineKeyboardButton(f"🎓 {name}", callback_data=f"program_show_{i}")
            ])
        text = "\n".join(lines)
        keyboard.append([InlineKeyboardButton("Домой", callback_data="start")])

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    if query:
        await query.answer()
        await _safe_edit_or_reply(query.message, text, reply_markup)
    elif update.message:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


async def show_program_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display detailed info for a single program."""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    programs = await get_program_data()

    try:
        idx = int(query.data.replace("program_show_", ""))
        if not (0 <= idx < len(programs)):
            await query.message.reply_text("Программа не найдена.")
            return
    except (ValueError, IndexError):
        await query.message.reply_text("Программа не найдена.")
        return

    prog = programs[idx]
    name = prog.get("Название", "")
    duration = prog.get("Продолжительность", "")
    price = prog.get("Стоимость", "")
    desc = prog.get("Описание", "")
    image_url = prog.get("Картинка", "").strip()

    text = f"🎓 <b>{name}</b>\n"
    if duration:
        text += f"⏱ {duration}\n"
    if price:
        text += f"💰 {price}\n"
    if desc:
        text += f"\n{desc}\n"

    keyboard = [
        [InlineKeyboardButton("✍️ Зарегистрироваться", callback_data=f"register_program_{idx}")],
        [InlineKeyboardButton("Домой", callback_data="start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if image_url and image_url.startswith(("http://", "https://")):
        try:
            await query.message.reply_photo(
                photo=image_url, caption=text, parse_mode="HTML", reply_markup=reply_markup
            )
            await query.message.delete()
            return
        except Exception:
            pass

    await _safe_edit_or_reply(query.message, text, reply_markup)


# Handler
show_programs_handler = CallbackQueryHandler(show_programs, pattern="^show_programs$")
show_program_details_handler = CallbackQueryHandler(show_program_details, pattern="^program_show_")


async def _safe_edit_or_reply(message, text: str, reply_markup):
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
