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
    print("[OK] Primary Handwriting Model (454 classes) Initialized")
except Exception as e:
    print(f"[ERROR] Failed to load Primary Handwriting Model: {e}")
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
# SENTENCES MODULE (Voice Feedback Practice - MongoDB Atlas)
# ============================================================
# MongoDB Atlas DB: 'customerfeedback', Collection: 'metadata'
# Fields: filename (str), text (str - Sinhala sentence)
_SENTENCES_DATA = []

def _load_sentences_from_mongo():
    """Load sentences from MongoDB Atlas (same connection as standalone voice backend)"""
    try:
        from pymongo import MongoClient as _MC
        _uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        _client = _MC(_uri, serverSelectionTimeoutMS=5000)
        _db_cf = _client['customerfeedback']
        metadata_col = _db_cf['metadata']
        timings_col = _db_cf['word_timings']

        metadata_docs = list(metadata_col.find())
        if not metadata_docs:
            print("⚠️  No sentences found in MongoDB metadata collection")
            return []

        # Load timings if available
        timings_doc = timings_col.find_one() or {}

        sentences = []
        for doc in metadata_docs:
            filename = doc.get('filename', '')
            text = doc.get('text', '')
            if not filename or not text:
                continue
            word_count = len(text.split())
            difficulty = 'easy' if word_count <= 6 else ('medium' if word_count <= 8 else 'hard')
            sentences.append({
                'id': filename,
                'text': text,
                'words': text.split(),
                'difficulty': difficulty,
                'hasAudio': True,
                'audioPath': f"/api/audio/{filename}.wav",
                'timings': timings_doc.get(filename, [])
            })

        print(f"[OK] Loaded {len(sentences)} sentences from MongoDB Atlas (customerfeedback/metadata)")
        return sentences

    except Exception as e:
        print(f"⚠️  MongoDB sentences unavailable: {e}")
        return []

# Load sentences at startup
_SENTENCES_DATA = _load_sentences_from_mongo()

# Offline fallback (used when MongoDB is unavailable)
_OFFLINE_SENTENCES = [
    {"id": "off_001", "text": "ආයුබෝවන් සුභ දවසක්", "words": ["ආයුබෝවන්", "සුභ", "දවසක්"], "difficulty": "easy"},
    {"id": "off_002", "text": "ඔබ කොහෙද යන්නේ", "words": ["ඔබ", "කොහෙද", "යන්නේ"], "difficulty": "easy"},
    {"id": "off_003", "text": "මගේ නම සිතාරා", "words": ["මගේ", "නම", "සිතාරා"], "difficulty": "easy"},
    {"id": "off_004", "text": "ඔබට ස්තූතියි", "words": ["ඔබට", "ස්තූතියි"], "difficulty": "easy"},
    {"id": "off_005", "text": "සිංහල ඉගෙනීම ප්‍රසාදජනකයි", "words": ["සිංහල", "ඉගෙනීම", "ප්‍රසාදජනකයි"], "difficulty": "medium"},
    {"id": "off_006", "text": "ගෙදර යමු", "words": ["ගෙදර", "යමු"], "difficulty": "easy"},
    {"id": "off_007", "text": "ඔයා කොහොමද", "words": ["ඔයා", "කොහොමද"], "difficulty": "easy"},
    {"id": "off_008", "text": "අම්මා හොඳ කෑම හදනවා", "words": ["අම්මා", "හොඳ", "කෑම", "හදනවා"], "difficulty": "easy"},
    {"id": "off_009", "text": "ලංකාව ලස්සන රටක්", "words": ["ලංකාව", "ලස්සන", "රටක්"], "difficulty": "easy"},
    {"id": "off_010", "text": "හිරු එළිය ලස්සනයි", "words": ["හිරු", "එළිය", "ලස්සනයි"], "difficulty": "easy"},
    {"id": "off_011", "text": "කලාව ජීවිතය සුන්දර කරයි", "words": ["කලාව", "ජීවිතය", "සුන්දර", "කරයි"], "difficulty": "medium"},
    {"id": "off_012", "text": "මම ළමයෙක්", "words": ["මම", "ළමයෙක්"], "difficulty": "easy"},
    {"id": "off_013", "text": "මට පොත් ආසයි", "words": ["මට", "පොත්", "ආසයි"], "difficulty": "easy"},
    {"id": "off_014", "text": "කුරුල්ලෝ ගී කියනවා", "words": ["කුරුල්ලෝ", "ගී", "කියනවා"], "difficulty": "easy"},
    {"id": "off_015", "text": "පාසල ළඟ ගස් තිබෙනවා", "words": ["පාසල", "ළඟ", "ගස්", "තිබෙනවා"], "difficulty": "medium"},
]

def _get_active_sentences():
    """Return MongoDB sentences if available, else offline fallback"""
    return _SENTENCES_DATA if _SENTENCES_DATA else _OFFLINE_SENTENCES

@app.route('/api/sentences/random', methods=['GET'])
@app.route('/api/sentences/random/<difficulty>', methods=['GET'])
def get_random_sentences(difficulty=None):
    """Return random practice sentences, optionally filtered by difficulty"""
    count = int(request.args.get('count', 10))
    try:
        data = _get_active_sentences()
        source = 'mongodb' if _SENTENCES_DATA else 'offline'
        if difficulty and difficulty.lower() not in ('all', 'offline'):
            data = [s for s in data if s.get('difficulty') == difficulty.lower()]
        if not data:
            data = _OFFLINE_SENTENCES
            source = 'offline'
        selected = random.sample(data, min(count, len(data)))
        return jsonify({'sentences': selected, 'count': len(selected), 'source': source})
    except Exception as e:
        return jsonify({'sentences': _OFFLINE_SENTENCES[:count], 'count': min(count, len(_OFFLINE_SENTENCES)), 'source': 'offline', 'error': str(e)})

