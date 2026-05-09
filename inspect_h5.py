import h5py
import json
import os

MODEL_PATH = os.path.join("model", "sinhala_handwriting_model (1).h5")

def inspect_h5_keys(f, indent="  "):
    for key in f.keys():
        print(f"{indent}{key}")
        if isinstance(f[key], h5py.Group):
            
            pass

try:
    with h5py.File(MODEL_PATH, 'r') as f:
        print("Keys in H5 file:")
        inspect_h5_keys(f)
        
        if 'model_config' in f.attrs:
            print("\nFound model_config in attrs:")
            config_str = f.attrs['model_config']
            if isinstance(config_str, bytes):
                config_str = config_str.decode('utf-8')
            
            config = json.loads(config_str)
            print(json.dumps(config, indent=2))
        else:
            print("\nNo model_config found in attrs")
            
except Exception as e:
    print(f"Error inspecting file: {e}")
