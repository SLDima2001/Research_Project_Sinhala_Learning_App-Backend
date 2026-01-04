"""
Flask API for Sinhala Handwriting Recognition - 454 Classes
Enhanced with User Authentication
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import cv2
import base64
from io import BytesIO
from PIL import Image
import os
import sys
from datetime import datetime
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the model
from sinhala_model import SinhalaHandwritingModel

# Import auth blueprint
from auth import auth_bp

# Initialize Flask app
app = Flask(__name__)
app.json.ensure_ascii = False  # Ensure correct encoding for Sinhala characters
CORS(app)  # Enable CORS for all routes

# Initialize the model
model = SinhalaHandwritingModel()

# Sinhala character mapping (454 classes)
SINHALA_LETTERS = {
    0: {"name": "අ", "romanized": "a"},
    1: {"name": "ආ", "romanized": "ā"},
    2: {"name": "ඇ", "romanized": "æ"},
    3: {"name": "ඈ", "romanized": "ǣ"},
    4: {"name": "ඉ", "romanized": "i"},
    5: {"name": "ඊ", "romanized": "ī"},
    6: {"name": "උ", "romanized": "u"},
    7: {"name": "ඌ", "romanized": "ū"},
    8: {"name": "ඍ", "romanized": "r̥"},
    9: {"name": "ඎ", "romanized": "r̥̄"},
    10: {"name": "ඏ", "romanized": "l̥"},
    11: {"name": "ඐ", "romanized": "l̥̄"},
    12: {"name": "එ", "romanized": "e"},
    13: {"name": "ඒ", "romanized": "ē"},
    14: {"name": "ඓ", "romanized": "ai"},
    15: {"name": "ඔ", "romanized": "o"},
    16: {"name": "ඕ", "romanized": "ō"},
    17: {"name": "ඖ", "romanized": "au"},
    18: {"name": "ක", "romanized": "ka"},
    19: {"name": "ඛ", "romanized": "kha"},
    20: {"name": "ග", "romanized": "ga"},
    # ... Add all 454 classes here (truncated for brevity)
}

# Session storage for user practice
user_sessions = {}

# Register auth blueprint
app.register_blueprint(auth_bp, url_prefix='/api/auth')


# Global error handler to return JSON instead of HTML
@app.errorhandler(Exception)
def handle_error(error):
    """Handle all errors and return JSON response"""
    import traceback
    print(f"Error occurred: {str(error)}")
    print(traceback.format_exc())
    
    # Get status code if it's an HTTP exception
    status_code = getattr(error, 'code', 500)
    
    return jsonify({
        'success': False,
        'message': str(error),
        'error': error.__class__.__name__
    }), status_code



@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        'success': True,
        'message': 'Sinhala Handwriting Recognition API',
        'version': '2.0',
        'endpoints': [
            '/api/auth/register',
            '/api/auth/login',
            '/api/auth/verify',
            '/api/auth/me',
            '/api/predict',
            '/api/health',
            '/api/get-random-letter',
            '/api/get-all-letters'
        ]
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'message': 'API is running',
        'model_loaded': model.model_loaded if model.model_loaded else False
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict Sinhala character from handwritten image"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'success': False, 'message': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Preprocess image
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # Resize to model input size (assuming 64x64)
        image_array = cv2.resize(image_array, (64, 64))
        image_array = image_array.reshape(1, 64, 64, 1) / 255.0
        
        # Make prediction
        if model.model_loaded:
            prediction = model.predict(image_array)
            predicted_class = int(np.argmax(prediction))
            confidence = float(np.max(prediction))
        else:
            # Mock prediction for testing
            predicted_class = random.randint(0, min(len(SINHALA_LETTERS) - 1, 453))
            confidence = random.uniform(0.7, 0.99)
        
        # Get character info
        letter_info = SINHALA_LETTERS.get(predicted_class, {"name": "Unknown", "romanized": "unknown"})
        
        return jsonify({
            'success': True,
            'prediction': {
                'class': predicted_class,
                'character': letter_info['name'],
                'romanized': letter_info['romanized'],
                'confidence': confidence
            },
            'score': confidence * 100,  # Add score for frontend (0-100)
            'feedback': f"Good job! Recognized as {letter_info['name']}" if confidence > 0.7 else "Keep practicing!"
        })
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return jsonify({'success': False, 'message': 'Prediction failed', 'error': str(e)}), 500


@app.route('/api/get-random-letter', methods=['GET'])
def get_random_letter():
    """Get a random Sinhala letter for practice"""
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        # Get random letter
        sinhala_classes = list(SINHALA_LETTERS.keys())
        letter_id = random.choice(sinhala_classes)
        letter_info = SINHALA_LETTERS[letter_id]
        
        # Create session
        session_id = f"{user_id}_{datetime.now().timestamp()}_{random.randint(1000, 9999)}"
        user_sessions[session_id] = {
            'user_id': user_id,
            'letter_id': letter_id,
            'letter_info': letter_info,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'letter': {
                'id': letter_id,
                'character': letter_info['name'],
                'romanized': letter_info['romanized']
            }
        })
        
    except Exception as e:
        print(f"Get random letter error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get random letter'}), 500


@app.route('/api/get-all-letters', methods=['GET'])
def get_all_letters():
    """Get all Sinhala letters"""
    try:
        letters = [
            {
                'id': letter_id,
                'character': info['name'],
                'romanized': info['romanized']
            }
            for letter_id, info in SINHALA_LETTERS.items()
        ]
        
        return jsonify({
            'success': True,
            'count': len(letters),
            'letters': letters
        })
        
    except Exception as e:
        print(f"Get all letters error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get letters'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Sinhala Handwriting Recognition API - 454 Classes")
    print("=" * 60)
    print(f"Total letters: {len(SINHALA_LETTERS)}")
    print(f"Model status: {'LOADED' if model.model_loaded else 'MOCK MODE'}")
    print(f"Available endpoints: {['/', '/api/auth/register', '/api/auth/login', '/api/predict', '/api/health', '/api/get-random-letter', '/api/get-all-letters']}")
    print("\nStarting server...")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)