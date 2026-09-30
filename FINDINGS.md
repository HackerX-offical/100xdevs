# Findings — 100xdevs course API

**When:** September 2026  
**Targets:** `100xdevs.com`, `course-backend.100xdevs.com`  
**Stack (recon):** Vite/React SPA, Express API, Bunny CDN for HLS (`transcoded-video.b-cdn.net`)

This is a hobby recon write-up. Severity labels are my opinion, not a formal rating.

---

## Summary

| ID | Issue | Severity |
|----|--------|----------|
| 001 | Unauthenticated OTP send to arbitrary emails | Medium |
| 007 | Peer `author.id` (CUID) + name in comments | Medium |
| 005 | Slug vs numeric course id on `/content` | Medium |
| 008 | Global content search requires auth; per-course search does not | Medium |
| 004 | Unauthenticated preview syllabus metadata | Low–Medium |
| 006 | Paid video id oracle (401/403 vs 404) | Low |
| 002 | `X-Powered-By: Express` | Low |
| 003 | Unauthenticated `POST /affiliate/visit` | Low |

**Did not break (from my tests):** paid HLS without purchase, JWT tampering, learner JWT on `/admin/*`, `purchases?userId=` IDOR, checkout amount tampering, open CDN URLs without session.

---

## 001 — OTP spam surface

`POST /auth/otp/send` with `{"email":"..."}` returns `200` / “Code sent” with no CAPTCHA. Per-email cooldown ~60s; rotate emails to abuse.

```http
POST /auth/otp/send
{"email":"someone@example.com"}
```

---

## 004 — Open per-course content tree (metadata only)

Without `Authorization`:

- `GET /courses/{id}/content/search?q=Week&includeExpiredAccess=true`
- `GET /courses/{id}/content?parentId=…&includeExpiredAccess=true`

Returns preview rows: titles, durations, `preview_*` ids, folder `parentId`. **Does not** hand out paid video streams — numeric video ids still `401`/`403`. Evidence dataset: `data/public-content/`, script: `scripts/scrape_public_content.py`, shell: `proofs/unauth-content-search.sh`.

---

## 005 — Slug breaks entitled content listing

For owned courses, `GET /courses/14/content` works; `GET /courses/complete-web-development-…/content` can return `hasAccess: false` and empty `data` with the same account.

---

## 006 — Video existence oracle

`GET /courses/{courseId}/video/{videoId}` — real but unpaid id → purchase error; bogus id → 404. Helps enumeration, not playback.

---

## 007 — Comment author ids

`GET /comments?contentItemId=…` (needs login + purchase on that lecture) returns `author.id` and `author.name` for peers. Sampled via `scripts/comment_peer_enum.py` → `data/comment-peer-enum.json`.

---

## 008 — Inconsistent search auth

| Endpoint | No bearer |
|----------|-----------|
| `/courses/24/content/search?q=…` | 200 |
| `/courses/content/search?q=…` | 401 |

---

## Architecture (short)

| Layer | Host |
|--------|------|
| SPA | `100xdevs.com` |
| API | `course-backend.100xdevs.com` |
| Video | `transcoded-video.b-cdn.net` (403 without valid session) |

Playback (when you own the course): `GET /courses/{courseId}/video/{videoId}?includeExpiredAccess=true` + header `X-Playback-Instance: <uuid>` → `hlsUrl` in JSON.

Admin routes return `401 Admin verification required` with a normal learner token (`data/admin-fuzz.json`).

---

## Scripts

| Script | Purpose |
|--------|---------|
| `probe_api.py` | Route coverage |
| `scrape_public_content.py` | Unauthenticated metadata harvest |
| `auth_audit.py` | Authenticated checks |
| `admin_fuzz.py` | Admin path map (401s) |
| `comment_peer_enum.py` | Comment author sampling |

Set `COURSE_API_BEARER` in `.env` for authenticated runs.
