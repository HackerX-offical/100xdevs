#!/usr/bin/env python3
"""Discover admin routes that return 401 vs 404 (authorized testing only)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("COURSE_API_BASE", "https://course-backend.100xdevs.com").rstrip("/")
TOKEN = os.environ.get("COURSE_API_BEARER", "")

PREFIXES = ["/admin", "/admin/api", "/admin/v1"]
RESOURCES = [
    "users",
    "user",
    "courses",
    "orders",
    "payments",
    "cohorts",
    "content",
    "videos",
    "dashboard",
    "login",
    "auth/login",
    "enrollments",
    "invoices",
    "coupons",
    "settings",
    "moderators",
    "comments",
]


def probe(path: str) -> tuple[int, str]:
    headers = {"Origin": "https://100xdevs.com"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(f"{BASE}{path}", headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read(120).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(120).decode("utf-8", errors="replace")


def main() -> None:
    hits: list[dict] = []
    for prefix in PREFIXES:
        for res in RESOURCES:
            path = f"{prefix}/{res}"
            code, snippet = probe(path)
            if code == 401 and "Admin" in snippet:
                hits.append({"path": path, "status": code, "snippet": snippet[:80]})
    out = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "admin-fuzz.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"hits": hits}, f, indent=2)
    print(f"Wrote {out} ({len(hits)} admin-gated routes)")


if __name__ == "__main__":
    main()
