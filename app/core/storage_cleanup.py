import os
import logging
from pathlib import Path

from app.utils.helpers import get_free_space_bytes, remove_file_safe


class StorageCleanup:
    def __init__(self, config, segment_manager):
        self.config = config
        self.segment_manager = segment_manager
        self.logger = logging.getLogger(self.__class__.__name__)

    def enforce_limits(self):
        self.logger.debug('Enforcing retention policies')
        self._prune_segments_by_count()
        self._prune_segments_by_size()
        self._prune_available_space()

    def _prune_segments_by_count(self):
        max_segments = int(self.config['retention'].get('max_segments', 300))
        segments = self.segment_manager.list_segments()
        if len(segments) <= max_segments:
            return
        for segment in segments[: len(segments) - max_segments]:
            self.logger.info('Removing old segment by count: %s', segment.name)
            remove_file_safe(segment)

    def _prune_segments_by_size(self):
        target_size = float(self.config['retention'].get('max_size_gb', 16)) * 1024**3
        segments = self.segment_manager.list_segments()
        total_size = sum(seg.stat().st_size for seg in segments)
        while segments and total_size > target_size:
            oldest = segments.pop(0)
            self.logger.info('Removing old segment by size: %s', oldest.name)
            total_size -= oldest.stat().st_size
            remove_file_safe(oldest)

    def _prune_available_space(self):
        min_free = float(self.config['retention'].get('min_free_space_gb', 1)) * 1024**3
        free_space = get_free_space_bytes(self.segment_manager.recordings_path)
        if free_space >= min_free:
            return
        self.logger.warning('Low free space: %s bytes, pruning oldest segments', free_space)
        segments = self.segment_manager.list_segments()
        while segments and free_space < min_free:
            oldest = segments.pop(0)
            self.logger.info('Removing segment to free space: %s', oldest.name)
            free_space += oldest.stat().st_size
            remove_file_safe(oldest)
