"""
Central configuration module.

All settings loaded here once. External integrations (Google Sheets, Bitrix, etc.)
are *optional* — the bot starts even if they are not configured.

Required: BOT_TOKEN (the bot won't start without it)
"""
import os
import logging
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env if it exists (first call only — safe to call multiple times)
load_dotenv()


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Read env variable, strip whitespace."""
    val = os.environ.get(key, default)
    return val.strip() if val else val


def _env_bool(key: str, default: bool = False) -> bool:
    return os.environ.get(key, str(default)).lower() in ("1", "true", "yes", "on")


def _env_list(key: str, default: str = "") -> List[str]:
    raw = os.environ.get(key, default)
    return [x.strip() for x in raw.split(",") if x.strip()]


def _env_int(key: str, default: int = 0) -> int:
    val = os.environ.get(key)
    try:
        return int(val) if val else default
    except (ValueError, TypeError):
        return default


# ── Telegram ─────────────────────────────────────────────────────────────────────
BOT_TOKEN = _env("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in _env_list("ADMIN_IDS")]

# ── Branding / Text ──────────────────────────────────────────────────────
BOT_WELCOME_TEXT = _env("BOT_WELCOME_TEXT", "Добро пожаловать! Выберите действие:")
MANAGER_USERNAME = _env("MANAGER_USERNAME", "ExEdTeam")
FAQ_FALLBACK_TEXT = _env("FAQ_FALLBACK_TEXT", "FAQ временно в разработке, возвращайтесь чуточку позже.")

# ── UI: Button Labels ────────────────────────────────────────────────────
BTN_EVENTS = _env("BTN_EVENTS", "📅 Мероприятия")
BTN_PROGRAMS = _env("BTN_PROGRAMS", "📚 Программы")
BTN_MANAGER = _env("BTN_MANAGER", "👤 Менеджер")
BTN_FAQ = _env("BTN_FAQ", "❓ FAQ")
BTN_ADMIN = _env("BTN_ADMIN", "⚙️ Админ")
BTN_HOME = _env("BTN_HOME", "Домой")
BTN_REGISTER = _env("BTN_REGISTER", "✍️ Зарегистрироваться")
BTN_BACK = _env("BTN_BACK", "Назад")
BTN_CANCEL = _env("BTN_CANCEL", "Отмена")
BTN_WRITE_MANAGER = _env("BTN_WRITE_MANAGER", "Написать менеджеру")

# Admin panel buttons
BTN_ADMIN_STATS = _env("BTN_ADMIN_STATS", "📊 Статистика")
BTN_ADMIN_BROADCAST = _env("BTN_ADMIN_BROADCAST", "📢 Рассылка")
BTN_ADMIN_REMINDERS = _env("BTN_ADMIN_REMINDERS", "⏰ Напоминания")
BTN_ADMIN_FAQ = _env("BTN_ADMIN_FAQ", "❓ Управление FAQ")
BTN_ADMIN_FAQ_VIEW = _env("BTN_ADMIN_FAQ_VIEW", "Просмотр")
BTN_ADMIN_FAQ_EDIT = _env("BTN_ADMIN_FAQ_EDIT", "Редактировать")
BTN_SEND_CONFIRM = _env("BTN_SEND_CONFIRM", "✅ Отправить")

# ── UI: Messages ──────────────────────────────────────────────────────
MSG_NO_EVENTS = _env("MSG_NO_EVENTS", "📅 Пока нет предстоящих мероприятий.\nСледите за обновлениями!")
MSG_EVENTS_TITLE = _env("MSG_EVENTS_TITLE", "📅 Афиша мероприятий:")
MSG_EVENT_NOT_FOUND = _env("MSG_EVENT_NOT_FOUND", "Мероприятие не найдено.")

MSG_NO_PROGRAMS = _env("MSG_NO_PROGRAMS", "📚 Пока нет доступных программ.\nСледите за обновлениями!")
MSG_PROGRAMS_TITLE = _env("MSG_PROGRAMS_TITLE", "📚 Программы обучения:")
MSG_PROGRAM_NOT_FOUND = _env("MSG_PROGRAM_NOT_FOUND", "Программа не найдена.")

MSG_ADMIN_TITLE = _env("MSG_ADMIN_TITLE", "Панель администратора:")
MSG_ADMIN_NO_ACCESS = _env("MSG_ADMIN_NO_ACCESS", "У вас нет прав администратора.")
MSG_ADMIN_BACK_TEXT = _env("MSG_ADMIN_BACK_TEXT", "Панель администратора:")

MSG_NO_ADMIN_EVENTS = _env("MSG_NO_ADMIN_EVENTS", "Нет предстоящих мероприятий в ближайшие 30 дней.")
MSG_ADMIN_REMINDERS_TITLE = _env("MSG_ADMIN_REMINDERS_TITLE", "⏰ Напоминания\nВыберите мероприятие:")

MSG_BROADCAST_PROMPT = _env("MSG_BROADCAST_PROMPT", "📢 Рассылка\n\nВведите текст для рассылки всем пользователям:")
MSG_BROADCAST_CONFIRM = _env("MSG_BROADCAST_CONFIRM", "Подтвердите рассылку:\n\n{text}")
MSG_BROADCAST_SENT = _env("MSG_BROADCAST_SENT", "✅ Рассылка отправлена\n\n{text}")
MSG_BROADCAST_BACK = _env("MSG_BROADCAST_BACK", "Назад")

MSG_FAQ_MANAGE_TITLE = _env("MSG_FAQ_MANAGE_TITLE", "❓ Управление FAQ")
MSG_FAQ_EDIT_PROMPT = _env("MSG_FAQ_EDIT_PROMPT", "Введите новый текст для FAQ:")
MSG_FAQ_SAVED = _env("MSG_FAQ_SAVED", "FAQ обновлён!")

MSG_REG_COMPANY = _env("MSG_REG_COMPANY", "Регистрация: {item_name}\n\nВведите название вашей компании:")
MSG_REG_COMPANY_EMPTY = _env("MSG_REG_COMPANY_EMPTY", "Поле не может быть пустым. Введите название компании:")
MSG_REG_COMPANY_LONG = _env("MSG_REG_COMPANY_LONG", "Слишком длинное название (макс. 255 символов). Повторите:")
MSG_REG_POSITION = _env("MSG_REG_POSITION", "Отлично! Теперь введите вашу должность:")
MSG_REG_POSITION_EMPTY = _env("MSG_REG_POSITION_EMPTY", "Поле не может быть пустым. Введите должность:")
MSG_REG_POSITION_LONG = _env("MSG_REG_POSITION_LONG", "Слишком длинное поле (макс. 255 символов). Повторите:")
MSG_REG_EMAIL = _env("MSG_REG_EMAIL", "Теперь введите ваш email:")
MSG_REG_EMAIL_EMPTY = _env("MSG_REG_EMAIL_EMPTY", "Введите ваш email:")
MSG_REG_EMAIL_INVALID = _env("MSG_REG_EMAIL_INVALID", "Неверный формат email. Попробуйте ещё раз:")
MSG_REG_CODE_WORD = _env("MSG_REG_CODE_WORD", "Введите кодовое слово для подтверждения участия:")
MSG_REG_CODE_OK = _env("MSG_REG_CODE_OK", "Код подтверждён!")
MSG_REG_CODE_FAIL_3 = _env("MSG_REG_CODE_FAIL_3", "Неверный код (3 попытки исчерпаны). Обратитесь к менеджеру.")
MSG_REG_CODE_FAIL_REMAINING = _env("MSG_REG_CODE_FAIL_REMAINING", "Неверный код. Осталось попыток: {remaining}")
MSG_REG_CONFIRM = _env("MSG_REG_CONFIRM", "✅ Регистрация завершена!\n\nМероприятие: <b>{item_name}</b>\nИмя: {first_name} {last_name}\nEmail: {email}\n\nМы свяжемся с вами для подтверждения.")
MSG_REG_ERROR_EVENT = _env("MSG_REG_ERROR_EVENT", "Ошибка: мероприятие не найдено.")
MSG_REG_ERROR_EVENT_ID = _env("MSG_REG_ERROR_EVENT_ID", "Ошибка ID мероприятия.")
MSG_REG_ERROR_PROGRAM = _env("MSG_REG_ERROR_PROGRAM", "Ошибка: программа не найдена.")
MSG_REG_ERROR_PROGRAM_ID = _env("MSG_REG_ERROR_PROGRAM_ID", "Ошибка ID программы.")
MSG_MANAGER_CONTACT = _env("MSG_MANAGER_CONTACT", "Связаться с менеджером: @{manager}")

MSG_CONTACT_PROMPT = _env("MSG_CONTACT_PROMPT", "Мы хотим вас запомнить и будем рады, если вы поделитесь контактом, нажав кнопку ниже.")
BTN_SHARE_CONTACT = _env("BTN_SHARE_CONTACT", "Поделиться контактом")
MSG_CONTACT_THANKS = _env("MSG_CONTACT_THANKS", "Спасибо, {first_name}! Мы вас запомнили.")

# ── Google Sheets
GOOGLE_SHEET_ID_USERS = _env("GOOGLE_SHEET_ID_USERS")
GOOGLE_SHEET_ID_EVENTS = _env("GOOGLE_SHEET_ID_EVENTS")
GOOGLE_SHEET_ID_PROGRAMS = _env("GOOGLE_SHEET_ID_PROGRAMS")
GOOGLE_SHEET_ID_REGISTRATIONS = _env("GOOGLE_SHEET_ID_REGISTRATIONS")
GOOGLE_CREDENTIALS_PATH = _env("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

# True if credentials file exists and Sheets IDs are set
HAS_GOOGLE_SHEETS = bool(
    GOOGLE_CREDENTIALS_PATH
    and os.path.exists(GOOGLE_CREDENTIALS_PATH)
    and GOOGLE_SHEET_ID_USERS
    and GOOGLE_SHEET_ID_EVENTS
    and GOOGLE_SHEET_ID_PROGRAMS
    and GOOGLE_SHEET_ID_REGISTRATIONS
)

# ── Bitrix24 CRM ─────────────────────────────────────────────────────────────────
BITRIX_WEBHOOK_URL = _env("BITRIX_WEBHOOK_URL")
BITRIX_CATEGORY_ID = _env_int("BITRIX_CATEGORY_ID", 17)
BITRIX_STAGE_ID = _env("BITRIX_STAGE_ID", "NEW")
BITRIX_FIELD_PHONE = _env("BITRIX_FIELD_PHONE")
BITRIX_FIELD_EMAIL = _env("BITRIX_FIELD_EMAIL")
BITRIX_FIELD_COMPANY = _env("BITRIX_FIELD_COMPANY")
BITRIX_FIELD_POSITION = _env("BITRIX_FIELD_POSITION")
BITRIX_FIELD_CODE_STATUS = _env("BITRIX_FIELD_CODE_STATUS")

HAS_BITRIX = bool(BITRIX_WEBHOOK_URL)

# ── Payments ─────────────────────────────────────────────────────────────────────
PAYMENT_URL = _env("PAYMENT_URL", "https://example.com/pay")

# ── Logging ──────────────────────────────────────────────────────────────────────
LOG_LEVEL = _env("LOG_LEVEL", "INFO").upper()

# ── Startup Validation ───────────────────────────────────────────────────────────
_REQUIRED_VARS = {
    "BOT_TOKEN": BOT_TOKEN,
}


def validate_config() -> List[str]:
    """
    Check all required configuration values.
    Returns a list of missing variables (empty if all good).
    """
    missing: List[str] = []
    for name, value in _REQUIRED_VARS.items():
        if not value:
            missing.append(name)
    return missing


def print_startup_diagnostics() -> None:
    """Print configuration status at bot startup."""
    missing = validate_config()
    if missing:
        logger.error("Missing required env vars: %s", missing)
        logger.error("Copy .env.example to .env and fill in the values.")
        raise RuntimeError(f"Missing required configuration: {missing}")

    logger.info("=== Bot Configuration ===")
    logger.info("  Telegram:       token=%s...", BOT_TOKEN[:10] if BOT_TOKEN else "unset")
    logger.info("  Admins:         %d IDs configured", len(ADMIN_IDS))
    logger.info("  Google Sheets:  %s", "OK" if HAS_GOOGLE_SHEETS else "DISABLED (will use local fallback)")
    logger.info("  Bitrix24 CRM:   %s", "OK" if HAS_BITRIX else "DISABLED")
    logger.info("  Manager:        @%s", MANAGER_USERNAME)
    logger.info("=========================")
