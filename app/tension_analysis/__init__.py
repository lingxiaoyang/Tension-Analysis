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

    try:
        with app.app_context():
            from . import preload  # noqa
    except Exception as e:
        exc_info = "{} {}\n{}\n".format(type(e), e, traceback.format_exc())
        app.logger.error(exc_info)
        return improperly_configured(app, exc_info)

    from .views import views
    app.register_blueprint(views)
    return app


def improperly_configured(app, exc_info):
    """
    Return a premature app serving error messages via HTTP (if debug) instead of failing directly.
    """
    @app.route("/")
    def error_index_page():
        lines = ["Tension Analysis app was improperly configured."]
        if app.debug:
            lines += [exc_info]
        return '\n'.join(lines), {'Content-Type': 'text/plain'}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
