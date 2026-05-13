#!/usr/bin/env bash
set -euo pipefail

DASHCAM_ROOT="/opt/dashcam"
PYTHON="/usr/bin/python3"

if [ ! -d "$DASHCAM_ROOT" ]; then
  echo "Dashcam root not found at $DASHCAM_ROOT"
  exit 1
fi

$PYTHON "$DASHCAM_ROOT/app/main.py" --cleanup
