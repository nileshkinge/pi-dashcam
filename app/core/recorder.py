import logging
import os
import shutil
import subprocess
import threading
import time

from pathlib import Path


class Recorder:
    def __init__(self, config, segment_manager, health_monitor, cleanup):
        self.config = config
        self.segment_manager = segment_manager
        self.health_monitor = health_monitor
        self.cleanup = cleanup
        self._stop_event = threading.Event()
        self._process = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def is_alive(self):
        return self._process is not None and self._process.poll() is None

    def run(self):
        self.health_monitor.update_status('recorder', 'starting')
        while not self._stop_event.is_set():
            segment_path = self.segment_manager.next_segment_path()
            self._logger.info('Starting segment %s', segment_path.name)
            self.health_monitor.update_status('recorder', 'starting_segment', str(segment_path.name))

            if not self.segment_manager.ensure_storage():
                self._logger.error('Storage unavailable, retrying in 5 seconds')
                time.sleep(5)
                continue

            self._process = self._start_segment_process(segment_path)
            if not self._process:
                self._logger.error('Recorder failed to start segment process, retrying')
                time.sleep(3)
                continue

            self.health_monitor.update_status('recorder', 'recording', str(segment_path.name))
            self._wait_for_segment_completion()
            self.cleanup.enforce_limits()

        self._stop_subprocess()
        self.health_monitor.update_status('recorder', 'stopped')
        self._logger.info('Recorder stopped')

    def restart(self):
        self.stop()
        self._stop_event.clear()
        runner = threading.Thread(target=self.run, daemon=True)
        runner.start()
        return True

    def stop(self):
        self._stop_event.set()
        self._stop_subprocess()

    def _start_segment_process(self, path: Path):
        camera = self.config['recording'].get('camera_index', 0)
        width = int(self.config['recording'].get('width', 1280))
        height = int(self.config['recording'].get('height', 720))
        framerate = int(self.config['recording'].get('framerate', 25))
        duration = int(self.config['recording'].get('segment_duration_seconds', 60)) * 1000
        bitrate = int(self.config['recording'].get('bitrate', 6000000))
        annotate = self.config['recording'].get('annotate_timestamp', True)

        command = [
            'libcamera-vid',
            f'--width={width}',
            f'--height={height}',
            f'--framerate={framerate}',
            f'--codec={self.config["recording"].get("codec", "h264")}',
            f'--bitrate={bitrate}',
            f'--timeout={duration}',
            f'--output={str(path)}',
        ]

        if annotate:
            command.append('--annotate=%Y-%m-%d %H:%M:%S')

        if camera != 0:
            command.append(f'--camera={camera}')

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                cwd=str(self.segment_manager.recordings_path),
            )
            return process
        except FileNotFoundError:
            self._logger.exception('libcamera-vid not available on this system')
        except Exception:
            self._logger.exception('Failed to start recorder subprocess')
        return None

    def _wait_for_segment_completion(self):
        if not self._process:
            return

        while self._process.poll() is None and not self._stop_event.is_set():
            time.sleep(0.5)

        if self._stop_event.is_set() and self._process.poll() is None:
            self._stop_subprocess()

        if self._process is not None:
            return_code = self._process.poll()
            if return_code != 0:
                stderr = self._process.stderr.read().decode(errors='ignore') if self._process.stderr else ''
                self._logger.warning('Recorder ended with code %s: %s', return_code, stderr.strip())
                self.health_monitor.update_status('recorder', 'error', stderr.strip())
            else:
                self._logger.debug('Segment process finished cleanly')

    def _stop_subprocess(self):
        if self._process is None:
            return
        if self._process.poll() is None:
            try:
                self._logger.info('Stopping recorder subprocess')
                self._process.terminate()
                self._process.wait(timeout=10)
            except Exception:
                self._logger.warning('Recorder subprocess did not terminate cleanly, killing')
                try:
                    self._process.kill()
                except Exception:
                    pass
        self._process = None
