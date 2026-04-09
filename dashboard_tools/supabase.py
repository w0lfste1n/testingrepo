from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from dashboard_tools.config import require_env
from dashboard_tools.http import request_json


def _supabase_url() -> str:
    return require_env("SUPABASE_URL").rstrip("/")


def _service_key() -> str:
    return require_env("SUPABASE_SERVICE_ROLE_KEY")


def _headers() -> dict[str, str]:
    key = _service_key()
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def supabase_request(
    method: str,
    path: str,
    *,
    query: dict[str, Any] | None = None,
    body: Any | None = None,
    extra_headers: dict[str, str] | None = None,
) -> Any:
    headers = _headers()
    if extra_headers:
        headers.update(extra_headers)
    return request_json(method, _supabase_url() + path, headers=headers, query=query, json_body=body)


def upsert_orders(rows: list[dict[str, Any]]) -> Any:
    if not rows:
        return []
    return supabase_request(
        "POST",
        "/rest/v1/orders",
        query={"on_conflict": "retailcrm_id"},
        body=rows,
        extra_headers={"Prefer": "resolution=merge-duplicates,return=representation"},
    )


def fetch_orders_for_dashboard() -> list[dict[str, Any]]:
    return supabase_request(
        "GET",
        "/rest/v1/orders",
        query={
            "select": "retailcrm_id,created_at,total_amount,city,utm_source",
            "total_amount": "gt.0",
            "order": "created_at.asc",
            "limit": 1000,
        },
    )


def fetch_unnotified_large_orders(threshold: int) -> list[dict[str, Any]]:
    return supabase_request(
        "GET",
        "/rest/v1/orders",
        query={
            "select": "retailcrm_id,order_number,first_name,last_name,city,total_amount,created_at",
            "total_amount": f"gt.{threshold}",
            "telegram_notified": "eq.false",
            "order": "created_at.asc",
            "limit": 100,
        },
    )


def mark_orders_notified(order_ids: list[int]) -> Any:
    if not order_ids:
        return []
    joined = ",".join(str(order_id) for order_id in order_ids)
    return supabase_request(
        "PATCH",
        "/rest/v1/orders",
        query={"retailcrm_id": f"in.({joined})"},
        body={
            "telegram_notified": True,
            "telegram_notified_at": datetime.now(timezone.utc).isoformat(),
        },
        extra_headers={"Prefer": "return=representation"},
    )
