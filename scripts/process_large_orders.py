from __future__ import annotations

import json

from dashboard_tools.config import load_dotenv
from dashboard_tools.workflows import notify_large_orders, sync_orders_from_retailcrm


def main() -> None:
    load_dotenv()
    sync_result = sync_orders_from_retailcrm()
    notify_result = notify_large_orders()
    print(json.dumps({"sync": sync_result, "notify": notify_result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
