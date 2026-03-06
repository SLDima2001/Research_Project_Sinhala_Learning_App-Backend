from pymongo import MongoClient

client = MongoClient('mongodb+srv://root:Dima2001@customerfeedback.83hfgpu.mongodb.net/?retryWrites=true&w=majority&appName=customerfeedback')
db = client['customerfeedback']

# Test parsing logic
count = 0
for i, doc in enumerate(db.metadata.find().limit(5)):
    print(f"\nDocument {i}:")
    for key, value in doc.items():
        if key == '_id':
            continue
        print(f'  Key type: {type(key)}')
        print(f'  Key length: {len(key)}')
        print(f'  Key preview: {repr(key[:50])}...')
        has_pipe = '|' in key
        print(f'  Has pipe: {has_pipe}')
        if has_pipe:
            parts = key.split('|', 1)
            filename = parts[0].strip()
            text = parts[1].strip() if len(parts) > 1 else ''
            print(f'  Filename: {filename}')
            print(f'  Text: {text[:50]}...')
            count += 1

print(f'\nTotal parsed: {count} sentences from 5 documents')
