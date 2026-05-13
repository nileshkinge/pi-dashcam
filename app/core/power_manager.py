import logging


class PowerManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def prepare_shutdown(self):
        self.logger.debug('PowerManager prepare_shutdown called')

    def monitor(self):
        self.logger.debug('PowerManager monitor called')
