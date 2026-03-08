"""
Sinhala Handwriting Recognition - Quick Reference & Utilities
Common tasks and utilities for model training and testing
"""

import os
import sys
from pathlib import Path
import json
import numpy as np
import cv2
from sinhala_model import SinhalaHandwritingModel

class QuickReference:
    """Quick reference utilities for common tasks"""
    
    @staticmethod
    def check_dataset():
        """Check dataset status"""
        print("\n" + "=" * 70)
        print("DATASET STATUS CHECK")
        print("=" * 70)
        
        train_path = Path("../dataset/train")
        test_path = Path("../dataset/test")
        valid_path = Path("../dataset/valid")
        
        for dataset_type, path in [("Train", train_path), ("Test", test_path), ("Valid", valid_path)]:
            if path.exists():
                folders = [d for d in path.iterdir() if d.is_dir()]
                total_images = sum(len(list(f.glob("*.png")) + list(f.glob("*.jpg"))) 
                                 for f in folders)
                print(f"\n[OK] {dataset_type} Dataset:")
                print(f"  Path: {path.absolute()}")
                print(f"  Classes: {len(folders)}")
                print(f"  Total Images: {total_images}")
                if folders:
                    avg_per_class = total_images // len(folders)
                    print(f"  Average per class: {avg_per_class}")
            else:
                print(f"\n[ERROR] {dataset_type} Dataset: NOT FOUND")
        
        print(f"\n{'=' * 70}\n")
    
    @staticmethod
    def check_model():
        """Check trained model status"""
        print("\n" + "=" * 70)
        print("MODEL STATUS CHECK")
        print("=" * 70)
        
        model_path = Path("models/sinhala_model.keras")
        info_path = Path("models/sinhala_model_info.json")
        history_path = Path("models/sinhala_model_history.json")
        
        print(f"\nModel Files:")
        
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"[OK] Model: {model_path.name} ({size_mb:.2f} MB)")
        else:
            print(f"[ERROR] Model: NOT FOUND")
        
        if info_path.exists():
            with open(info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
            print(f"[OK] Info: {info_path.name}")
            print(f"  - Classes: {info.get('num_classes', 'N/A')}")
            print(f"  - Image Size: {info.get('img_width', 'N/A')}x{info.get('img_height', 'N/A')}")
            print(f"  - Parameters: {info.get('total_parameters', 'N/A'):,}")
        else:
            print(f"[ERROR] Info: NOT FOUND")
        
        if history_path.exists():
            with open(history_path, 'r') as f:
                history = json.load(f)
            print(f"[OK] History: {history_path.name}")
            print(f"  - Epochs: {len(history.get('loss', []))}")
            if 'accuracy' in history:
                final_acc = history['accuracy'][-1]
                print(f"  - Final Training Accuracy: {final_acc * 100:.2f}%")
            if 'val_accuracy' in history:
                final_val_acc = history['val_accuracy'][-1]
                print(f"  - Final Validation Accuracy: {final_val_acc * 100:.2f}%")
        else:
            print(f"[ERROR] History: NOT FOUND")
        
        print(f"\n{'=' * 70}\n")
    
    @staticmethod
    def predict_image(image_path):
        """Predict a single image"""
        print("\n" + "=" * 70)
        print("SINGLE IMAGE PREDICTION")
        print("=" * 70)
        
        if not os.path.exists(image_path):
            print(f"[ERROR] Image not found: {image_path}")
            return
        
        print(f"\nLoading model...")
        model = SinhalaHandwritingModel()
        
        print(f"Predicting: {image_path}")
        result = model.predict(image_path)
        
        print(f"\nResults:")
        print(f"  Predicted Class: {result['predicted_class']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Model Mode: {result.get('model_mode', 'unknown')}")
        
        if 'top_3' in result:
            print(f"\n  Top 3 Predictions:")
            for i, pred in enumerate(result['top_3'], 1):
                print(f"    {i}. Class {pred['class']}: {pred['confidence']:.2%}")
        
        print(f"\n{'=' * 70}\n")
    
    @staticmethod
    def calculate_score(image_path, correct_class):
        """Calculate handwriting score"""
        print("\n" + "=" * 70)
        print("HANDWRITING SCORE CALCULATION")
        print("=" * 70)
        
        if not os.path.exists(image_path):
            print(f"[ERROR] Image not found: {image_path}")
            return
        
        print(f"\nLoading model...")
        model = SinhalaHandwritingModel()
        
        print(f"Calculating score for: {image_path}")
        print(f"Correct class: {correct_class}")
        
        score_result = model.calculate_score(image_path, correct_class)
        
        print(f"\nScore Results:")
        print(f"  Score: {score_result['score']}/100")
        print(f"  Is Correct: {score_result['is_correct']}")
        print(f"  Confidence: {score_result['confidence']:.2%}")
        print(f"  Model Loaded: {score_result['model_loaded']}")
        
        print(f"\nQuality Metrics:")
        quality = score_result['quality']
        print(f"  Has Content: {quality['has_content']}")
        print(f"  Coverage: {quality['coverage']:.2%}")
        print(f"  Complexity: {quality['complexity']}")
        
        print(f"\n{'=' * 70}\n")
    
    @staticmethod
    def batch_predict(image_folder):
        """Predict multiple images"""
        print("\n" + "=" * 70)
        print("BATCH PREDICTION")
        print("=" * 70)
        
        image_folder = Path(image_folder)
        if not image_folder.exists():
            print(f"[ERROR] Folder not found: {image_folder}")
            return
        
        image_files = list(image_folder.glob("*.png")) + \
                     list(image_folder.glob("*.jpg")) + \
                     list(image_folder.glob("*.jpeg"))
        
        if not image_files:
            print(f"[ERROR] No images found in: {image_folder}")
            return
        
        print(f"\nFound {len(image_files)} images")
        print(f"Loading model...")
        model = SinhalaHandwritingModel()
        
        print(f"Predicting...")
        results = model.batch_predict(image_files)
        
        print(f"\nResults:")
        for i, (img_path, result) in enumerate(zip(image_files, results), 1):
            print(f"  {i}. {img_path.name}")
            print(f"     Class: {result['predicted_class']}, Confidence: {result['confidence']:.2%}")
        
        print(f"\n{'=' * 70}\n")
    
    @staticmethod
    def show_help():
        """Show help information"""
        help_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║     SINHALA HANDWRITING RECOGNITION - QUICK REFERENCE                      ║
╚════════════════════════════════════════════════════════════════════════════╝

TRAINING:
  python train_sinhala_model.py          Train the model
  train.bat                              Quick start training (Windows)

TESTING:
  python test_model.py                   Full model testing
  python quick_reference.py check        Check dataset status
  python quick_reference.py model        Check model status

PREDICTION:
  python quick_reference.py predict <image_path>
                                         Predict single image
  python quick_reference.py score <image_path> <class>
                                         Calculate handwriting score
  python quick_reference.py batch <folder>
                                         Predict multiple images

UTILITIES:
  python check_dataset.py                Validate dataset structure
  python sinhala_model.py                Test model directly

EXAMPLES:
  python quick_reference.py check
  python quick_reference.py model
  python quick_reference.py predict ../dataset/train/1/1.png
  python quick_reference.py score ../dataset/train/1/1.png 1
  python quick_reference.py batch ../dataset/train/1

FILES:
  train_sinhala_model.py                 Main training script
  sinhala_model.py                       Model inference
  test_model.py                          Model testing
  quick_reference.py                     This utility
  TRAINING_GUIDE.md                      Detailed guide

MODELS FOLDER:
  sinhala_model.keras                    Trained model
  sinhala_model_info.json                Model metadata
  sinhala_model_history.json             Training history
  training_history.png                   Performance graphs
  confusion_matrix.png                   Confusion matrix
  classification_report.txt              Detailed metrics

╔════════════════════════════════════════════════════════════════════════════╗
║                          For more help, see TRAINING_GUIDE.md              ║
╚════════════════════════════════════════════════════════════════════════════╝
        """
        print(help_text)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        QuickReference.show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "check":
        QuickReference.check_dataset()
    
    elif command == "model":
        QuickReference.check_model()
    
    elif command == "predict":
        if len(sys.argv) < 3:
            print("Usage: python quick_reference.py predict <image_path>")
            return
        QuickReference.predict_image(sys.argv[2])
    
    elif command == "score":
        if len(sys.argv) < 4:
            print("Usage: python quick_reference.py score <image_path> <correct_class>")
            return
        try:
            correct_class = int(sys.argv[3])
            QuickReference.calculate_score(sys.argv[2], correct_class)
        except ValueError:
            print("Error: correct_class must be an integer")
    
    elif command == "batch":
        if len(sys.argv) < 3:
            print("Usage: python quick_reference.py batch <folder>")
            return
        QuickReference.batch_predict(sys.argv[2])
    
    elif command == "help":
        QuickReference.show_help()
    
    else:
        print(f"Unknown command: {command}")
        QuickReference.show_help()


if __name__ == "__main__":
    main()
