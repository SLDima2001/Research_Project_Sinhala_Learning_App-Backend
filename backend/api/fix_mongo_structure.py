from pymongo import MongoClient

client = MongoClient('mongodb+srv://root:Dima2001@customerfeedback.83hfgpu.mongodb.net/?retryWrites=true&w=majority&appName=customerfeedback')
db = client['customerfeedback']

# Delete all metadata records
result = db.metadata.delete_many({})
print(f"Deleted {result.deleted_count} documents from metadata collection")

# Recreate with proper structure - extract unique sentences from existing data
# Get all unique sentences from current metadata
unique_sentences = {}
for doc in db.metadata.find():
    for key in doc.keys():
        if key != '_id' and '|' in key:
            parts = key.split('|', 1)
            filename = parts[0].strip()
            text = parts[1].strip()
            if filename not in unique_sentences:
                unique_sentences[filename] = text
                
print(f"Found {len(unique_sentences)} unique sentences before deletion")

# Re-insert with proper structure
if unique_sentences:
    docs_to_insert = []
    for filename, text in unique_sentences.items():
        docs_to_insert.append({
            'filename': filename,
            'text': text
        })
    result = db.metadata.insert_many(docs_to_insert)
    print(f"Inserted {len(result.inserted_ids)} documents with proper structure")
else:
    print("No unique sentences found to re-insert")
