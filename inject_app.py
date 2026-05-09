import os
import re


with open('sinhala_dict_454.py', 'r', encoding='utf-8') as f:
    dict_content = f.read()


with open('app.py', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()


out_lines = []
skip = False
inject_dict_done = False

i = 0
while i < len(app_lines):
    line = app_lines[i]
    
    
    if line.startswith('SINHALA_LETTERS = {') and not inject_dict_done:
        out_lines.append(dict_content)
        inject_dict_done = True
        skip = True
    elif skip and line.strip() == '}':
        skip = False
        i += 1
        continue
    elif skip:
        i += 1
        continue
    else:
        
        out_lines.append(line)
        
    i += 1

app_content = "".join(out_lines)


get_rnd_old = """    if model and model.model_loaded and model.class_names:
        letter_id = random.randint(0, len(model.class_names) - 1)
        character = model.class_names[letter_id]
        romanized = character  # Use character itself if no romanized mapping"""

get_rnd_new = """    if model and model.model_loaded and model.class_names:
        letter_id = random.randint(0, len(model.class_names) - 1)
        class_str = model.class_names[letter_id]
        class_idx = int(class_str) if str(class_str).isdigit() else letter_id
        
        char_info = SINHALA_LETTERS.get(class_idx, {"name": class_str, "romanized": class_str})
        character = char_info["name"]
        romanized = char_info["romanized"]"""
        
app_content = app_content.replace(get_rnd_old, get_rnd_new)


predict_old = """        if model and model.model_loaded:
            prediction = model.predict(image)
            confidence_val = float(prediction.get('confidence', 0.0))
            score_val = round(confidence_val * 100, 2)
            predicted_letter = prediction['top_3'][0]['letter'] if prediction.get('top_3') else 'Unknown'"""

predict_new = """        if model and model.model_loaded:
            prediction = model.predict(image)
            confidence_val = float(prediction.get('confidence', 0.0))
            score_val = round(confidence_val * 100, 2)
            
            raw_letter = prediction['top_3'][0]['letter'] if prediction.get('top_3') else 'Unknown'
            # Convert class format e.g. "10" to actual Sinhala character
            if str(raw_letter).isdigit():
                predicted_letter = SINHALA_LETTERS.get(int(raw_letter), {}).get('name', raw_letter)
            else:
                predicted_letter = raw_letter
"""
app_content = app_content.replace(predict_old, predict_new)


mock_old = """        else:
            # Mock for development when model is not loaded
            # Use random score between 60.0 and 95.0
            mock_score = random.uniform(60.0, 95.0)
            mock_confidence = mock_score / 100.0
            is_correct = mock_score >= 70.0
            
            return jsonify({
                'success': True,
                'score': round(mock_score, 1),
                'confidence': mock_confidence,
                'is_correct': is_correct,
                'feedback': 'Mock Correct!' if is_correct else 'Mock Incorrect!',
                'predicted_letter': expected_letter if expected_letter else 'Mock',
                'mock': True
            })"""

mock_new = """        else:
            return jsonify({'success': False, 'message': 'Handwriting Model is offline'}), 503"""

app_content = app_content.replace(mock_old, mock_new)


with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)
    
print("Successfully patched app.py!")
