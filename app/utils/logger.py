import logging
from logging.handlers import RotatingFileHandler


def setup_logging(config):
    log_config = config.get('logging', {})
    log_path = log_config.get('path', '/var/log/dashcam/dashcam.log')
    level = getattr(logging, log_config.get('level', 'INFO').upper(), logging.INFO)
    max_bytes = log_config.get('max_bytes', 5 * 1024 * 1024)
    backup_count = log_config.get('backup_count', 3)

    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')

    handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger
