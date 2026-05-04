import os
import io
import json
import re
import base64
import hashlib
import requests
import random
from typing import Tuple, Dict, Optional, List
from flask import Blueprint, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tensorflow as tf

text_to_image_bp = Blueprint('text_to_image', __name__)

# Configuration
# This uses the same model as the rest of the application or the 75-class one as specified
MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join("model", "sinhala_handwriting_model (1).h5"))
LABELS_PATH = os.environ.get("LABELS_PATH", "label_map.json")
IMG_SIZE = (224, 224)

# Cache directory (root of the backend)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(PROJECT_ROOT, "image_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Optional: Pixabay API Key (get free at https://pixabay.com/api/docs/)
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")

# In-memory model state
_model = None
_idx_to_label = None

# ============================================================
# Sinhala word -> English translation mapping
# ============================================================
WORD_TO_ENGLISH: Dict[str, str] = {
    # Animals
    'බල්ලා': 'dog',
    'බළලා': 'cat',
    'අලියා': 'elephant',
    'කොටි': 'tiger',
    'සිංහයා': 'lion',
    'සමනලයා': 'butterfly',
    'කුරුල්ලා': 'bird',
    'මුවා': 'deer',
    'නරි': 'fox',
    'වඳුරා': 'monkey',
    'ගවයා': 'cow',
    'අශ්වයා': 'horse',
    'එළුවා': 'goat',
    'බුකුටා': 'rooster',
    'සීබ්‍රා': 'zebra',
    'කැන්ගරු': 'kangaroo',
    'මීයා': 'rat',
    # Nature
    'ගස': 'tree',
    'මල': 'flower',
    'මල්': 'flower',
    'අහස': 'sky',
    'හිරු': 'sun',
    'හඳ': 'moon',
    'චන්ද්‍රයා': 'moon',
    'තරු': 'stars',
    'චන්දය': 'election vote',
    'වැව': 'lake',
    'කන්ද': 'mountain',
    'ගෙවත්ත': 'garden',
    'වෙරළ': 'beach',
    'මුහුද': 'sea',
    'සොබාදහම': 'nature',
    'වතුර': 'water',
    'පොල්': 'coconut',
    # Objects
    'ගෙදර': 'house',
    'පුටුව': 'chair',
    'මේසය': 'table',
    'පොත': 'book',
    'කුඩය': 'umbrella',     # short u = umbrella
    'කූඩය': 'basket',       # long uu = basket
    'කූඩු': 'basket',
    'කූඩේ': 'basket',
    'කිරි': 'milk',
    'බත්': 'rice',
    # Transport
    'බස්': 'bus',
    'කාර්': 'car',
    'නැව': 'ship',
    'යානය': 'airplane',
    'දුම්රිය': 'train',
    'පාපැදිය': 'bicycle',
    'යතුරුපැදිය': 'motorbike',
    # Places
    'පාසල': 'school',
    'පන්සල': 'temple',
    'මහ රෝහල': 'hospital',
    'පොලිසිය': 'police station',
    # People
    'මිනිසා': 'person',
    'ළමයා': 'child',
    # Food / Fruit
    'ඇපල්': 'apple',
    'අඹ': 'mango',
    'දොඩම්': 'orange',
    'කෙසෙල්': 'banana',
    # Two-word phrases
    'මල් කූඩය': 'flower basket',   # long uu = basket
    'මල කූඩය': 'flower basket',
    'මල් කූඩේ': 'flower basket',
    'මල් කූඩු': 'flower basket',
    'මල් කුඩය': 'flower umbrella', # short u = umbrella
    'මල කුඩය': 'flower umbrella',
    'පොල් ගස': 'coconut tree',
    'තැඹිලි ගස': 'king coconut tree',
    'ගම් පාර': 'village road',
    'නිල් අහස': 'blue sky',
    'රතු මල': 'red flower',
    'රතු මල්': 'red flower',
    'ගල් කන්ද': 'rocky mountain',
    'දිය ඇල්ල': 'waterfall',
    'දිය ඇල': 'waterfall',
    'රන් මාළු': 'goldfish',
    'ගම් දනව්': 'village',
    'හිරු එළිය': 'sunlight',
    'හිරු රැස': 'sunbeam',
    'ළිදු වතුර': 'well water',
    'ළිඳ': 'water well',
    'ගිනි කඳ': 'volcano',
    'ගල් ගෙදර': 'stone house',
    'වැව් ජලය': 'lake water',
    'කඳු රට': 'hill country',
    'සුදු බල්ලා': 'white dog',
    'කළු බළලා': 'black cat',
    'කොළ ගස': 'green tree',
    'කොළ කෙසෙල්': 'green banana',
    'ලාල් ගෙදර': 'red house',
    'දිය කෙළිය': 'swimming pool',
    'මල් වත්ත': 'flower garden',
    'ගල් පාර': 'stone road',
    'අලි කූඩය': 'elephant basket',
    'කුකුළා ඇටය': 'chicken bone',
    'අල කූඩය': 'potato basket',
    'ළමා ක්‍රීඩා': 'children playing',
    'ගෙදර ළමා': 'children at home',
    'ගල් ලෙනක': 'cave',
    'කෝකිල ගී': 'cuckoo singing',
    'ගිනි ගෙදර': 'fire station',
    'නිල් මල': 'blue flower',
    'නිල් මල්': 'blue flower',
    'රතු ගෙදර': 'red house',
    'හේන් ගොවිතැන': 'farming',
    'කෙසෙල් ගස': 'banana tree',
    'ඇපල් ගස': 'apple tree',
    'අඹ ගස': 'mango tree',
}

