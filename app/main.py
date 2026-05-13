import argparse
import logging
import os
import signal
import sys
import threading
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.health_monitor import HealthMonitor
from app.core.recorder import Recorder
from app.core.segment_manager import SegmentManager
from app.core.storage_cleanup import StorageCleanup
from app.plugins.gps.gps_service import GPSService
from app.plugins.webapi.api_server import APIServer
from app.utils.config_loader import ConfigLoader
from app.utils.logger import setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(description='Dashcam appliance runtime')
    parser.add_argument('--cleanup', action='store_true', help='Run one-time storage cleanup and exit')
    args = parser.parse_args()
    config = ConfigLoader.load('config/settings.yaml')
    logger = setup_logging(config)
    logger.info('Dashcam starting')

    segment_manager = SegmentManager(config)
    storage_cleanup = StorageCleanup(config, segment_manager)
    health_monitor = HealthMonitor(config)

    if not segment_manager.ensure_storage():
        logger.error('Storage initialization failed, exiting')
        return 1

    storage_cleanup.enforce_limits()

    if args.cleanup:
        logger.info('Cleanup mode requested; exiting after pruning storage')
        return 0

    recorder = Recorder(config, segment_manager, health_monitor, storage_cleanup)
    recorder_thread = threading.Thread(target=recorder.run, name='RecorderThread', daemon=True)
    recorder_thread.start()

    services = []

    if config.get('api', {}).get('enabled', True):
        try:
            api_service = APIServer(config, segment_manager, health_monitor)
            api_thread = threading.Thread(target=api_service.run, name='APIServerThread', daemon=True)
            api_thread.start()
            services.append((api_service, api_thread))
            logger.info('Web API service started')
        except Exception:
            logger.exception('Failed to start Web API service; continuing without it')

    if config.get('gps', {}).get('enabled', False):
        try:
            gps_service = GPSService(config, health_monitor)
            gps_thread = threading.Thread(target=gps_service.run, name='GPSServiceThread', daemon=True)
            gps_thread.start()
            services.append((gps_service, gps_thread))
            logger.info('GPS service started')
        except Exception:
            logger.exception('Failed to start GPS service; continuing without it')

    stop_event = threading.Event()

    def handle_signal(signum, frame):
        logger.info('Received shutdown signal=%s', signum)
        stop_event.set()
        recorder.stop()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        while not stop_event.is_set():
            health_monitor.pulse('main_loop')
            if not recorder.is_alive():
                logger.warning('Recorder thread is not alive, attempting restart')
                if not recorder.restart():
                    logger.error('Recorder failed to restart, keeping service alive for manual recovery')
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt received')
        recorder.stop()
    finally:
        recorder.stop()
        logger.info('Dashcam stopped')

    return 0


if __name__ == '__main__':
    sys.exit(main())
