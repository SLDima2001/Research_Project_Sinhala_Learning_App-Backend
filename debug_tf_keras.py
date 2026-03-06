import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import tf_keras
import tensorflow as tf

print(f"tf_keras version: {tf_keras.__version__}")
print(f"tensorflow version: {tf.__version__}")

MODEL_PATH = os.path.join("model", "sinhala_handwriting_model (1).h5")

try:
    print(f"Attempting to load {MODEL_PATH} with tf_keras...")
    model = tf_keras.models.load_model(MODEL_PATH)
    print("SUCCESS")
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
