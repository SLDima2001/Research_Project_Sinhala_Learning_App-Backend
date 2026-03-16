import json
import traceback

try:
    with open('original_app.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    start = content.find('SINHALA_LETTERS = {')
    end = content.find('}', start) + 1
    
    dict_str = content[start:end]
    
    with open('sinhala_dict.py', 'w', encoding='utf-8') as f:
        f.write(dict_str)
        
    print("Extracted dict")
except Exception as e:
    traceback.print_exc()
