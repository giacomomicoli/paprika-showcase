"""
Paprika Showcase - Simple Flask Application
"""
import sys
from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def home():
    """Home endpoint"""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return jsonify({
        'message': 'Welcome to Paprika Showcase!',
        'status': 'running',
        'python_version': python_version
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
