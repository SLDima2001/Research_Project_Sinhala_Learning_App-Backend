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


MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join("model", "sinhala_handwriting_model (1).h5"))
LABELS_PATH = os.environ.get("LABELS_PATH", "label_map.json")
PORT = int(os.environ.get("PORT", 5005))
HOST = os.environ.get("HOST", "0.0.0.0")
IMG_SIZE: Tuple[int, int] = (224, 224)


CACHE_DIR = os.path.join(os.path.dirname(__file__), "image_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.before_request
def log_request_info():
    print(f">> Incoming: {request.method} {request.url}")

model = None
idx_to_label = None




WORD_TO_ENGLISH: Dict[str, str] = {
    'බල්ලා': 'dog',
    'බළලා': 'cat',
    'ගස': 'tree',
    'මල': 'flower',
    'අහස': 'sky',
    'හිරු': 'sun',
    'චන්දය': 'moon',
    'තරු': 'stars',
    'ගෙදර': 'house',
    'බස්': 'bus',
    'කාර්': 'car',
    'පාසල': 'school',
    'පුටුව': 'chair',
    'මේසය': 'table',
    'පොත': 'book',
    'පන්සල': 'temple',
    'මිනිසා': 'person',
    'ළමයා': 'child',
    'එළුවා': 'goat',
    'බුකුටා': 'rooster',
}





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
        print(f"[OK] Model weights loaded from {MODEL_PATH}")

    except Exception as e:
        print(f"Manual reconstruction failed: {e}")
        raise e

    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
        idx_to_label = {int(k): v for k, v in raw.items()}
    print(f"[OK] Loaded {len(idx_to_label)} labels")


load_error = None
try:
    load_artifacts()
except Exception as e:
    load_error = str(e)
    print(f"[ERROR] Failed to load artifacts: {e}")


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
        
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        result = buf.getvalue()
        print(f"  Optimized image: {len(image_bytes)} -> {len(result)} bytes")
        return result
    except Exception as e:
        print(f"  Image optimization failed: {e}")
        return image_bytes






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
            if len(data) > 1000:  
                print(f"  [OK] Using cached image for '{search_term}'")
                return data
    return None


def save_to_cache(search_term: str, image_bytes: bytes):
    """Save an image to the cache"""
    cache_path = get_cache_path(search_term)
    with open(cache_path, "wb") as f:
        f.write(image_bytes)
    print(f"  [OK] Cached image for '{search_term}'")


def search_wikimedia(search_term: str, randomize: bool = False) -> Optional[bytes]:
    """Search for a real image on Wikimedia Commons (FREE, no API key needed)"""
    try:
        print(f"  Searching Wikimedia Commons for: '{search_term}'...")
        search_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "generator": "search",
            "gsrnamespace": "6",       
            "gsrsearch": f"{search_term} filetype:bitmap",
            "gsrlimit": "20" if randomize else "5",
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "iiurlwidth": "512",       
            "format": "json",
        }
        resp = requests.get(search_url, params=params, timeout=10,
                            headers={"User-Agent": "SinhalaLearningApp/1.0"})
        data = resp.json()

        pages = data.get("query", {}).get("pages", {})
        page_items = list(pages.items())
        
        if randomize:
            import random
            random.shuffle(page_items)
        else:
            page_items = sorted(page_items, key=lambda x: x[1].get("index", 999))

        for page_id, page_data in page_items:
            imageinfo = page_data.get("imageinfo", [{}])[0]
            thumb_url = imageinfo.get("thumburl", "")
            mime = imageinfo.get("mime", "")

            
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


def search_wikipedia_image(search_term: str, randomize: bool = False) -> Optional[bytes]:
    """Search for an image via Wikipedia article (FREE, no API key)"""
    try:
        print(f"  Searching Wikipedia for: '{search_term}'...")
        
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": search_term.split()[0],  
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pithumbsize": "512",
            "format": "json",
        }
        resp = requests.get(search_url, params=params, timeout=10,
                            headers={"User-Agent": "SinhalaLearningApp/1.0"})
        data = resp.json()

        pages = data.get("query", {}).get("pages", {})
        page_items = list(pages.items())
        
        if randomize:
            import random
            random.shuffle(page_items)

        for page_id, page_data in page_items:
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

    
    try:
        small_font = ImageFont.truetype(font_paths[2] if os.path.exists(font_paths[2]) else "", 20)
    except:
        small_font = ImageFont.load_default()
    draw.text((140, 450), "Image not available", fill=(200, 200, 200), font=small_font)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def find_real_image(sinhala_text: str, randomize: bool = False) -> Tuple[bytes, str]:
    """
    Main function to find a REAL image for a Sinhala word.
    Tries multiple free web sources in order.
    Returns (image_bytes, source_name).
    """
    
    if sinhala_text in WORD_TO_ENGLISH:
        english_term = WORD_TO_ENGLISH[sinhala_text]
    else:
        
        try:
            from deep_translator import GoogleTranslator
            print(f"  Translating '{sinhala_text}' to English...")
            english_term = GoogleTranslator(source='sinhala', target='english').translate(sinhala_text)
            print(f"  Translated: '{sinhala_text}' -> '{english_term}'")
        except Exception as e:
            print(f"  Translation failed: {e}")
            english_term = sinhala_text

    print(f"\n🔍 Searching real image for: '{sinhala_text}' (English: '{english_term}', Randomize: {randomize})")

    
    if not randomize:
        cached = get_cached_image(english_term)
        if cached:
            return cached, "cache"

    
    image_bytes = search_wikipedia_image(english_term, randomize)
    if image_bytes:
        image_bytes = optimize_image(image_bytes)
        if not randomize: save_to_cache(english_term, image_bytes)
        return image_bytes, "Wikipedia"

    
    image_bytes = search_wikimedia(english_term, randomize)
    if image_bytes:
        image_bytes = optimize_image(image_bytes)
        if not randomize: save_to_cache(english_term, image_bytes)
        return image_bytes, "Wikimedia Commons"

    
    image_bytes = search_pixabay(english_term)
    if image_bytes:
        image_bytes = optimize_image(image_bytes)
        if not randomize: save_to_cache(english_term, image_bytes)
        return image_bytes, "Pixabay"

    
    simple_term = english_term.split()[0] if " " in english_term else None
    if simple_term:
        print(f"  Retrying with simpler term: '{simple_term}'...")
        image_bytes = search_wikipedia_image(simple_term, randomize)
        if image_bytes:
            image_bytes = optimize_image(image_bytes)
            if not randomize: save_to_cache(english_term, image_bytes)
            return image_bytes, "Wikipedia (simple)"

        image_bytes = search_wikimedia(simple_term, randomize)
        if image_bytes:
            image_bytes = optimize_image(image_bytes)
            if not randomize: save_to_cache(english_term, image_bytes)
            return image_bytes, "Wikimedia (simple)"

    
    print(f"  ⚠ No real image found, using placeholder")
    return generate_simple_placeholder(sinhala_text), "placeholder"






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
        randomize = data.get('randomize', False)

        if not sinhala_text:
            return jsonify({"error": "missing_prompt"}), 400

        
        image_bytes, source = find_real_image(sinhala_text, randomize)

        
        english_term = WORD_TO_ENGLISH.get(sinhala_text, sinhala_text)

        
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        print(f"[OK] Returning image from: {source} ({len(image_bytes)} bytes)")

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
