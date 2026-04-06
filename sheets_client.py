"""
Lazy Google Sheets client.

Does NOT import gspread/credentials at module level.
Provides functions that initialise the client on first call.
If Google credentials are missing, returns None gracefully
— callers should fall back to local Excel storage.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_client: Optional[object] = None
_initialised = False


def get_gsheets_client() -> Optional[object]:
    """
    Return authorized gspread client, or None if not configured.
    Safe to call multiple times — caches the client after first load.
    """
    global _client, _initialised
    if _initialised:
        return _client

    try:
        import config
    except ImportError:
        logger.warning("config module not found; Google Sheets disabled")
        _initialised = True
        return None

    if not config.HAS_GOOGLE_SHEETS:
        logger.info("Google Sheets not configured (credentials or sheet IDs missing)")
        _initialised = True
        return None

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(
            config.GOOGLE_CREDENTIALS_PATH, scopes=scopes
        )
        _client = gspread.authorize(creds)
        logger.info("Google Sheets client authorised")
    except FileNotFoundError:
        logger.warning(
            "Credentials file not found: %s — Google Sheets disabled",
            config.GOOGLE_CREDENTIALS_PATH,
        )
    except Exception as e:
        logger.warning("Google Sheets auth failed: %s", e)

    _initialised = True
    return _client
