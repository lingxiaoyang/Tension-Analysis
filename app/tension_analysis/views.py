import csv
import traceback

from flask import Blueprint, current_app, g, make_response, redirect, render_template, request, send_file, url_for

from .decorators import ensure_user_cookie
from .process import InvalidInput, process
from .storage import CannotOpen, open_user_csv

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@ensure_user_cookie
def welcome():
    errors = {}
    try:
        with open_user_csv(g.user_id, mode='r') as f:
            pass
    except CannotOpen:
        has_report = False
    else:
        has_report = True

    if request.method == 'POST':
        if 'file' not in request.files:
            errors['file'] = 'File missing'
        else:
            input_fileobj = request.files['file']
            try:
                with open_user_csv(g.user_id, mode='w') as output_fileobj:
                    process(input_fileobj, output_fileobj)
            except CannotOpen as e:
                errors['file'] = 'Cannot initialize output file. Please report with code: {}.'.format(g.user_id[:6])
                current_app.logger.error(traceback.format_exc())
            except InvalidInput as e:
                errors['file'] = str(e)
                current_app.logger.error(traceback.format_exc())
            except Exception as e:
                errors['file'] = 'Unexpected error when processing the file: {}'.format(e)
                current_app.logger.error(traceback.format_exc())
            else:
                return redirect(url_for('views.result'))

    return render_template('welcome.html', errors=errors, has_report=has_report)


@views.route('/result/')
@ensure_user_cookie
def result():
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
        with open_user_csv(g.user_id, mode='r') as f:
            reader = csv.reader(f, delimiter=current_app.config['CSV_DELIMITER'], quotechar=current_app.config['CSV_QUOTECHAR'])
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

    return render_template('result.html', lines=lines, skip=skip, take=take, has_previous_page=has_previous_page, has_next_page=has_next_page)


@views.route('/result.csv')
@ensure_user_cookie
def result_csv():
    try:
        # Don't use with statement because we need to keep the file object open.
        f = open_user_csv(g.user_id, mode='rb').get_file_object()
    except Exception:
        return "Requested report does not exist or has expired.", 404
    else:
        return send_file(f, mimetype='text/csv', attachment_filename='report.csv')
