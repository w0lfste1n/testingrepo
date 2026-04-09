from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler

from dashboard_tools.config import load_dotenv
from dashboard_tools.workflows import build_dashboard_payload


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        load_dotenv()
        payload = build_dashboard_payload()
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
