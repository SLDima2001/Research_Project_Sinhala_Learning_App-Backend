"""
Flask API for Sinhala Handwriting Recognition
File: app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
import random
from datetime import datetime

from sinhala_model import SinhalaHandwritingModel

app = Flask(__name__)
CORS(app)

# Initialize model
model = SinhalaHandwritingModel(num_classes=59)

# Sinhala Letters Dictionary
SINHALA_LETTERS = {
    0: {'name': 'අ', 'romanized': 'a'},
    1: {'name': 'ආ', 'romanized': 'aa'},
    2: {'name': 'ඇ', 'romanized': 'ae'},
    3: {'name': 'ඈ', 'romanized': 'aae'},
    4: {'name': 'ඉ', 'romanized': 'i'},
    5: {'name': 'ඊ', 'romanized': 'ii'},
    6: {'name': 'උ', 'romanized': 'u'},
    7: {'name': 'ඌ', 'romanized': 'uu'},
    8: {'name': 'ඍ', 'romanized': 'r'},
    9: {'name': 'ඎ', 'romanized': 'rr'},
    10: {'name': 'ඏ', 'romanized': 'l'},
    11: {'name': 'ඐ', 'romanized': 'll'},
    12: {'name': 'එ', 'romanized': 'e'},
    13: {'name': 'ඒ', 'romanized': 'ee'},
    14: {'name': 'ඓ', 'romanized': 'ai'},
    15: {'name': 'ඔ', 'romanized': 'o'},
    16: {'name': 'ඕ', 'romanized': 'oo'},
    17: {'name': 'ඖ', 'romanized': 'au'},
    18: {'name': 'ක', 'romanized': 'ka'},
    19: {'name': 'ඛ', 'romanized': 'kha'},
    20: {'name': 'ග', 'romanized': 'ga'},
    21: {'name': 'ඝ', 'romanized': 'gha'},
    22: {'name': 'ඞ', 'romanized': 'nga'},
    23: {'name': 'ඟ', 'romanized': 'nnga'},
    24: {'name': 'ච', 'romanized': 'ca'},
    25: {'name': 'ඡ', 'romanized': 'cha'},
    26: {'name': 'ජ', 'romanized': 'ja'},
    27: {'name': 'ඣ', 'romanized': 'jha'},
    28: {'name': 'ඤ', 'romanized': 'nya'},
    29: {'name': 'ඥ', 'romanized': 'jnya'},
    30: {'name': 'ඤ', 'romanized': 'nyja'},
    31: {'name': 'ට', 'romanized': 'tta'},
    32: {'name': 'ඨ', 'romanized': 'ttha'},
    33: {'name': 'ඩ', 'romanized': 'dda'},
    34: {'name': 'ඪ', 'romanized': 'ddha'},
    35: {'name': 'ණ', 'romanized': 'nna'},
    36: {'name': 'ඬ', 'romanized': 'nndda'},
    37: {'name': 'ත', 'romanized': 'ta'},
    38: {'name': 'ථ', 'romanized': 'tha'},
    39: {'name': 'ද', 'romanized': 'da'},
    40: {'name': 'ධ', 'romanized': 'dha'},
    41: {'name': 'න', 'romanized': 'na'},
    42: {'name': 'ඳ', 'romanized': 'nda'},
    43: {'name': 'ප', 'romanized': 'pa'},
    44: {'name': 'ඵ', 'romanized': 'pha'},
    45: {'name': 'බ', 'romanized': 'ba'},
    46: {'name': 'භ', 'romanized': 'bha'},
    47: {'name': 'ම', 'romanized': 'ma'},
    48: {'name': 'ඹ', 'romanized': 'mba'},
    49: {'name': 'ය', 'romanized': 'ya'},
    50: {'name': 'ර', 'romanized': 'ra'},
    51: {'name': 'ල', 'romanized': 'la'},
    52: {'name': 'ව', 'romanized': 'va'},
    53: {'name': 'ශ', 'romanized': 'sha'},
    54: {'name': 'ෂ', 'romanized': 'ssa'},
    55: {'name': 'ස', 'romanized': 'sa'},
    56: {'name': 'හ', 'romanized': 'ha'},
    57: {'name': 'ළ', 'romanized': 'lla'},
    58: {'name': 'ෆ', 'romanized': 'fa'},
}

user_sessions = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/get-letter', methods=['GET'])
def get_random_letter():
    user_id = request.args.get('user_id', 'anonymous')
    letter_id = random.choice(list(SINHALA_LETTERS.keys()))
    letter_info = SINHALA_LETTERS[letter_id]
    
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

@app.route('/api/submit-handwriting', methods=['POST'])
def submit_handwriting():
    try:
        data = request.json
        session_id = data.get('session_id')
        image_base64 = data.get('image')
        
        if not session_id or session_id not in user_sessions:
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        
        if not image_base64:
            return jsonify({'success': False, 'error': 'No image'}), 400
        
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        session_info = user_sessions[session_id]
        correct_letter_id = session_info['letter_id']
        
        result = model.calculate_score(image, correct_letter_id)
        feedback = generate_feedback(result['score'], result['is_correct'])
        
        return jsonify({
            'success': True,
            'score': round(result['score'], 2),
            'is_correct': result['is_correct'],
            'confidence': round(result['confidence'], 4),
            'feedback': feedback,
            'predicted_letter': SINHALA_LETTERS[correct_letter_id]['name']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-all-letters', methods=['GET'])
def get_all_letters():
    letters_list = [
        {'id': lid, 'character': info['name'], 'romanized': info['romanized']}
        for lid, info in sorted(SINHALA_LETTERS.items())
    ]
    return jsonify({'success': True, 'letters': letters_list, 'total': len(letters_list)})

def generate_feedback(score, is_correct):
    if not is_correct:
        return "වැරදි අකුරක්! නැවත උත්සාහ කරන්න. (Wrong letter! Try again.)"
    if score >= 95:
        return "විශිෂ්ටයි! පරිපූර්ණ ලිවීමකි! (Excellent! Perfect!)"
    elif score >= 90:
        return "ඉතා හොඳයි! (Very good!)"
    elif score >= 80:
        return "හොඳයි! (Good!)"
    elif score >= 70:
        return "හොඳ උත්සාහයක්! (Good try!)"
    else:
        return "තවත් පුහුණු වන්න. (Practice more.)"

@app.route('/')
def index():
    return jsonify({
        'name': 'Sinhala Handwriting API',
        'status': 'running',
        'endpoints': ['/api/health', '/api/get-letter', '/api/submit-handwriting']
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Sinhala Handwriting Recognition API")
    print("=" * 60)
    print(f"\nTotal letters: {len(SINHALA_LETTERS)}")
    print("\n⚠️  Running in MOCK MODE (for testing)")
    print("\nStarting server...")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)