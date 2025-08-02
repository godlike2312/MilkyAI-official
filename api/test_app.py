from flask import Flask, jsonify
from flask_cors import CORS
import os
import time

# Create a minimal Flask app for testing
app = Flask(__name__)
CORS(app, origins=['*'])

@app.route('/')
def index():
    return jsonify({
        'message': 'Hello from NumAI!',
        'status': 'running',
        'timestamp': time.time()
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'environment': os.environ.get('VERCEL_ENV', 'development')
    })

@app.route('/api/test')
def test():
    return jsonify({
        'message': 'Test endpoint working',
        'timestamp': time.time()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True) 