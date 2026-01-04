import os
import io
import json
import base64
from typing import Tuple, Dict
import requests

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf

# Configuration
MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join("model", "sinhala_handwriting_model (1).h5"))
LABELS_PATH = os.environ.get("LABELS_PATH", "label_map.json")
PORT = int(os.environ.get("PORT", 5001))
HOST = os.environ.get("HOST", "0.0.0.0")
IMG_SIZE: Tuple[int, int] = (224, 224)

# Image Generation API Configuration
# Option 1: Hugging Face Inference API (Free tier available)
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")
HUGGINGFACE_MODEL = "stabilityai/stable-diffusion-2-1"

# Option 2: Replicate API
REPLICATE_API_KEY = os.environ.get("REPLICATE_API_KEY", "")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

model = None
idx_to_label = None

# Mapping Sinhala words to English prompts for image generation
WORD_TO_PROMPT: Dict[str, str] = {
    'බල්ලා': 'a cute friendly dog playing in a colorful garden, children\'s book illustration style',
    'බළලා': 'a playful cat with big expressive eyes, children\'s book illustration style',
    'ගස': 'a big beautiful tree with green leaves and birds, children\'s book illustration style',
    'මල': 'colorful flowers blooming in a garden, children\'s book illustration style',
    'අහස': 'beautiful blue sky with fluffy white clouds, children\'s book illustration style',
    'හිරු': 'bright cheerful sun with rays shining, children\'s book illustration style',
    'චන්දය': 'crescent moon glowing in the starry night sky, children\'s book illustration style',
    'තරු': 'twinkling stars scattered across the night sky, children\'s book illustration style',
    'ගෙදර': 'a cozy beautiful house with a garden and fence, children\'s book illustration style',
    'බස්': 'a colorful school bus on the road, children\'s book illustration style',
    'කාර්': 'a shiny red car on a street, children\'s book illustration style',
    'පාසල': 'a school building with happy children playing, children\'s book illustration style',
    'පුටුව': 'a comfortable wooden chair, children\'s book illustration style',
    'මේසය': 'a study table with books and pencils, children\'s book illustration style',
    'පොත': 'colorful storybooks stacked together, children\'s book illustration style',
    'පන්සල': 'a pencil for writing and drawing, children\'s book illustration style',
    'මිනිසා': 'a friendly smiling person, children\'s book illustration style',
    'ළමයා': 'a happy child playing, children\'s book illustration style',
    'එළුවා': 'a white goat in a farm, children\'s book illustration style',
    'බුකුටා': 'a colorful rooster, children\'s book illustration style',
    # Add more mappings based on your dataset
}


def load_artifacts():
    """Load the trained model and label mappings"""
    global model, idx_to_label

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    if not os.path.exists(LABELS_PATH):
        raise FileNotFoundError(f"Label map not found at {LABELS_PATH}")

    # Load the trained TensorFlow model
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"✓ Model loaded from {MODEL_PATH}")

    # Load label mappings
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
    arr = np.expand_dims(arr, axis=0)  # shape (1, 224, 224, 3)
    return arr


def generate_image_huggingface(prompt: str) -> bytes:
    """Generate image using Hugging Face Inference API"""
    API_URL = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": prompt},
        timeout=60
    )
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Image generation failed: {response.text}")


def generate_image_replicate(prompt: str) -> bytes:
    """Generate image using Replicate API"""
    import replicate
    
    output = replicate.run(
        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        input={"prompt": prompt}
    )
    
    # Download the generated image
    image_url = output[0]
    response = requests.get(image_url, timeout=30)
    return response.content


