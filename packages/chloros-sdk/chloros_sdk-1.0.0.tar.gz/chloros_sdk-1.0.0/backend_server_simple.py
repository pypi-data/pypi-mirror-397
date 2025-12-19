#!/usr/bin/env python3
"""
Simple Backend Server - Development Mode Only
Bypasses missing imports by using mip module directly
"""

import sys
import os

print("🚀 Starting Chloros Backend (Simple Mode)...", flush=True)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('chloros_backend')

# Create Flask app
app = Flask(__name__)
CORS(app)

# Import mip modules
try:
    import mip
    from mip import Index, Calibrate_Images
    print("✅ MIP modules loaded successfully", flush=True)
except Exception as e:
    print(f"❌ Error loading MIP modules: {e}", flush=True)
    sys.exit(1)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

@app.route('/api/info', methods=['GET'])
def get_info():
    """Get backend information"""
    return jsonify({
        'version': '1.0.0',
        'python_version': sys.version,
        'mode': 'development'
    })

# Add more endpoints as needed...

if __name__ == '__main__':
    print("✅ Backend server starting on http://localhost:5000", flush=True)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

