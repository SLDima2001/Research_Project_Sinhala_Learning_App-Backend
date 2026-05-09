import os
import sys


sys.path.append(os.getcwd())

from sinhala_model import SinhalaHandwritingModel
import numpy as np

def verify():
    print("RUNNING FINAL VERIFICATION...")
    
    
    model_path = 'model/sinhala_handwriting_v2.keras'
    model = SinhalaHandwritingModel(model_path)
    
    if not model.model_loaded:
        print("FAIL: Model failed to load!")
        return
    
    print(f"SUCCESS: Model loaded with {len(model.class_names)} classes")
    print(f"Input dimensions: {model.img_width}x{model.img_height}")
    
    
    dummy_img = np.zeros((32, 32), dtype=np.uint8)
    prediction = model.predict(dummy_img)
    
    print("\nPrediction test:")
    print(f"Predicted Class: {prediction['predicted_class']}")
    print(f"Mode: {prediction.get('model_mode', 'unknown')}")
    print(f"Top 3: {prediction['top_3']}")
    
    if prediction.get('model_mode') == 'trained':
        print("\n✓ VERIFICATION SUCCESSFUL")
    else:
        print("\n✗ VERIFICATION FAILED: Mock mode still active")

if __name__ == "__main__":
    verify()