def generate_simple_placeholder(text: str) -> bytes:
    """Generate a simple placeholder image with the detected text"""
    from PIL import ImageDraw, ImageFont
    
    # Create a colorful background
    img = Image.new('RGB', (512, 512), color=(147, 51, 234))
    draw = ImageDraw.Draw(img)
    
    # Try to load a Unicode font that supports Sinhala
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansSinhala-Regular.ttf", 60)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
    
    # Draw the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (512 - text_width) // 2
    y = (512 - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


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
        
        # Get top prediction
        probs = preds[0]
        top_idx = int(np.argmax(probs))
        top_label = idx_to_label.get(top_idx, str(top_idx))
        top_conf = float(np.max(probs))
        
        # Get top 3 predictions
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
        return jsonify({"error": "inference_failed", "detail": str(e)}), 500


@app.post("/generate-image")
def generate_image():
    """Generate image from Sinhala text prompt"""
    try:
        data = request.get_json()
        sinhala_text = data.get('prompt', '')
        
        if not sinhala_text:
            return jsonify({"error": "missing_prompt"}), 400
        
        # Get English prompt for the Sinhala word
        english_prompt = WORD_TO_PROMPT.get(
            sinhala_text,
            f"beautiful illustration of {sinhala_text}, children's book style"
        )
        
        print(f"Generating image for: {sinhala_text} -> {english_prompt}")
        
        # Try different image generation methods
        image_bytes = None
        
        # Method 1: Use Hugging Face if API key is available
        if HUGGINGFACE_API_KEY:
            try:
                image_bytes = generate_image_huggingface(english_prompt)
                print("✓ Generated using Hugging Face")
            except Exception as e:
                print(f"Hugging Face failed: {e}")
        
        # Method 2: Use Replicate if API key is available
        if not image_bytes and REPLICATE_API_KEY:
            try:
                image_bytes = generate_image_replicate(english_prompt)
                print("✓ Generated using Replicate")
            except Exception as e:
                print(f"Replicate failed: {e}")
        
        # Method 3: Fallback to placeholder
        if not image_bytes:
            print("Using placeholder image")
            image_bytes = generate_simple_placeholder(sinhala_text)
        
        # Convert to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        return jsonify({
            "success": True,
            "image": image_b64,
            "detected_text": sinhala_text,
            "prompt_used": english_prompt
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "generation_failed",
            "detail": str(e)
        }), 500


@app.post("/ocr-and-generate")
def ocr_and_generate():
    """Combined endpoint: OCR + Image Generation"""
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
        detected_text = idx_to_label.get(top_idx, str(top_idx))
        confidence = float(np.max(preds[0]))
        
        print(f"Detected: {detected_text} (confidence: {confidence:.2f})")
        
        # Step 2: Generate Image
        english_prompt = WORD_TO_PROMPT.get(
            detected_text,
            f"beautiful illustration of {detected_text}, children's book style"
        )
        
        # Try to generate image
        image_bytes = None
        
        if HUGGINGFACE_API_KEY:
            try:
                image_bytes = generate_image_huggingface(english_prompt)
            except Exception as e:
                print(f"HF failed: {e}")
        
        if not image_bytes and REPLICATE_API_KEY:
            try:
                image_bytes = generate_image_replicate(english_prompt)
            except Exception as e:
                print(f"Replicate failed: {e}")
        
        if not image_bytes:
            image_bytes = generate_simple_placeholder(detected_text)
        
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        return jsonify({
            "success": True,
            "detected_text": detected_text,
            "confidence": confidence,
            "image": image_b64,
            "prompt_used": english_prompt
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "processing_failed",
            "detail": str(e)
        }), 500


if __name__ == "__main__":
    # Warm-up prediction to reduce first-request latency
    if load_error is None and model is not None:
        print("Warming up model...")
        dummy = np.zeros((1, IMG_SIZE[0], IMG_SIZE[1], 3), dtype="float32")
        try:
            _ = model.predict(dummy)
            print("✓ Model ready")
        except Exception as e:
            print(f"Warm-up failed: {e}")
    
    print(f"\n🚀 Starting server on {HOST}:{PORT}")
    print(f"📱 Mobile app should use: http://YOUR_IP_ADDRESS:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)