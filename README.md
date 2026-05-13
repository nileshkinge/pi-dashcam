# Raspberry Pi Dashcam Appliance

A production-oriented dashcam architecture for Raspberry Pi Zero W using hardware-accelerated libcamera recording and modular optional services.

## Project Structure

- `app/` - core recording engine, modules, and optional services
- `config/settings.yaml` - runtime configuration and retention policy
- `services/dashcam.service` - systemd unit for boot startup and supervision
- `scripts/` - install and maintenance utilities
- `recordings/` - local segment storage during development
- `logs/` - rotated log output during development
- `requirements.txt` - Python dependencies

## Design Principles

- Recording engine is sacred: optional services cannot stop video capture
- Hardware-accelerated H264 capture via `libcamera-vid`
- 1-minute rolling segments with storage pruning
- Safe recovery after reboot and unexpected failures
- Lightweight REST API isolated from recorder
- GPS and other features are optional and fail safely

## Features

- Continuous segment recording with safe rollover
- Automatic cleanup based on segment count, disk usage, and free space
- Timestamp overlay on all recordings
- Systemd-managed startup and restart supervision
- Modular plugin architecture for GPS and API support
- Embedded-first design for Pi Zero W

## Installation

1. Copy or clone this repo to Raspberry Pi OS:

```bash
cd /home/pi
git clone <repo-url> dashcam
cd dashcam
```

2. Make installer executable and run it:

```bash
sudo chmod +x scripts/install.sh
sudo scripts/install.sh
```

3. The service will be enabled and restarted automatically.

## Configuration

Edit `config/settings.yaml` before deployment.

- `storage.base_path` controls where recordings are stored
- `retention.max_segments` and `retention.max_size_gb` enforce rolling retention
- `api.enabled` turns the lightweight REST API on or off
- `gps.enabled` enables optional GPS support

## Runtime

The recorder is designed to run as a systemd service at boot. For development:

```bash
python3 app/main.py
```

For one-time cleanup:

```bash
sudo scripts/cleanup.sh
```

## Deployment Notes

- Use `libcamera-vid` for hardware H264 encoding
- Prefer a USB storage volume when available; fallback to SD card is handled by path configuration
- Keep segment duration short to minimize corruption risk during power loss
- Avoid heavy binaries and GUI frameworks on Pi Zero W

## Future Extensions

The architecture supports clean integration of:
- emergency clip locking
- Android companion app endpoints
- parking mode and motion-triggered recording
- secondary cameras and low-resolution preview
- hotspot/captive portal support

## License

MIT License
