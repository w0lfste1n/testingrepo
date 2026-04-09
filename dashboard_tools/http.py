from __future__ import annotations

import json
from typing import Any
from urllib import parse, request
from urllib.error import HTTPError


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    query: dict[str, Any] | None = None,
    form: dict[str, Any] | None = None,
    json_body: Any | None = None,
    timeout: int = 30,
) -> Any:
    final_url = url
    if query:
        encoded_query = parse.urlencode(
            {key: value for key, value in query.items() if value is not None},
            doseq=True,
        )
        separator = "&" if "?" in url else "?"
        final_url = f"{url}{separator}{encoded_query}"

    payload = None
    final_headers = dict(headers or {})

    if form is not None:
        encoded = {}
        for key, value in form.items():
            if value is None:
                continue
            encoded[key] = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        payload = parse.urlencode(encoded, doseq=True).encode("utf-8")
        final_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    elif json_body is not None:
        payload = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        final_headers.setdefault("Content-Type", "application/json")

    req = request.Request(final_url, data=payload, headers=final_headers, method=method.upper())

    try:
        with request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            if not body:
                return None
            return json.loads(body)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {final_url}: {body}") from exc
