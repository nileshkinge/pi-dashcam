#!/usr/bin/env bash
set -euo pipefail

DASHCAM_ROOT="/opt/dashcam"
VENV_PYTHON="$DASHCAM_ROOT/venv/bin/python3"
PYTHON="/usr/bin/python3"

if [ ! -d "$DASHCAM_ROOT" ]; then
  echo "Dashcam root not found at $DASHCAM_ROOT"
  exit 1
fi

# Prefer venv Python if available
if [ -x "$VENV_PYTHON" ]; then
  "$VENV_PYTHON" "$DASHCAM_ROOT/app/main.py" --cleanup
else
  $PYTHON "$DASHCAM_ROOT/app/main.py" --cleanup
fi
