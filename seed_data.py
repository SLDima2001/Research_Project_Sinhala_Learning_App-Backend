"""
Seed Script: Push new sentences and audio files to MongoDB Atlas
Database: customerfeedback
Collections: metadata (sentences), audio (audio files), word_timings (timing data)

Usage:
  1. Add your sentences to the SENTENCES list below
  2. Place matching .wav audio files in the 'seed_audio/' folder
  3. Run: python seed_data.py
"""

import os
from pymongo import MongoClient
from bson.binary import Binary
from dotenv import load_dotenv

load_dotenv()




MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://root:Dima2001@customerfeedback.83hfgpu.mongodb.net/?retryWrites=true&w=majority&appName=customerfeedback')
DB_NAME = 'customerfeedback'
AUDIO_FOLDER = os.path.join(os.path.dirname(__file__), 'seed_audio')





SENTENCES = [
    
    {"filename": "voice_1.wav", "text": "අද පාසලේ අපට නව ගුරුවරයෙක් හමුවුණා"},
    {"filename": "voice_2.wav", "text": "මම සවසට මගේ මිතුරන් සමඟ ක්‍රීඩා කිරීමට කැමතියි"},
    {"filename": "voice_3.wav", "text": "අපේ ගෙදර ඉදිරිපස ලස්සන මල් වත්තක් තිබේ"},
    {"filename": "voice_4.wav", "text": "අම්මා අද උදේ රසවත් කිරි බත් සකස් කළා"},
  
    {"filename": "voice_6.wav", "text": "අපි ඉරිදා දවසේ පවුල සමඟ උද්‍යානයට ගියා"},
    {"filename": "voice_7.wav", "text": "ගස්වල සිටින කුරුල්ලෝ මිහිරි ලෙස ගී ගායනා කළහ"},
    {"filename": "voice_8.wav", "text": "මම මගේ ගෙදර වැඩ හැමදාම වෙලාවට කරමි"},
    {"filename": "voice_9.wav", "text": "ගුරුතුමිය අපට සත්‍යය කතා කිරීම වැදගත් බව කියා දුන්නා"},
    {"filename": "voice_11.wav", "text": "මගේ හොඳම මිතුරා පාසලේදී මට උදව් කරයි"},
    {"filename": "voice_12.wav", "text": "අපි පරිසරය පිරිසිදුව තබා ගැනීමට උත්සාහ කළ යුතුය"},
    {"filename": "voice_13.wav", "text": "කුඩා බල්ලා ගෙදර වටේ දිවමින් සතුටින් ක්‍රීඩා කළා"},
    {"filename": "voice_14.wav", "text": "උදේ කාලයේ හිරු එළිය ඉතා සුන්දරයි"},  
    {"filename": "voice_15.wav", "text": "මම ගුරුතුමියට ගෞරවයෙන් කතා කරමි"},
    {"filename": "voice_16.wav", "text": "සීයා අපට පරණ කතා රැසක් කියා දෙනවා"},
    {"filename": "voice_17.wav", "text": "අපි මිතුරන් සමඟ එකට ඉගෙන ගන්නා විට පහසු වේ"},
   
    {"filename": "voice_19.wav", "text": "මම පොත් කියවීමෙන් අලුත් දේවල් බොහෝමයක් ඉගෙන ගන්නවා"},
    {"filename": "voice_20.wav", "text": "අපේ නගරයේ විශාල පුස්තකාලයක් තිබේ"},
    {"filename": "voice_21.wav", "text": "කුඩා දරුවන්ට සත්‍යය කතා කිරීම ඉතා වැදගත්ය"},
    {"filename": "voice_22.wav", "text": "ගුරුතුමිය අපට අලුත් ගීයක් ඉගැන්වුවා"},
      

    
]




def connect():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client[DB_NAME]
    
    client.server_info()
    print(f"✓ Connected to MongoDB Atlas ({DB_NAME})")
    return db

def clear_old_data(db):
    """Optional: clear existing data before seeding"""
    answer = input("\n⚠️  Do you want to DELETE all existing sentences & audio first? (yes/no): ").strip().lower()
    if answer == 'yes':
        r1 = db['metadata'].delete_many({})
        r2 = db['audio'].delete_many({})
        r3 = db['word_timings'].delete_many({})
        print(f"  Deleted {r1.deleted_count} metadata, {r2.deleted_count} audio, {r3.deleted_count} timings docs")
    else:
        print("  Keeping existing data (new entries will be added alongside)")

def seed_sentences(db):
    """Insert sentences into the metadata collection"""
    metadata_col = db['metadata']
    inserted = 0
    skipped = 0

    for s in SENTENCES:
        
        existing = metadata_col.find_one({'filename': s['filename']})
        if existing:
            print(f"  ⏭  Skipped (already exists): {s['filename']}")
            skipped += 1
            continue

        metadata_col.insert_one({
            'filename': s['filename'],
            'text': s['text']
        })
        inserted += 1

    print(f"\n✓ Sentences: {inserted} inserted, {skipped} skipped")

def seed_audio(db):
    """Insert audio files (.wav) from seed_audio/ folder into the audio collection"""
    audio_col = db['audio']

    if not os.path.exists(AUDIO_FOLDER):
        os.makedirs(AUDIO_FOLDER)
        print(f"\n📁 Created '{AUDIO_FOLDER}/' folder.")
        print(f"   Place your .wav files there (named to match 'filename' in SENTENCES, e.g. sent_001.wav)")
        return

    wav_files = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith('.wav')]
    if not wav_files:
        print(f"\n⚠️  No .wav files found in '{AUDIO_FOLDER}/'. Skipping audio upload.")
        print(f"   Place .wav files named like: sent_001.wav, sent_002.wav, etc.")
        return

    inserted = 0
    skipped = 0

    for wav_file in wav_files:
        fname = os.path.splitext(wav_file)[0]  

        
        existing = audio_col.find_one({'filename': wav_file})
        if existing:
            print(f"  ⏭  Skipped audio (already exists): {wav_file}")
            skipped += 1
            continue

        filepath = os.path.join(AUDIO_FOLDER, wav_file)
        with open(filepath, 'rb') as f:
            audio_bytes = f.read()

        audio_col.insert_one({
            'filename': wav_file,
            'audio_data': Binary(audio_bytes)
        })
        size_mb = len(audio_bytes) / (1024 * 1024)
        print(f"  ✓ Uploaded: {wav_file} ({size_mb:.2f} MB)")
        inserted += 1

    print(f"\n✓ Audio: {inserted} uploaded, {skipped} skipped")

def show_current_data(db):
    """Show what's currently in the database"""
    metadata_count = db['metadata'].count_documents({})
    audio_count = db['audio'].count_documents({})
    print(f"\n📊 Current DB status:")
    print(f"   Sentences (metadata): {metadata_count}")
    print(f"   Audio files:          {audio_count}")

    if metadata_count > 0:
        print(f"\n   Sample sentences:")
        for doc in db['metadata'].find().limit(5):
            print(f"     [{doc['filename']}] {doc['text']}")
        if metadata_count > 5:
            print(f"     ... and {metadata_count - 5} more")

if __name__ == '__main__':
    print("=" * 50)
    print("  Sinhala Learning App - Data Seed Script")
    print("=" * 50)

    db = connect()
    show_current_data(db)
    clear_old_data(db)
    seed_sentences(db)
    seed_audio(db)
    show_current_data(db)

    print("\n✅ Done! Restart the backend (python app.py) to load the new data.")
