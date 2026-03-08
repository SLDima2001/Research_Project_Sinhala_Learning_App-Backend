"""
Download the Sinhala ASR model from HuggingFace Hub.

Run this script after cloning the repo to get the model files:
    python download_model.py

Requirements:
    pip install huggingface_hub
"""

from huggingface_hub import snapshot_download
import os

MODEL_REPO = "sandu-2000/sinhala-asr-model"
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "sinhala_asr")

def download_model():
    print(f"Downloading Sinhala ASR model from HuggingFace: {MODEL_REPO}")
    print(f"Saving to: {MODEL_DIR}")
    
    snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=MODEL_DIR,
    )
    
    print("\nModel downloaded successfully!")
    print(f"Files saved to: {MODEL_DIR}")

if __name__ == "__main__":
    download_model()
