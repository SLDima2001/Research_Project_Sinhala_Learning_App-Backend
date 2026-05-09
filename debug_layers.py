import os

os.environ["TF_USE_LEGACY_KERAS"] = "1"

import tensorflow as tf
import tf_keras

print(f"TensorFlow Version: {tf.__version__}")

MODEL_PATH = os.path.join("model", "sinhala_handwriting_model (1).h5")

print("\n--- Attempting load with tf.keras (Legacy Env Var) ---")
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("[OK] Loaded with tf.keras")
except Exception as e:
    print(f"[FAIL] tf.keras load failed: {e}")

print("\n--- Attempting load with tf_keras (Explicit) ---")
try:
    model = tf_keras.models.load_model(MODEL_PATH)
    print("[OK] Loaded with tf_keras")
except Exception as e:
    print(f"[FAIL] tf_keras load failed: {e}")

print("\n--- Attempting load with tf.keras + compile=False ---")
try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("[OK] Loaded with tf.keras (compile=False)")
except Exception as e:
    print(f"[FAIL] tf.keras (compile=False) load failed: {e}")
