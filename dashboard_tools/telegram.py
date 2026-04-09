from __future__ import annotations

from dashboard_tools.config import require_env
from dashboard_tools.http import request_json


def send_message(text: str) -> dict:
    token = require_env("TELEGRAM_BOT_TOKEN")
    chat_id = require_env("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    return request_json(
        "POST",
        url,
        form={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        },
    )
