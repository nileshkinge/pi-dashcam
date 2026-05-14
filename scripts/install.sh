#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/opt/dashcam"
CONFIG_DIR="/etc/dashcam"
#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="/etc/dashcam"
#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/opt/dashcam"
CONFIG_DIR="/etc/dashcam"
LOG_DIR="/var/log/dashcam"
RECORDINGS_DIR="/var/lib/dashcam/recordings"
SERVICE_FILE="/etc/systemd/system/dashcam.service"
VENV_DIR="$BASE_DIR/venv"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$SCRIPT_DIR"

mkdir -p "$BASE_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$RECORDINGS_DIR"

if ! command -v libcamera-vid >/dev/null 2>&1; then
  echo 'Installing libcamera and camera support packages'
  apt-get update
  apt-get install -y libcamera-apps python3-pip python3-venv python3-yaml python3-serial
fi

# Create Python virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

# Activate venv and install dependencies
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$REPO_ROOT/requirements.txt"
deactivate

cp -r "$REPO_ROOT/app" "$BASE_DIR/app"
mkdir -p "$BASE_DIR/config"
cp -r "$REPO_ROOT/config/"* "$BASE_DIR/config/"
cp "$REPO_ROOT/services/dashcam.service" "$SERVICE_FILE"
chmod 644 "$SERVICE_FILE"

  apt-get update
  apt-get install -y libcamera-apps python3-pip python3-venv python3-yaml python3-serial
fi


python3 -m pip install --upgrade pip
python3 -m pip install -r "$REPO_ROOT/requirements.txt"

cp -r "$REPO_ROOT/app" "$BASE_DIR/app"
mkdir -p "$BASE_DIR/config"
cp -r "$REPO_ROOT/config/"* "$BASE_DIR/config/"
cp "$REPO_ROOT/services/dashcam.service" "$SERVICE_FILE"
chmod 644 "$SERVICE_FILE"

systemctl daemon-reload
systemctl enable dashcam.service
systemctl restart dashcam.service

echo 'Dashcam installation complete.'
