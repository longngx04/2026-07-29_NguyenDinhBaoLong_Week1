#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
report_path="$project_root/results/raw/opengrep.json"

mkdir -p "$project_root/results/raw"

docker compose --project-directory "$project_root" build scanner
docker compose --project-directory "$project_root" run --rm scanner \
  opengrep scan \
  --config rules/opengrep \
  --exclude 'target/**' \
  --json \
  --output results/raw/opengrep.json \
  targets/webgoat

jq -e '
  type == "object"
  and (.results | type == "array")
  and (.errors | type == "array")
  and all(.results[]?; (.path | startswith("targets/webgoat/")))
' "$report_path" >/dev/null

printf 'OpenGrep report: %s\n' "$report_path"
