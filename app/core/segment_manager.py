import datetime
import os
import re
from pathlib import Path

from app.utils.helpers import ensure_directory


class SegmentManager:
    SEGMENT_TEMPLATE = 'segment_{timestamp}.h264'
    SEGMENT_PATTERN = re.compile(r'segment_(\d{8}_\d{6})\.h264$')

    def __init__(self, config):
        self.config = config
        self.recordings_path = Path(self.config['storage']['base_path'])

    def ensure_storage(self):
        return ensure_directory(self.recordings_path)

    def next_segment_path(self):
        timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return self.recordings_path / self.SEGMENT_TEMPLATE.format(timestamp=timestamp)

    def list_segments(self):
        if not self.recordings_path.exists():
            return []
        return sorted(
            [path for path in self.recordings_path.iterdir() if self.SEGMENT_PATTERN.match(path.name)],
            key=lambda p: p.stat().st_mtime,
        )

    def segment_age_seconds(self, path):
        return (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(path.stat().st_mtime)).total_seconds()
