"""Cross-platform writable user-data paths for LamGo."""
import os
import shutil
import sys
from pathlib import Path

APP_NAME = 'LamGo'


def user_data_dir():
    if sys.platform == 'win32':
        root = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~/AppData/Local')
        path = Path(root) / APP_NAME
    elif sys.platform == 'darwin':
        path = Path.home() / 'Library' / 'Application Support' / APP_NAME
    else:
        root = os.environ.get('XDG_DATA_HOME') or str(Path.home() / '.local' / 'share')
        path = Path(root) / 'lamgo'
    path.mkdir(parents=True, exist_ok=True)
    return path


def user_data_path(filename, legacy_path=None):
    """Return a writable data path, migrating an old project-local file once."""
    target = user_data_dir() / filename
    if not target.exists() and legacy_path:
        old = Path(legacy_path)
        if old.is_file():
            try:
                shutil.copy2(old, target)
            except OSError:
                pass
    return str(target)
