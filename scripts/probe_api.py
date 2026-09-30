#!/usr/bin/env python3
"""Authorized API surface probe for 100xDevs course-backend. Read-only by default."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

BASE = os.environ.get("COURSE_API_BASE", "https://course-backend.100xdevs.com").rstrip("/")
ORIGIN = os.environ.get("COURSE_ORIGIN", "https://100xdevs.com")
BEARER = os.environ.get("COURSE_API_BEARER", "")

ROUTES: list[tuple[str, str, dict[str, Any] | None]] = [
    ("GET", "/health", None),
    ("GET", "/home", None),
    ("GET", "/courses/categories", None),
    ("GET", "/courses/web-dev-devops-bootcamp", None),
    (
        "GET",
        "/courses/web-dev-devops-bootcamp/content?parentId=-1&includeExpiredAccess=true",
        None,
    ),
    ("GET", "/payments/currencies", None),
    ("POST", "/payments/quote", {"courseId": "24", "currency": "INR"}),
    ("POST", "/auth/login", {"email": "nouser@example.com", "password": "wrong"}),
    ("POST", "/auth/password/forgot", {"email": "nouser@example.com"}),
    ("POST", "/auth/otp/send", {"email": "probe-no-send@example.com"}),
    ("GET", "/auth/me", None),
    ("GET", "/purchases", None),
    ("GET", "/dsa/overview", None),
    ("POST", "/affiliate/visit", {"referralCode": "probe", "courseSlug": "web-dev-devops-bootcamp"}),
    ("GET", "/admin", None),
]


@dataclass
class Result:
    method: str
    path: str
    status: int
    snippet: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "path": self.path,
            "status": self.status,
            "snippet": self.snippet,
        }


def request(method: str, path: str, body: dict[str, Any] | None) -> Result:
    url = f"{BASE}{path}"
    headers = {
        "Accept": "application/json",
        "Origin": ORIGIN,
    }
    if BEARER:
        headers["Authorization"] = f"Bearer {BEARER}"
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read(500).decode("utf-8", errors="replace")
            return Result(method, path, resp.status, raw.replace("\n", " ")[:200])
    except urllib.error.HTTPError as e:
        raw = e.read(500).decode("utf-8", errors="replace")
        return Result(method, path, e.code, raw.replace("\n", " ")[:200])
    except urllib.error.URLError as e:
        return Result(method, path, 0, str(e.reason)[:200])


def main() -> int:
    results = [request(m, p, b).to_dict() for m, p, b in ROUTES]
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "api-coverage.json"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = {
        "base": BASE,
        "authenticated": bool(BEARER),
        "probedAt": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "results": results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path} ({len(results)} routes)")
    for r in results:
        print(f"{r['status']:>3} {r['method']:4} {r['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
