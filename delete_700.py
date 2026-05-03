from pymongo import MongoClient

c = MongoClient(
    'mongodb+srv://root:Dima2001@customerfeedback.83hfgpu.mongodb.net/?retryWrites=true&w=majority&appName=customerfeedback',
    serverSelectionTimeoutMS=10000
)
db = c['customerfeedback']

print("Before:", db['metadata'].count_documents({}), "sentences,", db['audio'].count_documents({}), "audio files")

# Get the first 700 metadata docs
docs = list(db['metadata'].find().limit(700))
filenames = [d['filename'] for d in docs]
ids = [d['_id'] for d in docs]

# Delete 700 from metadata
r1 = db['metadata'].delete_many({'_id': {'$in': ids}})

# Delete matching audio files (try both with and without .wav extension)
audio_names = []
for f in filenames:
    audio_names.append(f)
    if not f.endswith('.wav'):
        audio_names.append(f + '.wav')

r2 = db['audio'].delete_many({'filename': {'$in': audio_names}})

print(f"Deleted: {r1.deleted_count} sentences, {r2.deleted_count} audio files")
print("After:", db['metadata'].count_documents({}), "sentences,", db['audio'].count_documents({}), "audio files")
