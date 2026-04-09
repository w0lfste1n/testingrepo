from __future__ import annotations

import json

from dashboard_tools.config import load_dotenv
from dashboard_tools.workflows import sync_orders_from_retailcrm


def main() -> None:
    load_dotenv()
    result = sync_orders_from_retailcrm()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
