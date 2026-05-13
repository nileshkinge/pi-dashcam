import os
import yaml


class ConfigLoader:
    DEFAULTS = {
        'recording': {
            'width': 1280,
            'height': 720,
            'framerate': 25,
            'segment_duration_seconds': 60,
            'codec': 'h264',
            'bitrate': 6000000,
            'annotate_timestamp': True,
            'camera_index': 0,
        },
        'storage': {
            'base_path': '/var/lib/dashcam/recordings',
            'preferred': ['usb', 'sd'],
        },
        'retention': {
            'max_segments': 300,
            'max_size_gb': 16,
            'min_free_space_gb': 1,
        },
        'logging': {
            'path': '/var/log/dashcam/dashcam.log',
            'level': 'INFO',
            'max_bytes': 5 * 1024 * 1024,
            'backup_count': 3,
        },
        'api': {
            'enabled': True,
            'host': '0.0.0.0',
            'port': 8080,
        },
        'gps': {
            'enabled': False,
            'device': '/dev/serial0',
            'baud_rate': 9600,
        },
    }

    @classmethod
    def load(cls, path):
        config = cls.DEFAULTS.copy()

        try:
            with open(path, 'r', encoding='utf-8') as handle:
                user_config = yaml.safe_load(handle) or {}
                cls.merge(config, user_config)
        except FileNotFoundError:
            if not os.path.isabs(path):
                alt_path = '/etc/dashcam/settings.yaml'
                if os.path.exists(alt_path):
                    with open(alt_path, 'r', encoding='utf-8') as handle:
                        user_config = yaml.safe_load(handle) or {}
                        cls.merge(config, user_config)
        except Exception:
            raise

        env_base = os.getenv('DASHCAM_RECORDINGS_PATH')
        if env_base:
            config['storage']['base_path'] = env_base

        return config

    @staticmethod
    def merge(base, override):
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                ConfigLoader.merge(base[key], value)
            else:
                base[key] = value
