from __future__ import annotations

from typing import Any

from dashboard_tools.config import get_threshold
from dashboard_tools.orders import retailcrm_order_to_row, summarize_orders
from dashboard_tools.retailcrm import fetch_orders
from dashboard_tools.supabase import (
    fetch_orders_for_dashboard,
    fetch_unnotified_large_orders,
    mark_orders_notified,
    upsert_orders,
)
from dashboard_tools.telegram import send_message


def sync_orders_from_retailcrm() -> dict[str, Any]:
    retailcrm_orders = fetch_orders()
    rows = [retailcrm_order_to_row(order) for order in retailcrm_orders if order.get("id")]
    upserted = upsert_orders(rows)
    return {
        "fetched": len(retailcrm_orders),
        "upserted": len(upserted) if isinstance(upserted, list) else len(rows),
    }


def build_dashboard_payload() -> dict[str, Any]:
    rows = fetch_orders_for_dashboard()
    return summarize_orders(rows, get_threshold())


def notify_large_orders() -> dict[str, Any]:
    threshold = get_threshold()
    orders = fetch_unnotified_large_orders(threshold)
    notified_ids: list[int] = []

    for order in orders:
        message = (
            "<b>Large order detected</b>\n"
            f"Order: #{order.get('order_number') or order.get('retailcrm_id')}\n"
            f"Customer: {(order.get('first_name') or '').strip()} {(order.get('last_name') or '').strip()}\n"
            f"City: {order.get('city') or 'Unknown'}\n"
            f"Amount: {float(order.get('total_amount', 0)):,.0f} ₸"
        )
        send_message(message)
        notified_ids.append(int(order["retailcrm_id"]))

    mark_orders_notified(notified_ids)
    return {
        "threshold": threshold,
        "checked": len(orders),
        "notified": len(notified_ids),
    }
