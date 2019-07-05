from pathlib import Path
import shutil

from flask import current_app

CSV_FILENAME = 'result.csv'
TMP_CSV_FILENAME = 'tmp.result.csv'


class open_user_csv_r(object):
    """
    Context manager for storage management.
    Provides a file object for read.
    """
    @property
    def folder_path(self):
        return Path(current_app.config['STORAGE_PATH']) / str(self.user_id)

    @property
    def csv_path(self):
        return self.folder_path / CSV_FILENAME

    def __init__(self, user_id):
        assert user_id, 'user_id cannot be empty'
        self.user_id = user_id
        _remove_if_not_regular_file(self.csv_path)
        self.f = self.csv_path.open(mode='r')

    def __enter__(self):
        return self.f

    def __exit__(self, type, value, traceback):
        self.f.close()


class open_user_csv_w(open_user_csv_r):
    """
    Context manager for storage management.
    Provides a file object for write.
    """
    @property
    def tmp_path(self):
        return self.folder_path / TMP_CSV_FILENAME

    def __init__(self, user_id):
        assert user_id, 'user_id cannot be empty'
        self.user_id = user_id
        if not self.folder_path.is_dir():
            self.folder_path.mkdir(parents=True)
        _remove_if_not_regular_file(self.csv_path)
        _remove_if_not_regular_file(self.tmp_path)
        self.tmp_f = self.tmp_path.open(mode='w')

    def __enter__(self):
        return self.tmp_f

    def __exit__(self, type, value, traceback):
        self.tmp_f.close()
        if not type and not value and not traceback:
            # The file successfully generated. Now replace self.csv_path
            self.tmp_path.rename(self.csv_path)


def _remove_if_not_regular_file(p):
    if p.is_dir() and not p.is_symlink():
        shutil.rmtree(p)
    elif p.is_symlink():
        p.unlink()
