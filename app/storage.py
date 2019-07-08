import logging
from pathlib import Path
import re
import shutil
import uuid

import global_config

logger = logging.getLogger(__name__)


__all__ = ['CannotOpen', 'CannotSave', 'open_user_file', 'add_to_queue', 'take_from_queue', 'NothingTaken']

FILE_CODES = {
    'input': 'input.json',
    'percentage': 'percentage',
    'result': 'result.csv',
}


class CannotOpen(Exception):
    pass


class CannotSave(Exception):
    pass


def open_user_file(user_id, file_code, mode='r'):
    """
    Returns a file object. Expected usage:

      try:
          with open_user_file(user_id, mode='r') as f:
              f.read()
      except CannotOpen:
          # failed to open the file
      except CannotSave:
          # failed to save the file (if the mode is writable)
      except Exception:
          # other exceptions
    """
    assert file_code in FILE_CODES

    # https://hg.python.org/cpython/file/3.2/Modules/_io/fileio.c#l273
    if 'w' in mode or 'a' in mode or '+' in mode:
        # Initialize with writable logic
        return _open_user_file_w(user_id, FILE_CODES[file_code], mode)
    else:
        # Initialize with read-only logic
        return _open_user_file_r(user_id, FILE_CODES[file_code], mode)


def _remove_if_not_regular_file(path):
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.is_symlink():
        path.unlink()


class _open_user_file_r(object):
    @property
    def folder_path(self):
        return Path(global_config.STORAGE_PATH) / str(self.user_id)

    @property
    def file_path(self):
        return self.folder_path / self.file_name

    def __init__(self, user_id, file_name, mode):
        assert user_id, 'user_id cannot be empty'
        self.user_id = user_id
        self.file_name = file_name
        try:
            _remove_if_not_regular_file(self.file_path)
            self.f = self.file_path.open(mode=mode)
        except Exception as e:
            raise CannotOpen from e

    def __enter__(self):
        return self.f

    def __exit__(self, type, value, traceback):
        self.f.close()

    def get_file_object(self):
        return self.f


class _open_user_file_w(_open_user_file_r):
    @property
    def tmp_path(self):
        return self.folder_path / (self.file_name + '.tmp')

    def __init__(self, user_id, file_name, mode):
        assert user_id, 'user_id cannot be empty'
        self.user_id = user_id
        self.file_name = file_name
        try:
            if not self.folder_path.is_dir():
                self.folder_path.mkdir(parents=True)
            _remove_if_not_regular_file(self.file_path)
            _remove_if_not_regular_file(self.tmp_path)
            self.tmp_f = self.tmp_path.open(mode=mode)
        except Exception as e:
            raise CannotSave from e

    def __enter__(self):
        return self.tmp_f

    def __exit__(self, type, value, traceback):
        self.tmp_f.close()
        if not type and not value and not traceback:
            # The file successfully generated. Replace atomically.
            self.tmp_path.rename(self.file_path)


# The process identifier is bound to be unique between workers.
_UUID_REGEX = re.compile('^[0-9a-f]{32}$')
_PROCESS_IDENTIFIER = uuid.uuid4().hex
_QUEUE_FOLDER_PATH = Path(global_config.STORAGE_PATH) / 'queue'
if not _QUEUE_FOLDER_PATH.is_dir():
    _QUEUE_FOLDER_PATH.mkdir(parents=True)


def add_to_queue(user_id):
    item_path = _QUEUE_FOLDER_PATH / str(user_id)
    _remove_if_not_regular_file(item_path)
    try:
        item_path.unlink()
    except Exception:
        pass
    item_path.touch()


class NothingTaken(Exception):
    pass


class take_from_queue(object):
    """
    Usage:
        try:
            with take_from_queue() as user_id:
                do_things(user_id)
        except NothingTaken:
            pass
    """
    def __init__(self):
        self.user_id = None

    def __enter__(self):
        children = [c for c in _QUEUE_FOLDER_PATH.iterdir() if _UUID_REGEX.match(c.name)]
        children.sort(key=lambda c: c.stat().st_mtime)  # old to new
        for c in children:
            if c.is_file():
                try:
                    self.user_id = c.name
                    # Try to lock the file
                    c.rename(c.with_suffix('.' + _PROCESS_IDENTIFIER))
                    break
                except Exception as e:
                    logger.warning(str(e))

        if self.user_id:
            # Verify the lock again
            if (_QUEUE_FOLDER_PATH / (self.user_id + '.' + _PROCESS_IDENTIFIER)).is_file():
                return self.user_id
        raise NothingTaken()

    def __exit__(self, type, value, traceback):
        # Remove the lock
        p = _QUEUE_FOLDER_PATH / (self.user_id + '.' + _PROCESS_IDENTIFIER)
        if p.is_file():
            p.unlink()
