import json
import logging
import traceback

from storage import CannotOpen, CannotSave, open_user_file

from .process import tension_analysis


logger = logging.getLogger(__name__)


def task_tension_analysis(user_id):
    # Import inline to avoid web thread loading all dependencies
    try:
        with open_user_file(user_id, 'input', mode='r') as f:
            questions_answers = json.load(f)
    except CannotOpen:
        _write_error(user_id, 'Cannot open input file. Please report with code {}'.format(user_id[:6]))
        logger.error(traceback.format_exc())
    except Exception as e:
        _write_error(user_id, 'Cannot read input file. Please report with code {}'.format(user_id[:6]))
        logger.error(traceback.format_exc())
    else:
        def update_percentage(percentage):
            with open_user_file(user_id, 'percentage', mode='w') as f1:
                f1.write(str(percentage))
        try:
            with open_user_file(user_id, 'result', mode='w') as f2:
                tension_analysis(questions_answers, f2, update_percentage)
        except CannotSave:
            _write_error(user_id, 'Cannot initialize output file. Please report with code {}'.format(user_id[:6]))
            logger.error(traceback.format_exc())
        except Exception as e:
            _write_error(
                user_id,
                'Unexpected error during processing: {}. '
                'Please report with code {}'.format(e, user_id[:6]))
            logger.error(traceback.format_exc())
        else:
            update_percentage(100)


def _write_error(user_id, error_string):
    with open_user_file(user_id, 'percentage', mode='w') as f:
        f.write(error_string)
