DEBUG = False

CSV_DELIMITER = ','
CSV_QUOTECHAR = '"'
DATA_ROOT = '/srv/data'
HEDGE_DETECTION_THRESHOLD = 0.8
STORAGE_PATH = '/mnt/tension_analysis_results'
USER_IDENTIFICATION_COOKIE_NAME = 'uid'


import logging  # noqa
logger = logging.getLogger('tension_analysis')
logger.setLevel(logging.INFO)
