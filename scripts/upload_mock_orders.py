from __future__ import annotations

import json

from dashboard_tools.config import load_dotenv, require_env
from dashboard_tools.orders import load_mock_orders, prepare_mock_orders_for_retailcrm
from dashboard_tools.retailcrm import upload_orders


def main() -> None:
    load_dotenv()
    require_env("RETAILCRM_BASE_URL")
    require_env("RETAILCRM_API_KEY")
    require_env("RETAILCRM_SITE_CODE")

    orders = prepare_mock_orders_for_retailcrm(load_mock_orders())
    response = upload_orders(orders)
    print(json.dumps({"uploaded": len(orders), "response": response}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
