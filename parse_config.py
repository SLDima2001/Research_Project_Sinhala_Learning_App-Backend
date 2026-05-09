import json
import re

filename = "h5_config.txt"

try:
    with open(filename, 'r') as f:
        content = f.read()
        
    
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        json_str = match.group(0)
        data = json.loads(json_str)
        
        layers = data['config']['layers']
        print(f"Total layers: {len(layers)}")
        
        
        for i, layer in enumerate(layers):
            name = layer['config'].get('name', 'unknown')
            cls = layer['class_name']
            print(f"{i}: {cls} - {name}")
            
            
            if 'Conv1' in name:
                print(f"   -> Likely MobileNet start: {layer['config']}")
            
            
            if cls in ['Dense', 'GlobalAveragePooling2D', 'Flatten', 'Dropout']:
                print(f"   -> Top Layer config: {layer['config']}")
                
    else:
        print("Could not find JSON in file")
        
except Exception as e:
    print(f"Error: {e}")
