import os
import io
import json
import base64
import hashlib
import requests
from typing import Tuple, Dict, Optional
from flask import Blueprint, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tensorflow as tf

text_to_image_bp = Blueprint('text_to_image', __name__)

# Configuration
MODEL_75_PATH = os.environ.get("MODEL_75_PATH", os.path.join("model", "sinhala_handwriting_model (1).h5"))
LABELS_75_PATH = os.environ.get("LABELS_75_PATH", "label_map.json")
IMG_SIZE = (224, 224)

# Cache directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(PROJECT_ROOT, "image_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Word mapping for search
WORD_TO_ENGLISH = {
    'බල්ලා': 'dog', 'බළලා': 'cat', 'ගස': 'tree', 'මල': 'flower',
    'අහස': 'blue sky', 'හිරු': 'sun', 'ගෙදර': 'house', 'පාසල': 'school'
}

# In-memory model
_model_75 = None
_idx_to_label_75 = None

def get_model():
    global _model_75, _idx_to_label_75
    if _model_75 is None:
        try:
            if os.path.exists(MODEL_75_PATH):
                base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False, weights=None)
                x = base_model.output
                x = tf.keras.layers.GlobalAveragePooling2D()(x)
                predictions = tf.keras.layers.Dense(75, activation='softmax')(x)
                _model_75 = tf.keras.models.Model(inputs=base_model.input, outputs=predictions)
                _model_75.load_weights(MODEL_75_PATH, by_name=True, skip_mismatch=True)
                
                if os.path.exists(LABELS_75_PATH):
                    with open(LABELS_75_PATH, "r", encoding="utf-8") as f:
                        _idx_to_label_75 = {int(k): v for k, v in json.load(f).items()}
        except Exception as e:
            print(f"Error loading 75-class model: {e}")
    return _model_75, _idx_to_label_75

@text_to_image_bp.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    sinhala_text = data.get('prompt', '')
    if not sinhala_text:
        return jsonify({"error": "missing_prompt"}), 400
    
    # Simple search or placeholder...
    img = Image.new('RGB', (512, 512), color=(147, 51, 234))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return jsonify({
        "success": True,
        "image": img_b64,
        "detected_text": sinhala_text
    })

@text_to_image_bp.route('/ocr-and-generate', methods=['POST'])
def ocr_and_generate():
    model, labels = get_model()
    if model is None:
        return jsonify({"error": "Model not available"}), 500
    
    if "file" not in request.files:
        return jsonify({"error": "missing_file"}), 400
    
    # Process OCR ...
    return jsonify({"success": True, "label": "Mock Word", "image": "..."})
