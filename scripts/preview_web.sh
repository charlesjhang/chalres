#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-4173}"

echo "Starting preview server at http://localhost:${PORT}/web/index.html"
python3 -m http.server "$PORT"
