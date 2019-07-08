import csv
import json
import traceback

from flask import Blueprint, current_app, g, redirect, render_template, request, send_file, url_for

import global_config
from storage import CannotOpen, CannotSave, add_to_queue, open_user_file

from .decorators import ensure_user_cookie
from .preprocessing import Preprocessor

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@ensure_user_cookie
def welcome():
    errors = {}
    # Percentage:
    #   -1:   No previous report
    #   0:    Scheduled
    #   1-99: In progress
    #   100:  Done
    #   Error message
    try:
        with open_user_file(g.user_id, 'percentage', mode='r') as f:
            percentage = f.read()
            percentage = int(percentage)
    except CannotOpen:
        percentage = -1
    except ValueError:
        pass  # leave percentage as a string

    if isinstance(percentage, str):
        status = 'FAILED'
        message = 'Last report failed. Details: {}'.format(percentage)
    elif percentage == -1:
        status = 'NEW'
        message = 'To start, submit an input file for processing.'
    elif percentage == 0:
        status = 'SCHEDULED'
        message = 'Your last report is scheduled.'
    elif 1 <= percentage <= 99:
        status = 'WIP'
        message = 'Your report is working in progress.'
    elif percentage == 100:
        status = 'READY'
        message = 'Your report is ready.'
    else:
        status = 'UNKNOWN'
        message = 'unknown status {}'.format(percentage)

    if request.method == 'POST':
        if 'file' not in request.files:
            errors['file'] = 'Please upload a file.'
        else:
            input_fileobj = request.files['file']
            try:
                processor = Preprocessor(input_fileobj)
                processor.process_html()
                questions_answers = processor.extract_ques_ans()
            except Exception as e:
                errors['file'] = 'Your file is not in the right format. Please provide valid file.'
                current_app.logger.error(traceback.format_exc())
            else:
                try:
                    with open_user_file(g.user_id, 'input', mode='w') as f1:
                        with open_user_file(g.user_id, 'percentage', mode='w') as f2:
                            json.dump(questions_answers, f1)
                            f2.write('0')
                    add_to_queue(g.user_id)
                except CannotSave as e:
                    errors['file'] = 'Cannot initialize output file. Please report with code: {}.'.format(g.user_id[:6])
                    current_app.logger.error(traceback.format_exc())
                else:
                    return redirect(url_for('views.result'))

    return render_template('welcome.html', errors=errors, status=status, message=message)


@views.route('/result/')
@ensure_user_cookie
def result():
    try:
        with open_user_file(g.user_id, 'percentage', mode='r') as f:
            percentage = f.read()
            percentage = int(percentage)
    except CannotOpen:
        percentage = -1
    except ValueError:
        pass  # leave percentage as a string
    if percentage != 100:
        return render_template('wait_for_result.html', percentage=percentage)

    try:
        skip = int(request.args.get('skip'))
        assert skip >= 0
    except Exception:
        skip = 0

    try:
        take = int(request.args.get('take'))
        assert take > 0
    except Exception:
        take = 50

    end = skip + take

    lines = []
    has_previous_page = (skip > 0)
    has_next_page = False

    try:
        with open_user_file(g.user_id, 'result', mode='r') as f:
            reader = csv.reader(f, delimiter=global_config.CSV_DELIMITER, quotechar=global_config.CSV_QUOTECHAR)
            next(reader)  # skip header

            for i, line in enumerate(reader):
                if skip <= i < end:
                    try:
                        lines.append([i + 1] + line[:3])
                    except Exception:
                        lines.append(['ERROR', '', '', ''])
                elif i == end:
                    has_next_page = True
                    break
    except CannotOpen as e:
        return "Requested report does not exist or has expired.", 404

    return render_template(
        'result.html',
        lines=lines, skip=skip, take=take,
        has_previous_page=has_previous_page, has_next_page=has_next_page
    )


@views.route('/result.csv')
@ensure_user_cookie
def result_csv():
    try:
        # Don't use with statement because we need to keep the file object open.
        f = open_user_file(g.user_id, 'result', mode='rb').get_file_object()
    except Exception:
        return "Requested report does not exist or has expired.", 404
    else:
        return send_file(f, mimetype='text/csv', attachment_filename='report.csv')
