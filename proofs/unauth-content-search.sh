#!/usr/bin/env bash
# Unauthenticated syllabus metadata (no secrets).
set -euo pipefail
BASE="${COURSE_API_BASE:-https://course-backend.100xdevs.com}"

echo "=== search (no Authorization) ==="
curl -s "${BASE}/courses/24/content/search?q=Week&includeExpiredAccess=true" \
  -H 'Origin: https://100xdevs.com' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('count', len(d.get('data',[]))); print('first title', d['data'][0]['title'][:80])"

echo "=== folder listing (no Authorization) ==="
curl -s "${BASE}/courses/24/content?parentId=6911&includeExpiredAccess=true" \
  -H 'Origin: https://100xdevs.com' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('hasAccess', d.get('hasAccess'), 'count', len(d.get('data',[])))"
