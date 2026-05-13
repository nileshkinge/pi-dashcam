import logging
import threading
import time


class HealthMonitor:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._statuses = {}
        self._lock = threading.Lock()
        self._last_pulse = {}

    def update_status(self, component, status, details=None):
        with self._lock:
            self._statuses[component] = {
                'status': status,
                'details': details,
                'timestamp': time.time(),
            }
        self.logger.debug('Health update: %s=%s', component, status)

    def pulse(self, component):
        with self._lock:
            self._last_pulse[component] = time.time()
        self.update_status(component, 'alive')

    def get_status(self):
        with self._lock:
            return {**self._statuses}

    def summary(self):
        with self._lock:
            return {
                'components': self._statuses,
                'last_pulse': self._last_pulse,
                'timestamp': time.time(),
            }
