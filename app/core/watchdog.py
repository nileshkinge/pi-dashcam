import logging
import time


class Watchdog:
    def __init__(self, health_monitor, interval_seconds=20):
        self.health_monitor = health_monitor
        self.interval_seconds = interval_seconds
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.logger.info('Watchdog started with interval %ss', self.interval_seconds)
        while True:
            summary = self.health_monitor.summary()
            for component, status in summary['components'].items():
                if status['status'] not in ('alive', 'running', 'recording', 'start'):
                    self.logger.debug('Watchdog component %s status %s', component, status['status'])
            time.sleep(self.interval_seconds)
