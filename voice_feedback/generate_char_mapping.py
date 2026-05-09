"""
Generate char_mapping.json from your existing Kaggle model
Run this ONCE after placing your Kaggle model files
"""

import json
import os
from transformers import Wav2Vec2Processor


MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "sinhal_asr")

print("=" * 60)
print("🔧 GENERATING char_mapping.json")
print("=" * 60)
print(f"📁 Looking for model at: {MODEL_PATH}")


if not os.path.exists(MODEL_PATH):
    print(f"❌ ERROR: Model folder not found at {MODEL_PATH}")
    print("\n📋 Expected structure:")
    print("   sinhala_app_backend/")
    print("   ├── models/")
    print("   │   └── sinhal_asr/")
    print("   │       ├── pytorch_model.bin")
    print("   │       ├── config.json")
    print("   │       ├── vocab.json")
    print("   │       └── ...")
    print("\n💡 Please place your Kaggle model files in that folder!")
    exit(1)

print("✅ Model folder found!")


required_files = ["config.json", "preprocessor_config.json", "tokenizer_config.json", "vocab.json"]
missing_files = []

for file in required_files:
    file_path = os.path.join(MODEL_PATH, file)
    if os.path.exists(file_path):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} MISSING!")
        missing_files.append(file)

if missing_files:
    print(f"\n❌ ERROR: Missing files: {', '.join(missing_files)}")
    print("\n💡 Make sure you downloaded ALL files from your Kaggle training!")
    exit(1)

print("\n📝 Loading processor...")

try:
    
    processor = Wav2Vec2Processor.from_pretrained(MODEL_PATH, local_files_only=True)
    
    
    char_to_idx = processor.tokenizer.get_vocab()
    
    
    output_path = os.path.join(MODEL_PATH, "char_mapping.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(char_to_idx, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Successfully created: {output_path}")
    print(f"📊 Vocabulary size: {len(char_to_idx)} characters")
    print("\n📋 Sample characters from your vocabulary:")
    
    
    for i, (char, idx) in enumerate(list(char_to_idx.items())[:10]):
        display_char = char if char.isprintable() else f"[{repr(char)}]"
        print(f"   '{display_char}' → {idx}")
    
    print("\n" + "=" * 60)
    print("🎉 SUCCESS! Your Kaggle model is now ready to use!")
    print("=" * 60)
    print("\n✅ Next steps:")
    print("   1. Run: python check_backend.py")
    print("   2. If all checks pass, run: python app.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\n🔧 Troubleshooting:")
    print("   - Make sure all model files are in the 'models/sinhal_asr/' folder")
    print("   - Try: pip install transformers torch")
    print("   - Check if pytorch_model.bin exists and is not corrupted")
    exit(1)