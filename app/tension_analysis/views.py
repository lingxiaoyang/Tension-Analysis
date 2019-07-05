import traceback

from flask import Blueprint, current_app, g, make_response, redirect, render_template, request, url_for

from .decorators import ensure_user_cookie
from .process import InvalidInput, process
from .storage import open_user_csv_r, open_user_csv_w

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@ensure_user_cookie
def welcome():
    errors = {}
    if request.method == 'POST':
        if 'file' not in request.files:
            errors['file'] = 'File missing'
        else:
            input_fileobj = request.files['file']
            try:
                output_opener = open_user_csv_w(g.user_id)
            except Exception as e:
                errors['file'] = 'Cannot initialize output file. Please report with code: {}.'.format(g.user_id[:6])
                current_app.logger.error(traceback.format_exc())
            else:
                try:
                    with output_opener as output_fileobj:
                        process(input_fileobj, output_fileobj)
                except InvalidInput as e:
                    errors['file'] = str(e)
                    current_app.logger.error(traceback.format_exc())
                except Exception as e:
                    errors['file'] = 'Unexpected error when processing the file: {}'.format(e)
                    current_app.logger.error(traceback.format_exc())
                else:
                    return redirect(url_for('result'))

    return render_template('welcome.html', errors=errors)


@views.route('/result/')
@ensure_user_cookie
def result():
    try:
        opener = open_user_csv_r(g.user_id)
    except Exception:
        return "Requested report does not exist or has expired.", 404
    return "TEST"


@views.route('/result.csv')
@ensure_user_cookie
def result_csv():
    try:
        opener = open_user_csv_r(g.user_id)
    except Exception:
        return "Requested report does not exist or has expired.", 404
    return "TEST"
