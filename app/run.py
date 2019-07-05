"""
Start up a development server. Don't use in prod.
"""

from tension_analysis import create_app

if __name__ == '__main__':
    app = create_app()
    # Don't use reloader when debugging - our huge preload will be loaded twice!
    # The only cost is that the dev server won't track local code changes. But it's fine!
    app.run(debug=True, host='0.0.0.0', use_reloader=False)
