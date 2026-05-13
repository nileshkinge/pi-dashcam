import os
import shutil


def ensure_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False


def format_bytes(bytes_count):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(bytes_count) < 1024.0:
            return f'{bytes_count:3.1f}{unit}'
        bytes_count /= 1024.0
    return f'{bytes_count:.1f}PB'


def get_free_space_bytes(path):
    try:
        stat = os.statvfs(path)
        return stat.f_bavail * stat.f_frsize
    except OSError:
        return 0


def remove_file_safe(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            return True
    except OSError:
        pass
    return False


def atomic_move(src, dst):
    try:
        shutil.move(src, dst)
        return True
    except OSError:
        return False
