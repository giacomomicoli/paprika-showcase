"""
Application Factory Module

Creates and configures the Flask application.
"""
from flask import Flask
from app.routes import health_bp, storyboard_bp
from app.config import settings


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(storyboard_bp)
    
    # Root endpoint
    @app.route('/')
    def index():
        return 'Hello from Paprika!'
    
    return app
