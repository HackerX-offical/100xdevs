# 100xdevs.com — casual API security notes

Personal weekend recon on [100xdevs](https://100xdevs.com/) and `course-backend.100xdevs.com`. Not a formal pentest deliverable — just scripts, raw probe output, and write-ups of what looked interesting.

**Write-up:** [FINDINGS.md](./FINDINGS.md)

## Quick start

```bash
cp .env.example .env
# Optional: paste a session JWT from your own account for authenticated probes
export COURSE_API_BEARER='...'

python3 scripts/probe_api.py
python3 scripts/scrape_public_content.py   # unauthenticated syllabus metadata
```

## Repo layout

```
├── FINDINGS.md              # What I found (and what did not break)
├── data/
│   ├── api-coverage.json    # Route probe snapshot
│   ├── public-content/      # Unauthenticated metadata scrape
│   └── *.json               # Other probe outputs
├── scripts/                 # Python helpers
└── proofs/                  # One-liner repro shells
```

## Disclaimer

Test only systems you are allowed to test. These scripts default to read-only probing. Do not use findings to harass users, spam OTPs, or bypass paywalls.
