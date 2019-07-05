from pathlib import Path
import shutil

from flask import current_app

__all__ = ['open_user_csv']

CSV_FILENAME = 'result.csv'
TMP_CSV_FILENAME = 'tmp.result.csv'


class CannotOpen(Exception):
    pass


class CannotSave(Exception):
    pass


def open_user_csv(user_id, mode='r'):
    """
    Returns a file object. Expected usage:

      try:
          with open_user_csv(user_id, mode='r') as f:
              f.read()
      except CannotOpen:
          # failed to open the file
      except CannotSave:
          # failed to save the file (if the mode is writable)
      except Exception:
          # other exceptions
    """
    # https://hg.python.org/cpython/file/3.2/Modules/_io/fileio.c#l273
    if 'w' in mode or 'a' in mode or '+' in mode:
        # Initialize with writable logic
        return _open_user_csv_w(user_id, mode)
    else:
        # Initialize with read-only logic
        return _open_user_csv_r(user_id, mode)


def _get_folder_path(user_id):
    return Path(current_app.config['STORAGE_PATH']) / str(user_id)


def _get_csv_path(user_id):
    return _get_folder_path(user_id) / CSV_FILENAME


def _get_tmp_csv_path(user_id):
    return _get_folder_path(user_id) / TMP_CSV_FILENAME


def _remove_if_not_regular_file(p):
    if p.is_dir() and not p.is_symlink():
        shutil.rmtree(p)
    elif p.is_symlink():
        p.unlink()


class _open_user_csv_r(object):
    @property
    def folder_path(self):
        return Path(current_app.config['STORAGE_PATH']) / str(self.user_id)

    @property
    def csv_path(self):
        return self.folder_path / CSV_FILENAME

    def __init__(self, user_id, mode):
        assert user_id, 'user_id cannot be empty'
        self.user_id = user_id
        try:
            _remove_if_not_regular_file(self.csv_path)
            self.f = self.csv_path.open(mode=mode)
        except Exception as e:
            raise CannotOpen from e

    def __enter__(self):
        return self.f

    def __exit__(self, type, value, traceback):
        self.f.close()

    def get_file_object(self):
        return self.f


class _open_user_csv_w(_open_user_csv_r):
    @property
    def tmp_path(self):
        return self.folder_path / TMP_CSV_FILENAME

    def __init__(self, user_id, mode):
        assert user_id, 'user_id cannot be empty'
        self.user_id = user_id
        try:
            if not self.folder_path.is_dir():
                self.folder_path.mkdir(parents=True)
            _remove_if_not_regular_file(self.csv_path)
            _remove_if_not_regular_file(self.tmp_path)
            self.tmp_f = self.tmp_path.open(mode=mode)
        except Exception as e:
            raise CannotOpen from e

    def __enter__(self):
        return self.tmp_f

    def __exit__(self, type, value, traceback):
        self.tmp_f.close()
        if not type and not value and not traceback:
            # The file successfully generated. Now replace self.csv_path
            self.tmp_path.rename(self.csv_path)
