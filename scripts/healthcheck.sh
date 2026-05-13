#!/usr/bin/env bash
set -euo pipefail

HOST="127.0.0.1"
PORT="8080"
URL="http://${HOST}:${PORT}/health"

if command -v curl >/dev/null 2>&1; then
  curl --max-time 5 --fail "$URL"
else
  echo 'curl is required for healthcheck'
  exit 1
fi
