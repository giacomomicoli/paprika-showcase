"""Routes package."""
from app.routes.health import health_bp
from app.routes.storyboard import storyboard_bp
from app.routes.storyboard_stream import storyboard_stream_bp

__all__ = ['health_bp', 'storyboard_bp', 'storyboard_stream_bp']