@app.route('/api/sentences', methods=['GET'])
def get_all_sentences():
    """Return all sentences"""
    try:
        data = _get_active_sentences()
        source = 'mongodb' if _SENTENCES_DATA else 'offline'
        return jsonify({'sentences': data, 'total': len(data), 'source': source})
    except Exception as e:
        return jsonify({'sentences': _OFFLINE_SENTENCES, 'total': len(_OFFLINE_SENTENCES), 'source': 'offline', 'error': str(e)})

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
        
        # Determine expected letter from session if possible
        expected_letter = None
        session_id = data.get('session_id')
        if session_id and session_id in user_sessions:
            session_data = user_sessions[session_id]
            expected_letter = session_data.get('letter', {}).get('character', None)
        
        if model and model.model_loaded:
            prediction = model.predict(image)
            confidence_val = float(prediction.get('confidence', 0.0))
            score_val = round(confidence_val * 100, 2)
            predicted_letter = prediction['top_3'][0]['letter'] if prediction.get('top_3') else 'Unknown'
            
            # Simple check, if the system gave us the true expected letter, enforce it slightly or just report
            is_correct = score_val > 50
            if expected_letter and predicted_letter != expected_letter and score_val < 80:
                 is_correct = False
                 score_val = max(0, score_val - 30)

            return jsonify({
                'success': True,
                'score': score_val,
                'confidence': confidence_val,
                'is_correct': is_correct,
                'feedback': 'Very good! Keep practicing!' if score_val >= 90 else 'Good effort! Keep trying!' if score_val >= 75 else 'Keep practicing, you can do it!',
                'predicted_letter': predicted_letter
            })
        else:
            # Mock for development when model is not loaded
            # Use random score between 60.0 and 95.0
            mock_score = random.uniform(60.0, 95.0)
            mock_confidence = mock_score / 100.0
            is_correct = mock_score >= 70.0
            
            return jsonify({
                'success': True,
                'score': round(mock_score, 1),
                'confidence': mock_confidence,
                'is_correct': is_correct,
                'feedback': 'Mock Correct!' if is_correct else 'Mock Incorrect!',
                'predicted_letter': expected_letter if expected_letter else 'Mock',
                'mock': True
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/get-random-letter', methods=['GET'])
def get_random_letter():
    user_id = request.args.get('user_id', 'anonymous')

    # Use the model's class names if available, otherwise fall back to a subset
    if model and model.model_loaded and model.class_names:
        letter_id = random.randint(0, len(model.class_names) - 1)
        character = model.class_names[letter_id]
        romanized = character  # Use character itself if no romanized mapping
    else:
        # Fallback: pick from a list of common Sinhala vowels & consonants
        SINHALA_LETTERS_LIST = [
            {'id': 0, 'character': 'අ', 'romanized': 'a'},
            {'id': 1, 'character': 'ආ', 'romanized': 'aa'},
            {'id': 2, 'character': 'ඇ', 'romanized': 'ae'},
            {'id': 3, 'character': 'ඈ', 'romanized': 'aae'},
            {'id': 4, 'character': 'ඉ', 'romanized': 'i'},
            {'id': 5, 'character': 'ඊ', 'romanized': 'ii'},
            {'id': 6, 'character': 'උ', 'romanized': 'u'},
            {'id': 7, 'character': 'ඌ', 'romanized': 'uu'},
            {'id': 8, 'character': 'එ', 'romanized': 'e'},
            {'id': 9, 'character': 'ඒ', 'romanized': 'ee'},
            {'id': 10, 'character': 'ඔ', 'romanized': 'o'},
            {'id': 11, 'character': 'ඕ', 'romanized': 'oo'},
            {'id': 12, 'character': 'ක', 'romanized': 'ka'},
            {'id': 13, 'character': 'ග', 'romanized': 'ga'},
            {'id': 14, 'character': 'ච', 'romanized': 'cha'},
            {'id': 15, 'character': 'ජ', 'romanized': 'ja'},
            {'id': 16, 'character': 'ට', 'romanized': 'ta'},
            {'id': 17, 'character': 'ඩ', 'romanized': 'da'},
            {'id': 18, 'character': 'ත', 'romanized': 'tha'},
            {'id': 19, 'character': 'ද', 'romanized': 'dha'},
            {'id': 20, 'character': 'න', 'romanized': 'na'},
            {'id': 21, 'character': 'ප', 'romanized': 'pa'},
            {'id': 22, 'character': 'බ', 'romanized': 'ba'},
            {'id': 23, 'character': 'ම', 'romanized': 'ma'},
            {'id': 24, 'character': 'ය', 'romanized': 'ya'},
            {'id': 25, 'character': 'ර', 'romanized': 'ra'},
            {'id': 26, 'character': 'ල', 'romanized': 'la'},
            {'id': 27, 'character': 'ව', 'romanized': 'va'},
            {'id': 28, 'character': 'ස', 'romanized': 'sa'},
            {'id': 29, 'character': 'හ', 'romanized': 'ha'},
        ]
        chosen = random.choice(SINHALA_LETTERS_LIST)
        return jsonify({'success': True, 'letter': chosen})

    return jsonify({
        'success': True,
        'letter': {'id': letter_id, 'character': character, 'romanized': romanized}
    })

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print(f"Unified Sinhala Learning API running on http://0.0.0.0:{PORT}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=PORT, debug=True)