# ============================================================
# Model loading
# ============================================================
def get_model():
    """Load the trained model and label mappings"""
    global _model, _idx_to_label

    if _model is not None and _idx_to_label is not None:
        return _model, _idx_to_label

    if not os.path.exists(MODEL_PATH):
        print(f"Model file not found at {MODEL_PATH}")
        return None, None
        
    if not os.path.exists(LABELS_PATH):
        print(f"Label map not found at {LABELS_PATH}")
        return None, None

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

        _model_local = tf.keras.models.Model(inputs=base_model.input, outputs=predictions)
        _model_local.load_weights(MODEL_PATH, by_name=True, skip_mismatch=True)
        print(f"[OK] Model weights loaded from {MODEL_PATH}")
        
        _model = _model_local
    except Exception as e:
        print(f"Manual reconstruction failed: {e}")
        return None, None

    try:
        with open(LABELS_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
            _idx_to_label = {int(k): v for k, v in raw.items()}
        print(f"[OK] Loaded {len(_idx_to_label)} labels")
    except Exception as e:
        print(f"Failed to load labels: {e}")
        return None, None

    return _model, _idx_to_label

# Trigger load initially on import to catch errors warmly 
get_model()

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
        return buf.getvalue()
    except Exception as e:
        print(f"  Image optimization failed: {e}")
        return image_bytes

# ============================================================
# IMAGE SEARCH FUNCTIONS - Real images from the web
# ============================================================

def get_cache_path(search_term: str) -> str:
    safe_name = hashlib.md5(search_term.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{safe_name}.jpg")

def get_cached_image(search_term: str) -> Optional[bytes]:
    cache_path = get_cache_path(search_term)
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            data = f.read()
            if len(data) > 1000:
                print(f"  [OK] Using cached image for '{search_term}'")
                return data
    return None

def is_accurate_enough(search_term: str, metadata: str, strict: bool = False) -> bool:
    """Check if the search term is significantly present in the metadata/filename"""
    if not metadata: 
        # For mini-games (strict mode), if we can't verify, reject it
        return not strict 
    
    term = search_term.lower()
    meta = metadata.lower()
    
    # Exclude common irrelevant terms that clutter results
    exclude_terms = ['person', 'people', 'man', 'woman', 'crowd', 'group', 'office', 'room', 'portrait', 'face']
    
    # If the search term itself isn't 'person' or 'child', exclude images mentioning people
    if not any(p in term for p in ['person', 'child', 'man', 'boy', 'girl', 'human', 'lady']):
        if any(ex in meta for ex in exclude_terms):
            print(f"  [DEBUG] Skipping result '{metadata}' - contains excluded term")
            return False

    # Check if the term or major parts of it are in the metadata
    words = [w for w in term.split() if len(w) > 2]
    if not words: return True
    
    # Require at least one word to be present
    return any(word in meta for word in words)


def save_to_cache(search_term: str, image_bytes: bytes):
    cache_path = get_cache_path(search_term)
    with open(cache_path, "wb") as f:
        f.write(image_bytes)
    print(f"  [OK] Cached image for '{search_term}'")


def search_wikimedia(search_term: str, randomize: bool = False) -> Optional[bytes]:
    """Search for a real image on Wikimedia Commons (FREE, no API key needed)"""
    try:
        print(f"  Searching Wikimedia Commons for: '{search_term}'...")
        search_url = "https://commons.wikimedia.org/w/api.php"
        
        # Exclude people and text-heavy images if searching for objects/animals
        negatives = "-icon -diagram -map -clipart -sketch -face -text -typography -alphabet -letter -font -words"
        if 'person' not in search_term.lower() and 'child' not in search_term.lower() and 'man' not in search_term.lower():
            negatives += " -person -people -man -woman -handler -owner -crowd"

        params = {
            "action": "query",
            "generator": "search",
            "gsrnamespace": "6",       # File namespace
            "gsrsearch": f'"{query}" {negatives} filetype:bitmap',
            "gsrlimit": "100" if randomize else "10",
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "iiurlwidth": "512",
            "format": "json",
        }
        resp = requests.get(search_url, params=params, timeout=10, headers={"User-Agent": "SinhalaLearningApp/1.0"})
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
            title = page_data.get("title", "")

            if thumb_url and mime in ("image/jpeg", "image/png", "image/webp"):
                if is_accurate_enough(search_term, title, strict=randomize):
                    img_resp = requests.get(thumb_url, timeout=10, headers={"User-Agent": "SinhalaLearningApp/1.0"})
                    if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                        return img_resp.content
    except Exception as e:
        print(f"  Wikimedia search failed: {e}")
    return None


def search_pixabay(search_term: str, randomize: bool = False) -> Optional[bytes]:
    """Search for a real image on Pixabay (FREE with API key)"""
    if not PIXABAY_API_KEY:
        return None

    try:
        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": search_term,
            "image_type": "photo",
            "safesearch": "true",
            "per_page": "80" if randomize else "3",
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        hits = data.get("hits", [])
        if hits:
            if randomize:
                import random
                random.shuffle(hits)
            img_url = hits[0].get("webformatURL", "")
            if img_url:
                img_resp = requests.get(img_url, timeout=10)
                if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                    return img_resp.content
    except Exception as e:
        print(f"  Pixabay search failed: {e}")
    return None

def search_duckduckgo_image(search_term: str, randomize: bool = False) -> Optional[bytes]:
    """Search for real images using DuckDuckGo (FREE, no API key)"""
    try:
        print(f"  Searching DuckDuckGo for: '{search_term}'...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "*/*",
        }
        
        # 1. Get VQD token
        res = requests.get("https://duckduckgo.com/", params={"q": search_term}, headers=headers, timeout=10)
        vqd_match = re.search(r'vqd=([0-9-]+)', res.text) or re.search(r'vqd=([^&"\']+)', res.text)
        if not vqd_match:
            return None
        vqd = vqd_match.group(1)

        # 2. Get results
        search_url = "https://duckduckgo.com/i.js"
        params = {
            "l": "wt-wt", "o": "json", "q": search_term,
            "vqd": vqd, "f": ",,,", "p": "1"
        }
        res = requests.get(search_url, params=params, headers=headers, timeout=10)
        data = res.json()
        results = data.get("results", [])

        if results:
            if randomize:
                random.shuffle(results)
            
            # Try top 10 results to find a valid image
            for i in range(min(10, len(results))):
                img_url = results[i].get("image", "")
                img_title = results[i].get("title", "")
                if img_url:
                    # Verify accuracy for randomized searches (games)
                    if not is_accurate_enough(search_term, img_title, strict=randomize):
                        continue
                        
                    try:
                        # Use a simpler image request
                        img_res = requests.get(img_url, headers={"User-Agent": headers["User-Agent"]}, timeout=8)
                        if img_res.status_code == 200 and len(img_res.content) > 10000:
                            return img_res.content
                    except:
                        continue
    except Exception as e:
        print(f"  DuckDuckGo search failed: {e}")
    return None


def search_wikipedia_image(search_term: str, randomize: bool = False) -> Optional[bytes]:
    """Search for an image via Wikipedia article (FREE, no API key)"""
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        
        if randomize:
            # Descriptive but strictly relevant search
            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": f'"{search_term}" photography',
                "gsrlimit": "40",
                "prop": "pageimages",
                "piprop": "thumbnail",
                "pithumbsize": "512",
                "format": "json",
            }
        else:
            # Direct title match for accuracy
            params = {
                "action": "query",
                "titles": search_term,
                "prop": "pageimages",
                "piprop": "thumbnail",
                "pithumbsize": "512",
                "format": "json",
            }
            
        resp = requests.get(search_url, params=params, timeout=10, headers={"User-Agent": "SinhalaLearningApp/1.0"})
        data = resp.json()

        pages = data.get("query", {}).get("pages", {})
        page_items = list(pages.items())
        
        if randomize:
            import random
            random.shuffle(page_items)

        for _, page_data in page_items:
            thumbnail = page_data.get("thumbnail", {})
            img_url = thumbnail.get("source", "")
            img_title = page_data.get("title", "")
            
            if img_url:
                if is_accurate_enough(search_term, img_title, strict=randomize):
                    img_resp = requests.get(img_url, timeout=10, headers={"User-Agent": "SinhalaLearningApp/1.0"})
                    if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                        return img_resp.content
    except Exception as e:
        print(f"  Wikipedia search failed: {e}")
    return None

def generate_simple_placeholder(text: str) -> bytes:
    """Generate a simple placeholder image with the detected text (last resort)"""
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


def translate_sinhala_to_english(sinhala_text: str) -> str:
    """Translate a Sinhala word/phrase to English using the dictionary,
    word-by-word fallback, and then deep_translator."""
    text = sinhala_text.strip()

    # 1. Direct dictionary lookup (full phrase)
    if text in WORD_TO_ENGLISH:
        return WORD_TO_ENGLISH[text]

    # 2. If multi-word, try each word individually and combine
    words = text.split()
    if len(words) > 1:
        translated_parts = []
        for word in words:
            if word in WORD_TO_ENGLISH:
                translated_parts.append(WORD_TO_ENGLISH[word])
            else:
                # Try deep_translator for individual word
                try:
                    from deep_translator import GoogleTranslator
                    t = GoogleTranslator(source='si', target='en').translate(word)
                    if t and t.strip() and t.strip().lower() != word:
                        translated_parts.append(t.strip())
                    else:
                        translated_parts.append(word)
                except Exception:
                    translated_parts.append(word)
        combined = ' '.join(translated_parts)
        print(f"  [Word-by-word translation] '{text}' -> '{combined}'")
        return combined

    # 3. Single unknown word - try deep_translator
    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source='si', target='en').translate(text)
        if result and result.strip() and result.strip().lower() != text:
            print(f"  [deep_translator] '{text}' -> '{result.strip()}'")
            return result.strip()
    except Exception as e:
        print(f"  [deep_translator failed] {e}")

    # 4. Last resort - return as-is (will search by Sinhala, usually fails gracefully)
    return text


def find_real_image(sinhala_text: str, randomize: bool = False) -> Tuple[bytes, str]:
    """Main function to find a REAL image for a Sinhala word or phrase."""
    english_term = translate_sinhala_to_english(sinhala_text)

    print(f"\n🔍 Searching real image for: '{sinhala_text}' -> '{english_term}' (randomize={randomize})")

    # Use cache only for non-random requests
    if not randomize:
        cached = get_cached_image(english_term)
        if cached:
            return cached, "cache"

    # Build search variants (most specific first, then broader)
    base_words = english_term.split()
    variants = [english_term]
    if len(base_words) > 1:
        # Add the most meaningful single word as a fallback
        variants.append(base_words[0])
        variants.append(base_words[-1])
    variants += [
        f"clear photo of {english_term} without any text",
        f"single {english_term} isolated on white background",
        f"{english_term} clipart illustration",
        f"educational photo of {english_term}",
    ]
    
    # Specific boosters for problematic words
    if 'star' in english_term.lower():
        variants.insert(0, "twinkling stars in night sky photography")
    if 'school' in english_term.lower():
        variants.insert(0, "primary school building exterior")
    if 'sky' in english_term.lower():
        variants.insert(0, "clear blue sky with white clouds")
    if 'sun' in english_term.lower():
        variants.insert(0, "bright sun in the sky")
    # Remove duplicates while preserving order
    seen = set()
    unique_variants = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            unique_variants.append(v)
    variants = unique_variants

    if randomize:
        random.shuffle(variants)

    for term in variants:
        # 1. DuckDuckGo
        image_bytes = search_duckduckgo_image(term, randomize)
        if image_bytes:
            image_bytes = optimize_image(image_bytes)
            if not randomize:
                save_to_cache(english_term, image_bytes)
            return image_bytes, "DuckDuckGo (Web)"

        # 2. Wikimedia
        image_bytes = search_wikimedia(term, randomize)
        if image_bytes:
            image_bytes = optimize_image(image_bytes)
            if not randomize:
                save_to_cache(english_term, image_bytes)
            return image_bytes, "Wikimedia Commons"

        # 3. Wikipedia
        image_bytes = search_wikipedia_image(term, randomize)
        if image_bytes:
            image_bytes = optimize_image(image_bytes)
            if not randomize:
                save_to_cache(english_term, image_bytes)
            return image_bytes, "Wikipedia"

        # 4. Pixabay (if API key set)
        image_bytes = search_pixabay(term, randomize)
        if image_bytes:
            image_bytes = optimize_image(image_bytes)
            if not randomize:
                save_to_cache(english_term, image_bytes)
            return image_bytes, "Pixabay"

    # All sources failed - generate placeholder with English label
    print(f"  ❌ All image sources failed for '{english_term}'. Using placeholder.")
    return generate_simple_placeholder(f"{sinhala_text}\n({english_term})"), "placeholder"


# ============================================================
# ENDPOINTS
# ============================================================

@text_to_image_bp.route('/generate-image', methods=['POST'])
def generate_image_endpoint():
    try:
        data = request.get_json()
        sinhala_text = data.get('prompt', '')
        randomize = data.get('randomize', False)

        if not sinhala_text:
            return jsonify({"error": "missing_prompt"}), 400

        image_bytes, source = find_real_image(sinhala_text, randomize)
        english_term = translate_sinhala_to_english(sinhala_text)
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

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


@text_to_image_bp.route('/ocr-and-generate', methods=['POST'])
def ocr_and_generate():
    model, labels = get_model()
    
    if "file" not in request.files:
        return jsonify({"error": "missing_file"}), 400

    try:
        file = request.files["file"]
        content = file.read()
        
        # If the model is not loaded (mock mode fallback)
        if model is None or labels is None:
             import random
             mock_word = random.choice(list(WORD_TO_ENGLISH.keys()))
             confidence = random.uniform(0.7, 0.95)
             image_bytes, source = find_real_image(mock_word)
             image_b64 = base64.b64encode(image_bytes).decode('utf-8')
             english_term = WORD_TO_ENGLISH.get(mock_word, mock_word)
             return jsonify({
                 "success": True,
                 "detected_text": mock_word,
                 "confidence": confidence,
                 "mock": True,
                 "image": image_b64,
                 "prompt_used": english_term,
                 "image_source": source,
             })
             
        batch = preprocess_image(content)
        preds = model.predict(batch)

        top_idx = int(np.argmax(preds[0]))

        if labels is not None and top_idx not in labels:
            return jsonify({
                "success": False,
                "error": "unknown_class",
                "class_id": top_idx,
                "detail": f"Model predicted Class {top_idx}, missing from labels.",
            }), 200

        detected_text = labels[top_idx]
        confidence = float(np.max(preds[0]))

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
