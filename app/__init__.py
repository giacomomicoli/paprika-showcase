"""
Application Factory Module

Creates and configures the Flask application.
"""
import os
from flask import Flask, render_template, send_from_directory
from app.routes import health_bp, storyboard_bp, storyboard_stream_bp
from app.config import settings


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(storyboard_bp)
    app.register_blueprint(storyboard_stream_bp)
    
    # Root endpoint - serve the frontend
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Serve output files (generated images and PDFs)
    @app.route('/output/<path:filename>')
    def serve_output(filename):
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        return send_from_directory(output_dir, filename)
    
    return app
