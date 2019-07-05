"""
The entrypoint of tension analysis app.
"""
import traceback

from flask import Flask


def create_app():
    """
    The entrypoint: factory the Flask app to share with multiple instances.
    """
    app = Flask(__name__)
    app.config.from_object('config')

    if not app.config['DATA_ROOT'].endswith('/'):
        app.config['DATA_ROOT'] += '/'

    if not hasattr(app, 'preload'):
        app.preload = {}

    try:
        with app.app_context():
            from . import preload  # noqa
    except Exception as e:
        exc_info = "{} {}\n{}\n".format(type(e), e, traceback.format_exc())
        app.logger.error(exc_info)
        raise

    from .views import views
    app.register_blueprint(views)
    return app
