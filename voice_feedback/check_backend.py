"""
Backend verification script
Run this BEFORE starting your Flask server to check everything is working
"""

import os
import sys

print("=" * 60)
print("SINHALA LEARNING APP - BACKEND VERIFICATION")
print("=" * 60)


print("\n1. Checking Python version...")
py_version = sys.version_info
print(f"   [OK] Python {py_version.major}.{py_version.minor}.{py_version.micro}")
if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 8):
    print("   [ERROR] WARNING: Python 3.8+ recommended")


print("\n2. Checking model files...")

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(script_dir, "models", "sinhala_asr")
print(f"   Model path: {MODEL_PATH}")

required_files = [
    "config.json",
    "vocab.json", 
    "preprocessor_config.json",
    "tokenizer_config.json",
    "model.safetensors"  
]

all_files_exist = True
for file in required_files:
    file_path = os.path.join(MODEL_PATH, file)
    if os.path.exists(file_path):
        print(f"   [OK] {file}")
    else:
        print(f"   [ERROR] MISSING: {file}")
        all_files_exist = False

if not all_files_exist:
    print("\n   ERROR: Some model files are missing!")
    print("   Make sure you copied ALL files from Kaggle output to:")
    print(f"   {MODEL_PATH}")
    sys.exit(1)


print("\n3. Checking dependencies...")
packages = [
    ("flask", "Flask"),
    ("flask_socketio", "Flask-SocketIO"),
    ("torch", "PyTorch"),
    ("transformers", "Transformers"),
    ("librosa", "Librosa"),
    ("eventlet", "Eventlet"),
    ("numpy", "NumPy")
]

missing_packages = []
for module_name, display_name in packages:
    try:
        __import__(module_name)
        print(f"   [OK] {display_name}")
    except ImportError:
        print(f"   [ERROR] MISSING: {display_name}")
        missing_packages.append(module_name)

if missing_packages:
    print("\n   ERROR: Missing packages!")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)


print("\n4. Loading model (this may take a minute)...")
try:
    from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
    
    processor = Wav2Vec2Processor.from_pretrained(MODEL_PATH, local_files_only=True)
    model = Wav2Vec2ForCTC.from_pretrained(MODEL_PATH, local_files_only=True)
    print("   [OK] Model loaded successfully!")
    print(f"   [OK] Vocab size: {len(processor.tokenizer)}")
    
except Exception as e:
    print(f"   [ERROR] ERROR: {str(e)}")
    sys.exit(1)


print("\n5. Testing inference with dummy audio...")
try:
    import torch
    import numpy as np
    
    
    dummy_audio = np.zeros(16000)
    
    inputs = processor(dummy_audio, sampling_rate=16000, return_tensors="pt")
    
    with torch.no_grad():
        logits = model(inputs.input_values).logits
    
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]
    
    print(f"   [OK] Inference successful!")
    print(f"   [OK] Test transcription: '{transcription}'")
    
except Exception as e:
    print(f"   [ERROR] ERROR: {str(e)}")
    sys.exit(1)


print("\n6. Checking folder structure...")
required_dirs = [
    "modules/speech_feedback",
    "uploads"
]

for dir_path in required_dirs:
    if os.path.exists(dir_path):
        print(f"   [OK] {dir_path}/")
    else:
        print(f"   [ERROR] Creating: {dir_path}/")
        os.makedirs(dir_path, exist_ok=True)

print("\n" + "=" * 60)
print("ALL CHECKS PASSED! [OK]")
print("=" * 60)
print("\nYou can now start the backend server:")
print("   python app.py")
print("\nThe server will run at: http://0.0.0.0:5000")
print("From Android emulator, use: http://10.0.2.2:5000")
print("=" * 60)