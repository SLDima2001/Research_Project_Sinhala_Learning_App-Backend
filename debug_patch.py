import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import tf_keras
import tensorflow as tf

print(f"tf_keras version: {tf_keras.__version__}")

MODEL_PATH = os.path.join("model", "sinhala_handwriting_model (1).h5")

class PatchedInputLayer(tf_keras.layers.InputLayer):
    def __init__(self, *args, **kwargs):
        # Handle 'batch_shape' which might be present in old configs
        # but unrecognized by newer InputLayer
        if 'batch_shape' in kwargs:
            print(f"PatchedInputLayer: Remapping 'batch_shape' {kwargs['batch_shape']}")
            # Keras 2 usually expects batch_input_shape
            if 'batch_input_shape' not in kwargs:
                kwargs['batch_input_shape'] = kwargs.pop('batch_shape')
            else:
                kwargs.pop('batch_shape')
        super().__init__(*args, **kwargs)

try:
    print(f"Attempting to load {MODEL_PATH} with PatchedInputLayer...")
    model = tf_keras.models.load_model(
        MODEL_PATH,
        custom_objects={'InputLayer': PatchedInputLayer}
    )
    print("SUCCESS: Model loaded with patch!")
    model.summary()
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
