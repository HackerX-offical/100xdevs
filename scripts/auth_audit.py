#!/usr/bin/env python3
"""Authenticated checks against course-backend (requires your own session JWT)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass

BASE = os.environ.get("COURSE_API_BASE", "https://course-backend.100xdevs.com").rstrip("/")
TOKEN = os.environ.get("COURSE_API_BEARER", "")
ORIGIN = os.environ.get("COURSE_ORIGIN", "https://100xdevs.com")

if not TOKEN:
    print("Set COURSE_API_BEARER", file=sys.stderr)
    sys.exit(1)


@dataclass
class Finding:
    id: str
    title: str
    severity: str
    evidence: str


def api(method: str, path: str, body: dict | None = None, instance: str | None = None) -> tuple[int, dict]:
    headers = {"Authorization": f"Bearer {TOKEN}", "Origin": ORIGIN, "Accept": "application/json"}
    if instance:
        headers["X-Playback-Instance"] = instance
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw.decode("utf-8", errors="replace")[:500]}


def main() -> int:
    findings: list[Finding] = []

    st, me = api("GET", "/auth/me")
    if st != 200:
        print(f"auth/me failed: {st} {me}")
        return 1
    user = me.get("user", {})
    owned = {str(x["id"]) for x in api("GET", "/purchases")[1].get("data", [])}

    # Slug vs numeric content access
    for cid in list(owned)[:2]:
        st_id, d_id = api("GET", f"/courses/{cid}/content?parentId=-1")
        slug = d_id.get("data") and api("GET", f"/courses/{cid}")[1].get("data", {}).get("slug")
        if slug:
            st_slug, d_slug = api("GET", f"/courses/{slug}/content?parentId=-1")
            if d_id.get("hasAccess") and not d_slug.get("hasAccess"):
                findings.append(
                    Finding(
                        "005",
                        "Slug content route denies entitled users",
                        "Medium",
                        f"course {cid}: id hasAccess={d_id.get('hasAccess')} slug hasAccess={d_slug.get('hasAccess')}",
                    )
                )

    # Unowned course metadata leak
    for unowned in ("24", "21"):
        if unowned in owned:
            continue
        st, d = api("GET", f"/courses/{unowned}/content/search?q=Week&includeExpiredAccess=true")
        n = len(d.get("data", []))
        if n > 20:
            findings.append(
                Finding(
                    "004",
                    "Unpurchased course search leaks module metadata",
                    "Medium",
                    f"course {unowned}: {n} search hits without purchase",
                )
            )

    # Playback gate on unowned numeric video id
    st, d = api("GET", "/courses/24/content?parentId=6911&includeExpiredAccess=true")
    inst = str(uuid.uuid4())
    for item in d.get("data", [])[:3]:
        iid = str(item.get("id", ""))
        if iid.isdigit():
            vst, vout = api("GET", f"/courses/24/video/{iid}?includeExpiredAccess=true", instance=inst)
            if vst == 200 and (vout.get("data") or {}).get("hlsUrl"):
                findings.append(
                    Finding(
                        "playback-bypass",
                        "Unpurchased video HLS exposed",
                        "Critical",
                        f"course 24 video {iid}",
                    )
                )
            break

    out = {
        "userId": user.get("id"),
        "ownedCourseIds": sorted(owned),
        "findings": [f.__dict__ for f in findings],
    }
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "auth-audit.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
