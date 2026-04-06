"""
Fetch event data from Google Sheets (or empty list if unavailable).
"""
import os
import asyncio
import logging
from sheets_client import get_gsheets_client
import config

logger = logging.getLogger(__name__)


async def get_event_data():
    """Retrieve rows from the events Google Sheet."""
    if not config.HAS_GOOGLE_SHEETS:
        return _fallback_events()

    client = get_gsheets_client()
    if not client:
        return _fallback_events()

    def _get():
        try:
            workbook = client.open_by_key(config.GOOGLE_SHEET_ID_EVENTS)
            sheet = workbook.sheet1
            headers = sheet.row_values(1)
            events = []
            for row in sheet.get_all_values()[1:]:
                if row and any(row):
                    event = dict(zip(headers, row))
                    event["Картинка"] = event.get("Картинка", "")
                    event["Кодовое слово"] = event.get("Кодовое слово", "")
                    events.append(event)
            return events
        except Exception as e:
            logger.error("Error reading events sheet: %s", e)
            return _fallback_events()

    try:
        return await asyncio.to_thread(_get)
    except Exception as e:
        logger.error("Error reading events from Google Sheets: %s", e)
        return _fallback_events()


def _fallback_events():
    """
    Minimal placeholder data so the bot works without Sheets.
    Replace with your own demo data.
    """
    return [
        {
            "Название": "Demo Event 1",
            "Дата": "01.01.2027",
            "Цена": "Free",
            "Картинка": "",
            "Кодовое слово": "",
            "Описание": "Demo event — Google Sheets not configured",
            "Место": "Online",
        },
    ]
