#!/usr/bin/env bash
set -euo pipefail

required=(
  "sql/schema.sql"
  "sql/views.sql"
  "sql/queries.sql"
  "sql/seed.sql"
  "docs/setup.md"
  "docs/kpi_dictionary.md"
  "automations/README.md"
)

for file in "${required[@]}"; do
  if [[ ! -s "$file" ]]; then
    echo "[ERROR] Missing or empty: $file"
    exit 1
  fi
  echo "[OK] $file"
done

echo "All SQL/doc assets exist and are non-empty."
