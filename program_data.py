"""
Fetch program / course data from Google Sheets (or empty list).
"""
import os
import asyncio
import logging
from sheets_client import get_gsheets_client
import config

logger = logging.getLogger(__name__)


async def get_program_data():
    """Retrieve rows from the programs Google Sheet."""
    if not config.HAS_GOOGLE_SHEETS:
        return _fallback_programs()

    client = get_gsheets_client()
    if not client:
        return _fallback_programs()

    def _get():
        try:
            workbook = client.open_by_key(config.GOOGLE_SHEET_ID_PROGRAMS)
            sheet = workbook.sheet1
            headers = sheet.row_values(1)
            programs = []
            for row in sheet.get_all_values()[1:]:
                if row and any(row):
                    program = dict(zip(headers, row))
                    program["Картинка"] = program.get("Картинка", "")
                    programs.append(program)
            return programs
        except Exception as e:
            logger.error("Error reading programs sheet: %s", e)
            return _fallback_programs()

    try:
        return await asyncio.to_thread(_get)
    except Exception as e:
        logger.error("Error reading programs from Google Sheets: %s", e)
        return _fallback_programs()


def _fallback_programs():
    """
    Minimal placeholder data so the bot works without Sheets.
    """
    return [
        {
            "Название": "Demo Program 1",
            "Картинка": "",
            "Описание": "Demo program — Google Sheets not configured",
            "Продолжительность": "4 weeks",
            "Стоимость": "Consult with manager",
        },
    ]
