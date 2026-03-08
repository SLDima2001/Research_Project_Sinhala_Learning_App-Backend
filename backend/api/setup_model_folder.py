"""
Run this script to check your model folder setup
It will tell you exactly where to place your model files
"""

import os

print("=" * 70)
print("SINHALA LEARNING APP - MODEL FOLDER SETUP")
print("=" * 70)

# Get the correct paths
script_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = script_dir  # We're in api/ folder
project_root = os.path.dirname(api_dir)

print(f"\n📁 Project Structure:")
print(f"   Project Root: {project_root}")
print(f"   API Folder:   {api_dir}")

# Where models should be
models_dir = os.path.join(api_dir, "models")
sinhala_asr_dir = os.path.join(models_dir, "sinhala_asr")

print(f"\n📦 Model Location:")
print(f"   {sinhala_asr_dir}")

# Check if folders exist
print(f"\n🔍 Checking folders...")

if not os.path.exists(models_dir):
    print(f"   ❌ MISSING: models/ folder")
    print(f"   Creating: {models_dir}")
    os.makedirs(models_dir)
    print(f"   [OK] Created models/ folder")
else:
    print(f"   [OK] models/ folder exists")

if not os.path.exists(sinhala_asr_dir):
    print(f"   ❌ MISSING: sinhala_asr/ folder")
    print(f"   Creating: {sinhala_asr_dir}")
    os.makedirs(sinhala_asr_dir)
    print(f"   [OK] Created sinhala_asr/ folder")
else:
    print(f"   [OK] sinhala_asr/ folder exists")

# Check for model files
print(f"\n📋 Checking model files...")
required_files = [
    "config.json",
    "vocab.json",
    "preprocessor_config.json", 
    "tokenizer_config.json",
    "model.safetensors"  # or pytorch_model.bin
]

missing_files = []
for file_name in required_files:
    file_path = os.path.join(sinhala_asr_dir, file_name)
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"   [OK] {file_name} ({file_size:.2f} MB)")
    else:
        print(f"   ❌ MISSING: {file_name}")
        missing_files.append(file_name)

# Special check for model file (could be .safetensors or .bin)
model_files = ["model.safetensors", "pytorch_model.bin"]
has_model = any(os.path.exists(os.path.join(sinhala_asr_dir, f)) for f in model_files)

if not has_model:
    print(f"   ❌ MISSING: model.safetensors OR pytorch_model.bin")

print("\n" + "=" * 70)

if missing_files or not has_model:
    print("❌ SETUP INCOMPLETE")
    print("=" * 70)
    print("\n📥 NEXT STEPS:")
    print("\n1. Go to your Kaggle notebook")
    print("2. Download ALL files from the output folder: sinhala_asr_final/")
    print("3. Copy them to this folder:")
    print(f"\n   {sinhala_asr_dir}")
    print("\n4. Your folder structure should look like this:")
    print(f"""
   sinhala_app_backend/
   └── api/
       ├── models/
       │   └── sinhala_asr/
       │       ├── config.json
       │       ├── vocab.json
       │       ├── preprocessor_config.json
       │       ├── tokenizer_config.json
       │       └── model.safetensors
       ├── modules/
       │   └── speech_feedback/
       ├── app.py
       └── requirements.txt
    """)
    print("\n5. After copying files, run this script again to verify")
else:
    print("✅ SETUP COMPLETE!")
    print("=" * 70)
    print("\nAll model files are in place! You can now run:")
    print("   python app.py")

print("\n" + "=" * 70)
