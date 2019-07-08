"""
The entrypoint of tension analysis app.
"""
from flask import Flask


def create_app():
    """
    The entrypoint: factory the Flask app to share with multiple instances.
    """
    app = Flask(__name__)
    app.config.from_object('global_config')

    from .views import views
    app.register_blueprint(views)
    return app
