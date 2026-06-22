#!/bin/sh
set -eu

BASE_URL="${CYPRESS_BASE_URL:-http://web:8000}"
MAX_ATTEMPTS="${CYPRESS_WAIT_ATTEMPTS:-60}"
SLEEP_SECONDS="${CYPRESS_WAIT_SLEEP:-2}"

echo "Waiting for app at ${BASE_URL} ..."
attempt=1
while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
  if wget -q -O /dev/null "${BASE_URL}/" 2>/dev/null; then
    echo "App is up."
    break
  fi
  if [ "$attempt" -eq "$MAX_ATTEMPTS" ]; then
    echo "Timed out waiting for ${BASE_URL}" >&2
    exit 1
  fi
  attempt=$((attempt + 1))
  sleep "$SLEEP_SECONDS"
done

exec cypress run "$@"
