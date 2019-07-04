from pathlib import Path

from flask import Blueprint, current_app, g, make_response, render_template, request

from .decorators import ensure_user_cookie

views = Blueprint('views', __name__)

# Result file storage
RESULTS_PATH = Path('/tmp/tension_analysis_results')
if not RESULTS_PATH.is_dir():
    RESULTS_PATH.mkdir(parents=True)


@views.route('/', methods=['GET', 'POST'])
@ensure_user_cookie
def welcome():
    errors = {}
    if request.method == 'POST':
        print(request.files)
        if 'file' not in request.files:
            errors['file'] = 'File missing'
        else:
            input_file = request.files['file']
            print(input_file)
    return render_template('welcome.html', errors=errors)

@views.route('/result/')
@ensure_user_cookie
def result():
    return "TEST"

@views.route('/result.csv')
@ensure_user_cookie
def result_csv():
    return "TEST"
