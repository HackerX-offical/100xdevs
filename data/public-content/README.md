# Unauthenticated content metadata scrape

**Source:** `course-backend.100xdevs.com` with no `Authorization` header.

```bash
python3 scripts/scrape_public_content.py
# optional: SCRAPE_DEEP=true for slow folder recursion
```

Titles, `preview_*` ids, durations — not video files or HLS URLs.

| File | Description |
|------|-------------|
| `catalog.json` | Index + counts |
| `course-*.json` | Items per cohort |
