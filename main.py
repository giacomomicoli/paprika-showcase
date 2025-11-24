"""
Application Entry Point

Runs the Flask application server.
"""
from app import create_app
from app.config import settings


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG,
        use_reloader=settings.FLASK_DEBUG
    )
