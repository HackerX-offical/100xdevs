#!/usr/bin/env python3
"""Measure peer user-id exposure via comments (authorized; uses caller's enrollments only)."""

from __future__ import annotations

import json
import os
import sys
import urllib.request

BASE = os.environ.get("COURSE_API_BASE", "https://course-backend.100xdevs.com").rstrip("/")
TOKEN = os.environ.get("COURSE_API_BEARER", "")
LIMIT = int(os.environ.get("COMMENT_SAMPLE_LIMIT", "25"))


def get(path: str) -> dict:
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Authorization": f"Bearer {TOKEN}", "Origin": "https://100xdevs.com"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def main() -> int:
    if not TOKEN:
        print("Set COURSE_API_BEARER", file=sys.stderr)
        return 1
    items = get(f"/courses/content/search?q=Week")["data"][:LIMIT]
    peer_ids: set[str] = set()
    videos_checked = 0
    for it in items:
        cid = str(it.get("id", ""))
        if not cid.isdigit():
            continue
        videos_checked += 1
        try:
            comments = get(f"/comments?contentItemId={cid}").get("comments", [])
        except Exception:
            continue
        for c in comments:
            aid = (c.get("author") or {}).get("id")
            if aid:
                peer_ids.add(aid)
    out = {
        "videosChecked": videos_checked,
        "uniquePeerAuthorIds": len(peer_ids),
        "sampleLimit": LIMIT,
    }
    print(json.dumps(out, indent=2))
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "comment-peer-enum.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
