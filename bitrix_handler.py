"""
Bitrix24 CRM lead creation.
Gracefully skips all operations if Bitrix webhook is not configured.
"""
import os
import aiohttp
import logging

import config

logger = logging.getLogger(__name__)


async def _do_bitrix(url: str, payload: dict) -> dict:
    """POST to Bitrix, return parsed JSON or {} on failure."""
    if not config.BITRIX_WEBHOOK_URL:
        return {}
    full_url = f"{config.BITRIX_WEBHOOK_URL}{url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(full_url, json=payload) as response:
                return await response.json()
    except Exception as e:
        logger.debug("Bitrix call failed %s: %s", url, e)
        return {}


async def _get_telegram_bot_source_id() -> str:
    """Dynamically fetch the SOURCE ID for 'Telegram BOT' from Bitrix."""
    data = await _do_bitrix(
        "crm.status.list.json",
        {"filter": {"ENTITY_ID": "SOURCE"}},
    )
    for item in data.get("result", []):
        if item.get("NAME") == "Telegram BOT":
            return item["STATUS_ID"]
    return "WEB"


def _build_deal_fields(user_data: dict) -> dict:
    """Build minimal CRM deal fields. Custom fields only if present."""
    fields: dict = {
        "TITLE": f"Заявка с Telegram: {user_data.get('name', '')}",
        "NAME": user_data.get("name", ""),
        "CATEGORY_ID": config.BITRIX_CATEGORY_ID,
        "STAGE_ID": config.BITRIX_STAGE_ID,
    }
    # Optional custom fields
    mapping = {
        "UF_CRM_PHONE": user_data.get("phone"),
        "UF_CRM_EMAIL": user_data.get("email"),
        "UF_CRM_COMPANY": user_data.get("company"),
        "UF_CRM_POSITION": user_data.get("position"),
    }
    for env_key, val in mapping.items():
        cfg_key = getattr(config, env_key, None)
        if cfg_key and val:
            fields[cfg_key] = val
    return fields


async def create_cold_lead(user_data: dict) -> int:
    """Create a 'cold' lead in Bitrix after the user shares contact."""
    if not config.HAS_BITRIX:
        return 0
    fields = {
        "fields": {
            "TITLE": f"Новый пользователь Telegram: {user_data.get('name', '')}",
            "CATEGORY_ID": config.BITRIX_CATEGORY_ID,
            "STAGE_ID": "NEW",
        }
    }
    source = await _get_telegram_bot_source_id()
    fields["fields"]["SOURCE_ID"] = source
    result = await _do_bitrix("crm.deal.add.json", fields)
    deal_id = result.get("result", 0)
    logger.info("Bitrix cold lead id=%d", deal_id)
    return deal_id


async def create_hot_lead(user_data: dict, event_name: str = "") -> int:
    """Create a 'hot' lead in Bitrix after event registration."""
    if not config.HAS_BITRIX:
        return 0
    fields = {
        "fields": _build_deal_fields(user_data)
    }
    fields["fields"]["TITLE"] = f"Регистрация на {event_name or 'мероприятие'}"
    fields["fields"]["COMMENTS"] = f"Клиент зарегистрировался через Telegram бота"
    source = await _get_telegram_bot_source_id()
    fields["fields"]["SOURCE_ID"] = source
    result = await _do_bitrix("crm.deal.add.json", fields)
    deal_id = result.get("result", 0)
    logger.info("Bitrix hot lead id=%d", deal_id)
    return deal_id
