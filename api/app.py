"""
Flask API for Sinhala Handwriting Recognition - 454 Classes
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

# Initialize model with 454 classes
model = SinhalaHandwritingModel(num_classes=454)

# Complete Sinhala Letters Dictionary (454 classes)
sinhala_classes = ["අ","ආ","ඇ","ඈ","ඉ","ඊ","උ","එ","ඒ","ඔ","ඕ",
             "ක","කා","කැ","කෑ","කි","කී","කු","කූ","ක්","කෝ","ක්‍ර","ක්‍රි","ක්‍රී",
             "ග","ගා","ගැ","ගෑ","ගි","ගී","ගු","ගූ","ග්","ගෝ","ග්‍ර","ග්‍රි","ග්‍රී",
             "ච","චා","චැ","චෑ","චි","චී","චු","චූ","ච්","චෝ","ච්‍ර","ච්‍ර්","ච්‍රී",
             "ජ","ජා","ජැ","ජෑ","ජි","ජී","ජු","ජූ","ජ්","ජෝ","ජ්‍ර","ජ්‍රි","ජ්‍රී",
             "ට","ටා","ටැ","ටෑ","ටි","ටී","ටු","ටූ","ට්","ටෝ","ට්‍ර","ට්‍ර්","ට්‍රි",
             "ඩ","ඩා","ඩැ","ඩෑ","ඩි","ඩී","ඩු","ඩූ","ඩ්","ඩෝ","ඩ්‍ර","ඩ්‍ර්","ඩ්‍රි",
             "ණ","ණා","ණි",
             "ත","තා","ති","තී","තු","තූ","ත්","තෝ","ත්‍ර","ත්‍රා","ත්‍රි","ත්‍රී",
             "ද ","දා","දැ","දෑ","දි","දී","දු","දූ","ද්","දෝ","ද්‍ර","ද්‍රෝ","ද්‍රා","ද්‍රි","ද්‍රී",
             "න","නා","නැ","නෑ","නි","නී","නු","නූ","න්","නෝ","න්‍ර","න්‍රා","න්‍රි","න්‍රී",
             "ප","පා","පැ","පෑ","පි","පී","පු","පූ","ප්","ප්‍රෝ","පෝ","ප්‍ර","ප්‍රා","ප්‍රි","ප්‍රී",
             "බ","බා","බැ","බෑ","බි","බී","බු","බූ","බ්","බ්‍රෝ","බ්‍ර","බ්‍රා","බ්‍රි","බ්‍රී","බ්‍රෝ",
             "ම","මා","මැ","මෑ","මි","මී","මු","මූ","ම්","මෝ","ම්‍ර","ම්‍රා","ම්‍රි","ම්‍රී","ම්‍රෝ",
             "ය","යා","යැ","යෑ","යි","යී","යු","යූ","ෝ","ය්","hda",
             "ර","රා","රැ","රැ","රු","රූ","රි","රී",
             "ල","ලා","ලැ","ලෑ","ලි","ලී","ලු","ලූ","ල්",",da",
             "ව","වා","වැ","වෑ","වි","වී","වු","වූ","ව්","jda","ව්‍ර","ව්‍රා","ව්‍රැ","ව්‍රෑ","j%da",
             "ශ","ශා","ශැ","ශෑ","ශි","ශී","ශු","ශූ","ශ්","Yda","ශ්‍ර","ශ්‍රා","ශ්‍රැ","ශ්‍රෑ","ශ්‍රි","ශ්‍රී","Y%da",
             "ෂ","ෂා","ෂැ","ෂෑ","ෂි","ෂී","ෂු","ෂූ","ෂ්","Ida",
             "ස","සා","සැ","සෑ","සි","සී","සු","සූ","ida","ස්‍ර","ස්‍රා","ස්‍රි","ස්‍රී","ස්",
             "හ","හා","හැ","හෑ","හි","හී","හු","හූ","හ්","yda",
             "ළ","ළා","ළැ","ළෑ","ළි","ළී",
             "ළූ","ළූ",
             "ෆ","ෆා","ෆැ","ෆෑ","ෆි","ෆී","ෆූ","ෆූ","ෆ්‍ර","ෆ්‍රි","ෆ්‍රී","ෆ්‍රැ","ෆ්‍රෑ","ෆ්","*da",
             "ක්‍රා","ක්‍රැ","ක්‍රෑ","l%da",".%da",
             "ඛ","ඛා","ඛි","ඛී","ඛ්",
             "ඝ","ඝා","ඝැ","ඝෑ","ඝි","ඝී","ඝු","ඝූ",">da","ඝ්","ඝ්‍ර","ඝ්‍රා","ඝ්‍රි","ඝ්‍රී",
             "ඳ","ඳා","ඳැ","ෑ","ඳෑ","ඳි","ඳී","ඳු","ඳූ","|da ","ඳ්",
             "ඟ","ඟා","ඟැ","ඟෑ","ඟි","ඟී","ඟු","ඟූ","Õda","ඟ්",
             "ඬ","ැ","ඬා","ඬැ","ඬෑ","ඬි","ඬී","ඬු","ඬූ","ඬda ","ඬ්",
             "ඹ","ඹා","ඹැ","ඹෑ","ඹි","ඹී","ඹු","ඹූ","Uda","ඹ්",
             "භ","භා","භැ","භෑ","භි","භී","භු","භූ","Nda","භ්",
             "ධ","ධා","ධැ","ධෑ","ධි","ධී","ධු","ධූ","ධෝ","ධ්",
             "ඨ","ඨා","ඨැ","ඨි","ඨී","ඨු","ඨූ","ඨ්","ඪ","ඪා","ඪි","Vda",
             "ඵ","ඵා","ඵු","ඵි","Mda","ඵ් ","ථ","ථා","ථැ","ථ්","ා","ෟ","ණැ","ණෑ","ෘ","ණී","ණු","ණූ",
             "Kda","ණ්","ඥ","ඥා","{da","ඤ","ඤා","ඤු","[da","ඤ්","ඣ","ඣා","ඣු","COda",
             "ඣ්","ඦ","ඦා","ඦැ","ඦෑ","ඦි","ඦු","ඦූ","ඦෝ",
             "ඦ්","ඡ","ඡා","ඡැ","ඡෑ","ඡි","ඡේ","තැ","තෑ","ත්‍රැ","ත්‍රෑ",";%da",
             "ළු","ෲ","HQ","ff","f","H","Hq"]

# Create dictionary from list
SINHALA_LETTERS = {i: {'name': char, 'romanized': f'class_{i}'} for i, char in enumerate(sinhala_classes)}

user_sessions = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'API is running',
        'model_status': 'loaded' if model.model_loaded else 'mock_mode',
        'timestamp': datetime.now().isoformat(),
        'total_classes': len(SINHALA_LETTERS)
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
        
        predicted_letter = SINHALA_LETTERS.get(result['predicted_class'], {'name': '?', 'romanized': 'unknown'})
        
        return jsonify({
            'success': True,
            'score': round(result['score'], 2),
            'is_correct': result['is_correct'],
            'confidence': round(result['confidence'], 4),
            'feedback': feedback,
            'predicted_letter': predicted_letter['name'],
            'correct_letter': SINHALA_LETTERS[correct_letter_id]['name'],
            'model_mode': result.get('model_mode', 'unknown')
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
        'name': 'Sinhala Handwriting API - 454 Classes',
        'status': 'running',
        'total_classes': len(SINHALA_LETTERS),
        'model_loaded': model.model_loaded,
        'endpoints': ['/api/health', '/api/get-letter', '/api/submit-handwriting', '/api/get-all-letters']
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Sinhala Handwriting Recognition API - 454 Classes")
    print("=" * 60)
    print(f"\nTotal classes: {len(SINHALA_LETTERS)}")
    print(f"Model status: {'LOADED' if model.model_loaded else 'MOCK MODE'}")
    print("\nStarting server...")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)