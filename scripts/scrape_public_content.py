#!/usr/bin/env python3
"""
Harvest course metadata exposed without authentication (metadata only).
Does NOT download video streams or bypass purchase gates.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = os.environ.get("COURSE_API_BASE", "https://course-backend.100xdevs.com").rstrip("/")
ORIGIN = os.environ.get("COURSE_ORIGIN", "https://100xdevs.com")
DELAY = float(os.environ.get("SCRAPE_DELAY", "2.1"))
SEARCH_Q = os.environ.get("SCRAPE_SEARCH_Q", "a")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "public-content")


def get(path: str) -> dict:
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Origin": ORIGIN, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def get_safe(path: str) -> dict | None:
    try:
        return get(path)
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": e.read(500).decode("utf-8", errors="replace")}
    except urllib.error.URLError as e:
        return {"status": 0, "error": str(e.reason)}


def walk_folders(course_id: str, parent: str = "-1", depth: int = 0, max_depth: int = 8) -> list[dict]:
    if depth > max_depth:
        return []
    path = f"/courses/{urllib.parse.quote(str(course_id), safe='')}/content?parentId={urllib.parse.quote(parent)}&includeExpiredAccess=true"
    time.sleep(DELAY)
    data = get_safe(path)
    if not data or "data" not in data:
        return []
    items: list[dict] = []
    for row in data.get("data", []):
        row["_source"] = f"folder:{parent}"
        items.append(row)
        rid = str(row.get("id", ""))
        if rid.isdigit() or row.get("childCounts"):
            items.extend(walk_folders(course_id, rid, depth + 1, max_depth))
    return items


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    home = get("/home")
    courses = home.get("featured", [])
    catalog: dict = {
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
        "base": BASE,
        "searchQuery": SEARCH_Q,
        "courses": {},
    }

    for c in courses:
        cid = c.get("id") or c.get("slug")
        if not cid:
            continue
        print(f"course {cid} …")
        slug = c.get("slug", "")
        time.sleep(DELAY)
        meta = get_safe(f"/courses/{urllib.parse.quote(str(cid), safe='')}")
        time.sleep(DELAY)
        q = urllib.parse.quote(SEARCH_Q)
        search = get_safe(
            f"/courses/{urllib.parse.quote(str(cid), safe='')}/content/search?q={q}&includeExpiredAccess=true"
        )
        time.sleep(DELAY)
        root = get_safe(
            f"/courses/{urllib.parse.quote(str(cid), safe='')}/content?parentId=-1&includeExpiredAccess=true"
        )
        # Optional deep folder walk (slow); default off — search q=a + root covers most public metadata
        folders: list[dict] = []
        if os.environ.get("SCRAPE_DEEP", "").lower() in ("1", "true", "yes"):
            folders = walk_folders(str(cid))

        by_id: dict[str, dict] = {}
        for block, payload in [("search", search), ("root", root), ("tree", {"data": folders})]:
            if not isinstance(payload, dict):
                continue
            for item in payload.get("data", []):
                iid = str(item.get("id", ""))
                if not iid:
                    continue
                if iid not in by_id:
                    item["_seenIn"] = [block]
                    by_id[iid] = item
                elif block not in by_id[iid].get("_seenIn", []):
                    by_id[iid].setdefault("_seenIn", []).append(block)

        course_out = {
            "listing": c,
            "meta": meta,
            "searchHits": len(search.get("data", [])) if isinstance(search, dict) else 0,
            "rootItems": len(root.get("data", [])) if isinstance(root, dict) else 0,
            "uniqueItems": len(by_id),
            "items": list(by_id.values()),
        }
        catalog["courses"][str(cid)] = {
            "uniqueItems": course_out["uniqueItems"],
            "searchHits": course_out["searchHits"],
            "title": c.get("title"),
        }
        course_path = os.path.join(OUT_DIR, f"course-{cid}.json")
        with open(course_path, "w", encoding="utf-8") as f:
            json.dump(course_out, f, indent=2)

    catalog["totals"] = {
        "courseCount": len(catalog["courses"]),
        "itemsAllCourses": sum(x["uniqueItems"] for x in catalog["courses"].values()),
    }
    with open(os.path.join(OUT_DIR, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
    print(json.dumps(catalog["totals"], indent=2))


if __name__ == "__main__":
    main()
