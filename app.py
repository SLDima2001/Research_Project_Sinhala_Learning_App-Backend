<<<<<<< HEAD
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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        
        # Get session info to verify correctness
        session_id = data.get('session_id')
        expected_letter = None
        is_correct = False
        
        if session_id and session_id in user_sessions:
            session = user_sessions[session_id]
            expected_id = session['letter_id']
            expected_letter = SINHALA_LETTERS.get(expected_id, {}).get('name', '?')
            
            # Verify if prediction matches expected
            is_correct = (predicted_class == expected_id)
        
        # Calculate final score and feedback
        score = confidence * 100
        feedback = ""
        
        if expected_letter:
            if is_correct:
                feedback = f"Correct! You wrote {letter_info['name']} properly."
            else:
                score = max(0, score - 50) # Penalize wrong answer
                feedback = f"Incorrect. expected {expected_letter}, but looks like {letter_info['name']}."
        else:
            feedback = f"Recognized as {letter_info['name']}"

        return jsonify({
            'success': True,
            'prediction': {
                'class': predicted_class,
                'character': letter_info['name'],
                'romanized': letter_info['romanized'],
                'confidence': confidence
            },
            'score': score,
            'is_correct': is_correct,
            'expected_letter': expected_letter,
            'feedback': feedback
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
=======
import os
import io
import json
import base64
import hashlib
import urllib.parse
from typing import Tuple, Dict, Optional
import requests

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf

# Configuration
MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join("model", "sinhala_handwriting_model (1).h5"))
LABELS_PATH = os.environ.get("LABELS_PATH", "label_map.json")
PORT = int(os.environ.get("PORT", 5005))
HOST = os.environ.get("HOST", "0.0.0.0")
IMG_SIZE: Tuple[int, int] = (224, 224)

# Image cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "image_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Optional: Pixabay API Key (get free at https://pixabay.com/api/docs/)
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.before_request
def log_request_info():
    print(f">> Incoming: {request.method} {request.url}")

model = None
idx_to_label = None

# ============================================================
# Sinhala word -> English translation mapping
# ============================================================
WORD_TO_ENGLISH: Dict[str, str] = {
    'බල්ලා': 'dog',
    'බළලා': 'cat',
    'ගස': 'tree',
    'මල': 'flower',
    'අහස': 'blue sky clouds',
    'හිරු': 'sun sunshine',
    'චන්දය': 'moon night',
    'තරු': 'stars night sky',
    'ගෙදර': 'house home',
    'බස්': 'bus',
    'කාර්': 'car automobile',
    'පාසල': 'school building',
    'පුටුව': 'chair furniture',
    'මේසය': 'table desk',
    'පොත': 'book',
    'පන්සල': 'buddhist temple',
    'මිනිසා': 'man person',
    'ළමයා': 'child kid',
    'එළුවා': 'goat',
    'බුකුටා': 'rooster chicken',
}


# ============================================================
# Model loading
# ============================================================
def load_artifacts():
    """Load the trained model and label mappings"""
    global model, idx_to_label

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    if not os.path.exists(LABELS_PATH):
        raise FileNotFoundError(f"Label map not found at {LABELS_PATH}")

    try:
        print("Constructing MobileNetV2 architecture manually...")
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=IMG_SIZE + (3,),
            include_top=False,
            weights=None
        )

        x = base_model.output
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        num_classes = 75
        predictions = tf.keras.layers.Dense(num_classes, activation='softmax')(x)

        model = tf.keras.models.Model(inputs=base_model.input, outputs=predictions)
        model.load_weights(MODEL_PATH, by_name=True, skip_mismatch=True)
        print(f"✓ Model weights loaded from {MODEL_PATH}")

    except Exception as e:
        print(f"Manual reconstruction failed: {e}")
        raise e

    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
        idx_to_label = {int(k): v for k, v in raw.items()}
    print(f"✓ Loaded {len(idx_to_label)} labels")


load_error = None
try:
    load_artifacts()
except Exception as e:
    load_error = str(e)
    print(f"✗ Failed to load artifacts: {e}")


def preprocess_image(file_bytes: bytes) -> np.ndarray:
    """Preprocess image for OCR model"""
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE)
    arr = np.asarray(img).astype("float32") / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr


