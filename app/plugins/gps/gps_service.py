import logging
import serial
import threading
import time


class GPSService:
    def __init__(self, config, health_monitor):
        self.config = config
        self.health_monitor = health_monitor
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device = self.config['gps'].get('device', '/dev/serial0')
        self.baud_rate = int(self.config['gps'].get('baud_rate', 9600))
        self._stop_event = threading.Event()
        self.current_fix = None

    def run(self):
        self.health_monitor.update_status('gps', 'starting')
        try:
            with serial.Serial(self.device, baudrate=self.baud_rate, timeout=1) as port:
                self.health_monitor.update_status('gps', 'running')
                while not self._stop_event.is_set():
                    line = port.readline().decode('ascii', errors='ignore').strip()
                    if line.startswith('$GPRMC'):
                        self.current_fix = self._parse_rmc(line)
                        self.health_monitor.update_status('gps', 'fix', self.current_fix)
                    time.sleep(0.1)
        except Exception:
            self.logger.exception('GPS service initialization failed')
            self.health_monitor.update_status('gps', 'failed')

    def stop(self):
        self._stop_event.set()

    @staticmethod
    def _parse_rmc(sentence):
        try:
            parts = sentence.split(',')
            if parts[2] != 'A':
                return {'valid': False}
            return {
                'valid': True,
                'timestamp': parts[1],
                'latitude': parts[3],
                'latitude_dir': parts[4],
                'longitude': parts[5],
                'longitude_dir': parts[6],
                'speed_knots': parts[7],
                'track_angle': parts[8],
                'date': parts[9],
            }
        except Exception:
            return {'valid': False}
