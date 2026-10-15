# 100xdevs

Research workspace: API probes, JSON snapshots, and findings for 100xdevs surfaces.

## Why this exists

Security research needs reproducible probes and frozen responses. This repo holds scripts, `data/` captures, and narrative findings for authorized review.

## Features

- Python probe scripts under `scripts/`
- Captured JSON under `data/`
- pytest smoke and auth audit tests

## Install

```bash
git clone https://github.com/HackerX-official/100xdevs.git
cd 100xdevs
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

## Quick start

```bash
pytest tests -q
```

## Output

JSON snapshots in `data/` and markdown in `FINDINGS.md`.

## Develop

```bash
pytest tests -q
```

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for module layout and extension points.

## Ethics

Use only on systems and content you are **authorized** to test. See [SECURITY.md](./SECURITY.md).

## License

Licensed under the [HackerX License](./LICENSE). Redistributions must retain copyright,
license text, and [NOTICE](./NOTICE) attribution per the license terms.