def optimize_image(image_bytes: bytes, max_size: int = 400, quality: int = 80) -> bytes:
    """Resize and compress an image to reduce transfer size for mobile"""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # Resize to max dimension while keeping aspect ratio
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        result = buf.getvalue()
        print(f"  Optimized image: {len(image_bytes)} -> {len(result)} bytes")
        return result
    except Exception as e:
        print(f"  Image optimization failed: {e}")
        return image_bytes


# ============================================================
# IMAGE SEARCH FUNCTIONS - Real images from the web
# ============================================================

def get_cache_path(search_term: str) -> str:
    """Get a consistent cache file path for a search term"""
    safe_name = hashlib.md5(search_term.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{safe_name}.jpg")


def get_cached_image(search_term: str) -> Optional[bytes]:
    """Check if we have a cached image for this search term"""
    cache_path = get_cache_path(search_term)
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            data = f.read()
            if len(data) > 1000:  # Ensure it's a real image, not empty
                print(f"  ✓ Using cached image for '{search_term}'")
                return data
    return None


def save_to_cache(search_term: str, image_bytes: bytes):
    """Save an image to the cache"""
    cache_path = get_cache_path(search_term)
    with open(cache_path, "wb") as f:
        f.write(image_bytes)
    print(f"  ✓ Cached image for '{search_term}'")


def search_wikimedia(search_term: str) -> Optional[bytes]:
    """Search for a real image on Wikimedia Commons (FREE, no API key needed)"""
    try:
        print(f"  Searching Wikimedia Commons for: '{search_term}'...")
        search_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "generator": "search",
            "gsrnamespace": "6",       # File namespace
            "gsrsearch": f"{search_term} filetype:bitmap",
            "gsrlimit": "5",
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "iiurlwidth": "512",       # Request 512px thumbnail
            "format": "json",
        }
        resp = requests.get(search_url, params=params, timeout=10,
                            headers={"User-Agent": "SinhalaLearningApp/1.0"})
        data = resp.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in sorted(pages.items(), key=lambda x: x[1].get("index", 999)):
            imageinfo = page_data.get("imageinfo", [{}])[0]
            thumb_url = imageinfo.get("thumburl", "")
            mime = imageinfo.get("mime", "")

            # Only use actual images (not SVG, PDF, etc.)
            if thumb_url and mime in ("image/jpeg", "image/png", "image/webp"):
                print(f"  Found Wikimedia image: {thumb_url[:80]}...")
                img_resp = requests.get(thumb_url, timeout=10,
                                        headers={"User-Agent": "SinhalaLearningApp/1.0"})
                if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                    return img_resp.content

        print(f"  No suitable Wikimedia image found for '{search_term}'")
    except Exception as e:
        print(f"  Wikimedia search failed: {e}")
    return None


def search_pixabay(search_term: str) -> Optional[bytes]:
    """Search for a real image on Pixabay (FREE with API key)"""
    if not PIXABAY_API_KEY:
        return None

    try:
        print(f"  Searching Pixabay for: '{search_term}'...")
        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": search_term,
            "image_type": "photo",
            "safesearch": "true",
            "per_page": "3",
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        hits = data.get("hits", [])
        if hits:
            # Use webformatURL (640px) - good quality, fast download
            img_url = hits[0].get("webformatURL", "")
            if img_url:
                print(f"  Found Pixabay image: {img_url[:80]}...")
                img_resp = requests.get(img_url, timeout=10)
                if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                    return img_resp.content

        print(f"  No Pixabay image found for '{search_term}'")
    except Exception as e:
        print(f"  Pixabay search failed: {e}")
    return None


def search_wikipedia_image(search_term: str) -> Optional[bytes]:
    """Search for an image via Wikipedia article (FREE, no API key)"""
    try:
        print(f"  Searching Wikipedia for: '{search_term}'...")
        # First, find the Wikipedia page
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": search_term.split()[0],  # Use first word
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pithumbsize": "512",
            "format": "json",
        }
        resp = requests.get(search_url, params=params, timeout=10,
                            headers={"User-Agent": "SinhalaLearningApp/1.0"})
        data = resp.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                continue
            thumbnail = page_data.get("thumbnail", {})
            img_url = thumbnail.get("source", "")
            if img_url:
                print(f"  Found Wikipedia image: {img_url[:80]}...")
                img_resp = requests.get(img_url, timeout=10,
                                        headers={"User-Agent": "SinhalaLearningApp/1.0"})
                if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                    return img_resp.content

        print(f"  No Wikipedia image found for '{search_term}'")
    except Exception as e:
        print(f"  Wikipedia search failed: {e}")
    return None


