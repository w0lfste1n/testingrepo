from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os
from typing import Any


def load_mock_orders(path: str = "mock_orders.json") -> list[dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def calculate_total_amount(order: dict[str, Any]) -> float:
    if order.get("totalSumm") is not None:
        return float(order["totalSumm"])

    total = 0.0
    for item in order.get("items", []):
        quantity = float(item.get("quantity", 0) or 0)
        price = float(item.get("initialPrice", 0) or 0)
        total += quantity * price
    return round(total, 2)


def prepare_mock_orders_for_retailcrm(orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_time = datetime.now(timezone.utc) - timedelta(days=len(orders) - 1)
    default_order_type = os.getenv("RETAILCRM_ORDER_TYPE", "main")
    default_order_method = os.getenv("RETAILCRM_ORDER_METHOD")
    prepared: list[dict[str, Any]] = []

    for index, order in enumerate(orders, start=1):
        copy = dict(order)
        copy["externalId"] = f"mock-order-{index:03d}"
        copy["createdAt"] = (base_time + timedelta(days=index - 1)).strftime("%Y-%m-%d %H:%M:%S")
        copy["managerComment"] = "Imported from mock_orders.json for the analytics dashboard test task."
        copy["orderType"] = default_order_type
        if default_order_method:
            copy["orderMethod"] = default_order_method
        prepared.append(copy)

    return prepared


def retailcrm_order_to_row(order: dict[str, Any]) -> dict[str, Any]:
    delivery = order.get("delivery") or {}
    address = delivery.get("address") or {}
    customer = order.get("customer") or {}
    custom_fields = order.get("customFields") or {}
    total_amount = calculate_total_amount(order)

    return {
        "retailcrm_id": int(order["id"]),
        "external_id": order.get("externalId"),
        "order_number": order.get("number"),
        "status": order.get("status"),
        "order_type": order.get("orderType"),
        "order_method": order.get("orderMethod"),
        "first_name": order.get("firstName") or customer.get("firstName"),
        "last_name": order.get("lastName") or customer.get("lastName"),
        "phone": order.get("phone") or customer.get("phone"),
        "email": order.get("email") or customer.get("email"),
        "city": address.get("city"),
        "address_text": address.get("text"),
        "utm_source": custom_fields.get("utm_source"),
        "total_amount": total_amount,
        "items_count": len(order.get("items", [])),
        "large_order": total_amount > 50000,
        "created_at": (order.get("createdAt") or datetime.now(timezone.utc).isoformat()).replace(" ", "T"),
        "raw_payload": order,
    }


def summarize_orders(rows: list[dict[str, Any]], threshold: int) -> dict[str, Any]:
    total_revenue = sum(float(row.get("total_amount", 0) or 0) for row in rows)
    total_orders = len(rows)
    average_order_value = round(total_revenue / total_orders, 2) if total_orders else 0
    large_orders = sum(1 for row in rows if float(row.get("total_amount", 0) or 0) > threshold)

    by_day: dict[str, dict[str, float | int]] = defaultdict(lambda: {"orders": 0, "revenue": 0.0})
    by_city: dict[str, float] = defaultdict(float)
    by_source: dict[str, float] = defaultdict(float)

    for row in rows:
        created_at = str(row.get("created_at") or "")
        day = created_at.split("T", 1)[0] if created_at else "unknown"
        amount = float(row.get("total_amount", 0) or 0)
        city = row.get("city") or "Unknown"
        source = row.get("utm_source") or "unknown"

        by_day[day]["orders"] += 1
        by_day[day]["revenue"] += amount
        by_city[city] += amount
        by_source[source] += amount

    daily = [
        {
            "date": day,
            "orders": values["orders"],
            "revenue": round(float(values["revenue"]), 2),
        }
        for day, values in sorted(by_day.items())
    ]
    top_cities = [
        {"city": city, "revenue": round(amount, 2)}
        for city, amount in sorted(by_city.items(), key=lambda item: item[1], reverse=True)
    ]
    top_sources = [
        {"source": source, "revenue": round(amount, 2)}
        for source, amount in sorted(by_source.items(), key=lambda item: item[1], reverse=True)
    ]

    return {
        "summary": {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "average_order_value": average_order_value,
            "large_orders": large_orders,
            "threshold": threshold,
        },
        "daily": daily,
        "top_cities": top_cities,
        "top_sources": top_sources,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
