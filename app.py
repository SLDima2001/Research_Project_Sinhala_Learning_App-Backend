"""
Sinhala Learning Unified API
Combined Backend for:
1. Handwriting Recognition (454 Classes)
2. User Authentication (MongoDB + JWT)
3. Gamified Storytelling (Stories & Quizzes)
4. Text-to-Image (OCR + Real Image Search)
"""

import os
import sys
import json
import base64
import random
import traceback
import datetime
from io import BytesIO
from typing import Tuple, Dict, Optional, List

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

# External Module Imports (Blueprints)
try:
    from auth import auth_bp
    from stories import stories_bp
    from text_to_image import text_to_image_bp
except ImportError as e:
    print(f"Warning: Could not import some module blueprints: {e}")

# Internal Model Import
try:
    from sinhala_model import SinhalaHandwritingModel
except ImportError:
    print("Warning: SinhalaHandwritingModel class not found in sinhala_model.py")

# Initialize Flask app
app = Flask(__name__)
app.json.ensure_ascii = False  # Support Sinhala characters in JSON
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(stories_bp, url_prefix='/api')
app.register_blueprint(text_to_image_bp, url_prefix='/api/ti')

# ============================================================
# CONFIGURATION
# ============================================================
PORT = int(os.environ.get("PORT", 5000))
user_sessions = {}

# Primary Handwriting Model Initialization
try:
    model = SinhalaHandwritingModel()
    print("✓ Primary Handwriting Model (454 classes) Initialized")
except Exception as e:
    print(f"✗ Failed to load Primary Handwriting Model: {e}")
    model = None

# Sinhala character mapping (Truncated for brevity, normally loads from info.json)
SINHALA_LETTERS = {
    0: {"name": "අ", "romanized": "a"},
    1: {"name": "ආ", "romanized": "ā"},
    2: {"name": "ඇ", "romanized": "æ"},
    3: {"name": "ඈ", "romanized": "ǣ"},
    4: {"name": "ඉ", "romanized": "i"},
    # Full mapping can be loaded from models/sinhala_model_info.json automatically by the model class
}

# ============================================================
# UTILITIES / ERROR HANDLING
# ============================================================
@app.errorhandler(Exception)
def handle_error(error):
    print(f"ERROR: {str(error)}")
    traceback.print_exc()
    status_code = getattr(error, 'code', 500)
    return jsonify({
        'success': False,
        'message': str(error),
        'error': error.__class__.__name__
    }), status_code

# ============================================================
# CORE ENDPOINTS
# ============================================================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'success': True,
        'message': 'Sinhala Learning Unified API - v3.0',
        'status': 'Online',
        'endpoints': [
            '/api/auth/*', '/api/stories', '/api/quiz/submit',
            '/api/predict', '/api/get-random-letter',
            '/api/ti/generate-image', '/api/ti/ocr-and-generate'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'success': True,
        'status': 'healthy',
        'models_loaded': model.model_loaded if model else False
    })

# ============================================================
# HANDWRITING MODULE ROUTES
# ============================================================
@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict Sinhala character from handwritten image"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'success': False, 'message': 'No image data provided'}), 400
        
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        if model and model.model_loaded:
            prediction = model.predict(image)
            return jsonify({
                'success': True,
                'prediction': {
                    'class': prediction['predicted_class'],
                    'character': prediction['top_3'][0]['letter'] if prediction['top_3'] else "Unknown",
                    'confidence': prediction['confidence']
                }
            })
        else:
            # Mock for development
            return jsonify({
                'success': True,
                'prediction': {'class': 0, 'character': 'mock', 'confidence': 0.99},
                'mock': True
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/get-random-letter', methods=['GET'])
def get_random_letter():
    user_id = request.args.get('user_id', 'anonymous')
    letter_id = random.randint(0, 453) # 454 classes
    return jsonify({
        'success': True,
        'letter': {'id': letter_id, 'character': 'අ', 'romanized': 'a'}
    })

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print(f"Unified Sinhala Learning API running on http://0.0.0.0:{PORT}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=PORT, debug=True)
