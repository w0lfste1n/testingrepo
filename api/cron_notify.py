from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler

from dashboard_tools.config import load_dotenv
from dashboard_tools.workflows import notify_large_orders, sync_orders_from_retailcrm


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        load_dotenv()
        sync_result = sync_orders_from_retailcrm()
        notify_result = notify_large_orders()
        body = json.dumps(
            {"ok": True, "sync": sync_result, "notify": notify_result},
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)