def generate_simple_placeholder(text: str) -> bytes:
    """Generate a simple placeholder image with the detected text (last resort)"""
    from PIL import ImageDraw, ImageFont

    img = Image.new('RGB', (512, 512), color=(147, 51, 234))
    draw = ImageDraw.Draw(img)

    font_paths = [
        "C:\\Windows\\Fonts\\iskpota.ttf",
        "C:\\Windows\\Fonts\\Nirmala.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansSinhala-Regular.ttf",
    ]

    font = None
    for path in font_paths:
        try:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 60)
                break
        except:
            continue
    if font is None:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (512 - text_width) // 2
    y = (512 - text_height) // 2
    draw.text((x, y), text, fill=(255, 255, 255), font=font)

    # Add subtitle
    try:
        small_font = ImageFont.truetype(font_paths[2] if os.path.exists(font_paths[2]) else "", 20)
    except:
        small_font = ImageFont.load_default()
    draw.text((140, 450), "Image not available", fill=(200, 200, 200), font=small_font)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def find_real_image(sinhala_text: str) -> Tuple[bytes, str]:
    """
    Main function to find a REAL image for a Sinhala word.
    Tries multiple free web sources in order.
    Returns (image_bytes, source_name).
    """
    # Step 1: Get the English search term
    if sinhala_text in WORD_TO_ENGLISH:
        english_term = WORD_TO_ENGLISH[sinhala_text]
    else:
        # Try translating dynamically
        try:
            from deep_translator import GoogleTranslator
            print(f"  Translating '{sinhala_text}' to English...")
            english_term = GoogleTranslator(source='sinhala', target='english').translate(sinhala_text)
            print(f"  Translated: '{sinhala_text}' -> '{english_term}'")
        except Exception as e:
            print(f"  Translation failed: {e}")
            english_term = sinhala_text

    print(f"\n🔍 Searching real image for: '{sinhala_text}' (English: '{english_term}')")

    # Step 2: Check cache first
    cached = get_cached_image(english_term)
    if cached:
        return cached, "cache"

    # Step 3: Try Wikipedia (best quality, most relevant for single-word searches)
    image_bytes = search_wikipedia_image(english_term)
    if image_bytes:
        image_bytes = optimize_image(image_bytes)
        save_to_cache(english_term, image_bytes)
        return image_bytes, "Wikipedia"

    # Step 4: Try Wikimedia Commons (huge free image library)
    image_bytes = search_wikimedia(english_term)
    if image_bytes:
        image_bytes = optimize_image(image_bytes)
        save_to_cache(english_term, image_bytes)
        return image_bytes, "Wikimedia Commons"

    # Step 5: Try Pixabay (if API key is configured)
    image_bytes = search_pixabay(english_term)
    if image_bytes:
        image_bytes = optimize_image(image_bytes)
        save_to_cache(english_term, image_bytes)
        return image_bytes, "Pixabay"

    # Step 6: Try with simpler search term (first word only)
    simple_term = english_term.split()[0] if " " in english_term else None
    if simple_term:
        print(f"  Retrying with simpler term: '{simple_term}'...")
        image_bytes = search_wikipedia_image(simple_term)
        if image_bytes:
            image_bytes = optimize_image(image_bytes)
            save_to_cache(english_term, image_bytes)
            return image_bytes, "Wikipedia (simple)"

        image_bytes = search_wikimedia(simple_term)
        if image_bytes:
            image_bytes = optimize_image(image_bytes)
            save_to_cache(english_term, image_bytes)
            return image_bytes, "Wikimedia (simple)"

    # Step 7: Last resort - placeholder
    print(f"  ⚠ No real image found, using placeholder")
    return generate_simple_placeholder(sinhala_text), "placeholder"


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/health")
def health():
    """Health check endpoint"""
    if load_error is not None:
        return jsonify({"status": "error", "detail": load_error}), 500
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "num_classes": len(idx_to_label) if idx_to_label else 0
    })


