#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
report_path="$project_root/results/raw/findsecbugs.sarif"

mkdir -p "$project_root/results/raw"

docker compose --project-directory "$project_root" build scanner
docker compose --project-directory "$project_root" run --rm scanner bash -euo pipefail -c '
  build_root=$(mktemp -d)
  cp -a targets/webgoat "$build_root/webgoat"
  cd "$build_root/webgoat"

  ./mvnw --batch-mode --no-transfer-progress \
    -DskipTests \
    compile \
    dependency:build-classpath \
    -Dmdep.outputFile="$build_root/classpath.txt"

  findsecbugs.sh \
    -sarif \
    -effort:max \
    -low \
    -auxclasspathFromFile "$build_root/classpath.txt" \
    -output /workspace/results/raw/findsecbugs.sarif \
    "$build_root/webgoat/target/classes"
'

jq -e '
  type == "object"
  and .version == "2.1.0"
  and (.runs | type == "array")
  and all(.runs[]?; (.tool.driver.name | type == "string") and (.results | type == "array"))
' "$report_path" >/dev/null

printf 'FindSecBugs report: %s\n' "$report_path"
