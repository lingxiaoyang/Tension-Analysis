import logging
import time
import traceback

from storage import take_from_queue, NothingTaken
from tension_analysis_worker import task_tension_analysis

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('Worker ready.')
    while True:
        try:
            with take_from_queue() as user_id:
                logger.info('Taking {}'.format(user_id))
                task_tension_analysis(user_id)
        except NothingTaken:
            time.sleep(2)
        except Exception as e:
            logger.error('Unexpected exception:')
            logger.error(traceback.format_exc())