@app.post("/predict")
def predict():
    """OCR endpoint - recognize Sinhala handwriting"""
    if load_error is not None:
        return jsonify({"error": "model_not_loaded", "detail": load_error}), 500

    if "file" not in request.files:
        return jsonify({"error": "missing_file", "detail": "Expected multipart form field 'file'"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "empty_filename"}), 400

    try:
        content = file.read()
        batch = preprocess_image(content)
        preds = model.predict(batch)

        probs = preds[0]
        top_idx = int(np.argmax(probs))
        top_label = idx_to_label.get(top_idx, str(top_idx))
        top_conf = float(np.max(probs))

        top_3_indices = np.argsort(probs)[-3:][::-1]
        top_3_predictions = [
            {
                "label": idx_to_label.get(int(idx), str(idx)),
                "confidence": float(probs[idx])
            }
            for idx in top_3_indices
        ]

        return jsonify({
            "success": True,
            "label": top_label,
            "confidence": top_conf,
            "top_index": top_idx,
            "top_3_predictions": top_3_predictions,
            "num_classes": len(idx_to_label),
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "inference_failed", "detail": str(e)}), 500


@app.post("/generate-image")
def generate_image_endpoint():
    """Generate/find a real image from a Sinhala text prompt"""
    print("\n===== /generate-image =====")
    try:
        data = request.get_json()
        sinhala_text = data.get('prompt', '')

        if not sinhala_text:
            return jsonify({"error": "missing_prompt"}), 400

        # Find a real image from the web
        image_bytes, source = find_real_image(sinhala_text)

        # Get English term for response
        english_term = WORD_TO_ENGLISH.get(sinhala_text, sinhala_text)

        # Convert to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        print(f"✓ Returning image from: {source} ({len(image_bytes)} bytes)")

        return jsonify({
            "success": True,
            "image": image_b64,
            "detected_text": sinhala_text,
            "prompt_used": english_term,
            "image_source": source,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "generation_failed",
            "detail": str(e)
        }), 500


@app.post("/ocr-and-generate")
def ocr_and_generate():
    """Combined endpoint: OCR + Real Image Search"""
    if load_error is not None:
        return jsonify({"error": "model_not_loaded", "detail": load_error}), 500

    if "file" not in request.files:
        return jsonify({"error": "missing_file"}), 400

    try:
        # Step 1: OCR
        file = request.files["file"]
        content = file.read()
        batch = preprocess_image(content)
        preds = model.predict(batch)

        top_idx = int(np.argmax(preds[0]))

        if top_idx not in idx_to_label:
            print(f"Error: Model predicted class {top_idx} which is not in label_map.json")
            return jsonify({
                "success": False,
                "error": "unknown_class",
                "class_id": top_idx,
                "detail": f"Model predicted Class {top_idx}, but this class is missing from label_map.json.",
                "num_classes_in_map": len(idx_to_label)
            }), 200

        detected_text = idx_to_label[top_idx]
        confidence = float(np.max(preds[0]))

        print(f"\nDetected: {detected_text} (confidence: {confidence:.2f})")

        # Step 2: Find a real image from the web
        image_bytes, source = find_real_image(detected_text)

        english_term = WORD_TO_ENGLISH.get(detected_text, detected_text)
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        return jsonify({
            "success": True,
            "detected_text": detected_text,
            "confidence": confidence,
            "image": image_b64,
            "prompt_used": english_term,
            "image_source": source,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "processing_failed",
            "detail": str(e)
        }), 500


@app.get("/clear-cache")
def clear_cache():
    """Clear the image cache"""
    import shutil
    try:
        shutil.rmtree(CACHE_DIR)
        os.makedirs(CACHE_DIR, exist_ok=True)
        return jsonify({"success": True, "message": "Cache cleared"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print(f"\n🚀 Starting server on {HOST}:{PORT}")
    print(f"📱 Mobile app should use: http://192.168.1.233:{PORT}")
    print(f"📂 Image cache directory: {CACHE_DIR}")
    print(f"🔑 Pixabay API key: {'configured' if PIXABAY_API_KEY else 'not set (optional)'}")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
>>>>>>> origin/text-to-image
