from __future__ import annotations

import json
from typing import Any

from dashboard_tools.config import require_env
from dashboard_tools.http import request_json


def _base_url() -> str:
    return require_env("RETAILCRM_BASE_URL").rstrip("/") + "/api/v5"


def _api_key() -> str:
    return require_env("RETAILCRM_API_KEY")


def retailcrm_request(
    method: str,
    path: str,
    *,
    query: dict[str, Any] | None = None,
    form: dict[str, Any] | None = None,
) -> dict[str, Any]:
    params = {"apiKey": _api_key()}
    if query:
        params.update(query)
    response = request_json(method, _base_url() + path, query=params, form=form)
    if isinstance(response, dict) and response.get("success") is False:
        raise RuntimeError(f"RetailCRM request failed: {json.dumps(response, ensure_ascii=False)}")
    return response


def upload_orders(orders: list[dict[str, Any]], site_code: str | None = None) -> dict[str, Any]:
    payload = {
        "site": site_code or require_env("RETAILCRM_SITE_CODE"),
        "orders": orders,
    }
    return retailcrm_request("POST", "/orders/upload", form=payload)


def fetch_orders(limit: int = 100) -> list[dict[str, Any]]:
    site_code = require_env("RETAILCRM_SITE_CODE")
    page = 1
    orders: list[dict[str, Any]] = []

    while True:
        response = retailcrm_request(
            "GET",
            "/orders",
            query={
                "limit": limit,
                "page": page,
                "filter[sites][]": site_code,
            },
        )
        chunk = response.get("orders", [])
        if not chunk:
            break
        orders.extend(chunk)

        pagination = response.get("pagination") or {}
        total_pages = pagination.get("totalPageCount")
        if total_pages and page >= int(total_pages):
            break
        if len(chunk) < limit:
            break
        page += 1

    return orders
