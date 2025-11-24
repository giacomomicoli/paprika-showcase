"""
Health Check Route

Provides application health status endpoint.
"""
from flask import Blueprint, jsonify
from datetime import datetime
from app.config import settings

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with service status and timestamp
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': settings.SERVICE_NAME
    }), 200
