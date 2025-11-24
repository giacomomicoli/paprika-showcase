"""
Paprika Showcase - Simple Flask Application
"""
from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Welcome to Paprika Showcase!',
        'status': 'running',
        'python_version': '3.10'
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
