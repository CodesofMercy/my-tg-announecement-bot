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

# ── Branding / Text ──────────────────────────────────────────────────────────────
BOT_WELCOME_TEXT = _env("BOT_WELCOME_TEXT", "Добро пожаловать! Выберите действие:")
MANAGER_USERNAME = _env("MANAGER_USERNAME", "ExEdTeam")

# ── Google Sheets ────────────────────────────────────────────────────────────────
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
