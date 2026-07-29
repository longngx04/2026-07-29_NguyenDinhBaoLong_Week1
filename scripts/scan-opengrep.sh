#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
report_path="$project_root/results/raw/opengrep.json"
opengrep_bin="$project_root/scanner/opengrep"
opengrep_url='https://github.com/opengrep/opengrep/releases/download/v1.26.0/opengrep_manylinux_x86'
opengrep_sha256='40c21299eeddabf743b856daa843d24f9d4a027130671cd45b3b21776fd9ab26'

mkdir -p "$project_root/results/raw"

if [[ ! -x "$opengrep_bin" ]] || ! echo "$opengrep_sha256  $opengrep_bin" | sha256sum --check --status; then
  curl --fail --location --retry 5 --retry-all-errors \
    --connect-timeout 30 --max-time 600 \
    --output "$opengrep_bin" "$opengrep_url"
  echo "$opengrep_sha256  $opengrep_bin" | sha256sum --check --status
  chmod 0755 "$opengrep_bin"
fi

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
