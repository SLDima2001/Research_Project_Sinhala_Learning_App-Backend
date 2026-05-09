"""
Unified MongoDB Migration Script
Consolidates: migrate_data_to_mongo.py, migrate_audio_to_mongo.py, and re_migrate_mongo.py
Handles migration of all data: metadata, word timings, and audio files
"""
import os
import csv
import json
import logging
import argparse
from pymongo import MongoClient
from bson.binary import Binary


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


MONGO_URI = "mongodb+srv://root:Dima2001@customerfeedback.83hfgpu.mongodb.net/?retryWrites=true&w=majority&appName=customerfeedback"
client = MongoClient(MONGO_URI)
db = client['customerfeedback']


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
AUDIO_DIR = os.path.join(DATA_DIR, 'audio')
METADATA_CSV = os.path.join(DATA_DIR, 'metadata.csv')
METADATA_BACKUP_CSV = os.path.join(os.path.dirname(__file__), 'metadata_backup.csv')
TIMINGS_JSON = os.path.join(DATA_DIR, 'word_timings.json')

def migrate_metadata(clear_existing=False):
    """Migrate metadata from CSV to MongoDB"""
    logger.info("=" * 60)
    logger.info("MIGRATING METADATA")
    logger.info("=" * 60)
    
    
    metadata_file = None
    if os.path.exists(METADATA_CSV):
        metadata_file = METADATA_CSV
    elif os.path.exists(METADATA_BACKUP_CSV):
        metadata_file = METADATA_BACKUP_CSV
        logger.info(f"Using backup metadata: {METADATA_BACKUP_CSV}")
    else:
        logger.warning(f"⚠ Metadata file not found in {METADATA_CSV} or {METADATA_BACKUP_CSV}")
        return 0
    
    if clear_existing:
        result = db.metadata.delete_many({})
        logger.info(f"Cleared {result.deleted_count} existing metadata documents")
    
    docs_to_insert = []
    
    with open(metadata_file, 'r', encoding='utf-8') as csvfile:
        
        first_line = csvfile.readline()
        csvfile.seek(0)
        
        if '|' in first_line:
            
            logger.info("Detected pipe-delimited format")
            reader = csv.reader(csvfile, delimiter='|')
            for row in reader:
                if len(row) >= 2:
                    filename = row[0].strip()
                    text = row[1].strip()
                    if filename and text:
                        docs_to_insert.append({
                            'filename': filename,
                            'text': text
                        })
        else:
            
            logger.info("Detected CSV with headers format")
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row and row.get('filename') and row.get('text'):
                    docs_to_insert.append({
                        'filename': row['filename'].strip(),
                        'text': row['text'].strip()
                    })
    
    if docs_to_insert:
        result = db.metadata.insert_many(docs_to_insert)
        logger.info(f"[OK] Migrated {len(result.inserted_ids)} metadata documents")
        return len(result.inserted_ids)
    else:
        logger.warning("⚠ No valid metadata records found")
        return 0

def migrate_timings():
    """Migrate word timings from JSON to MongoDB"""
    logger.info("=" * 60)
    logger.info("MIGRATING WORD TIMINGS")
    logger.info("=" * 60)
    
    if not os.path.exists(TIMINGS_JSON):
        logger.warning(f"⚠ Timings file not found: {TIMINGS_JSON}")
        return
    
    
    db.word_timings.delete_many({})
    logger.info("Cleared existing word timings")
    
    with open(TIMINGS_JSON, 'r', encoding='utf-8') as jsonfile:
        word_timings = json.load(jsonfile)
    
    if isinstance(word_timings, list):
        if word_timings:
            result = db.word_timings.insert_many(word_timings)
            logger.info(f"[OK] Migrated {len(result.inserted_ids)} word timing documents")
        else:
            logger.warning("⚠ Timings JSON is empty")
    else:
        result = db.word_timings.insert_one(word_timings)
        logger.info(f"[OK] Migrated word timings as single document")

def migrate_audio(clear_existing=True):
    """Migrate audio files as binary data to MongoDB"""
    logger.info("=" * 60)
    logger.info("MIGRATING AUDIO FILES")
    logger.info("=" * 60)
    
    if not os.path.exists(AUDIO_DIR):
        logger.warning(f"⚠ Audio directory not found: {AUDIO_DIR}")
        return 0
    
    audio_files = sorted([
        f for f in os.listdir(AUDIO_DIR) 
        if f.endswith('.wav') and os.path.isfile(os.path.join(AUDIO_DIR, f))
    ])
    
    if not audio_files:
        logger.warning("⚠ No audio files found")
        return 0
    
    logger.info(f"Found {len(audio_files)} audio files")
    
    if clear_existing:
        result = db.audio.delete_many({})
        logger.info(f"Cleared {result.deleted_count} existing audio documents")
    
    success_count = 0
    failed_files = []
    
    for idx, filename in enumerate(audio_files, 1):
        try:
            filepath = os.path.join(AUDIO_DIR, filename)
            file_size = os.path.getsize(filepath)
            
            
            with open(filepath, 'rb') as f:
                audio_data = f.read()
            
            
            audio_doc = {
                'filename': filename,
                'audio_data': Binary(audio_data),
                'file_size': file_size,
                'format': 'wav'
            }
            
            db.audio.insert_one(audio_doc)
            success_count += 1
            
            
            if idx % 100 == 0 or idx == len(audio_files):
                logger.info(f"  Progress: {idx}/{len(audio_files)} files migrated...")
                
        except Exception as e:
            logger.error(f"Failed to migrate {filename}: {str(e)}")
            failed_files.append(filename)
    
    logger.info(f"[OK] Successfully migrated {success_count}/{len(audio_files)} audio files")
    
    if failed_files:
        logger.warning(f"⚠ Failed to migrate {len(failed_files)} files:")
        for f in failed_files[:10]:
            logger.warning(f"  - {f}")
    
    return success_count

def verify_migration():
    """Verify migration was successful"""
    logger.info("=" * 60)
    logger.info("VERIFYING MIGRATION")
    logger.info("=" * 60)
    
    metadata_count = db.metadata.count_documents({})
    timings_count = db.word_timings.count_documents({})
    audio_count = db.audio.count_documents({})
    
    logger.info(f"MongoDB Collections Status:")
    logger.info(f"  • metadata: {metadata_count} documents")
    logger.info(f"  • word_timings: {timings_count} documents")
    logger.info(f"  • audio: {audio_count} documents")
    
    if metadata_count > 0 and audio_count > 0:
        logger.info("[OK] Migration verification successful!")
        return True
    else:
        logger.warning("⚠ Migration may be incomplete")
        return False

def main():
    """Run migrations based on arguments"""
    parser = argparse.ArgumentParser(
        description='MongoDB Data Migration Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python migrate_to_mongodb.py --all          # Migrate everything
  python migrate_to_mongodb.py --metadata     # Migrate only metadata
  python migrate_to_mongodb.py --audio        # Migrate only audio
  python migrate_to_mongodb.py --timings      # Migrate only timings
  python migrate_to_mongodb.py --verify       # Check current state
        '''
    )
    
    parser.add_argument('--all', action='store_true', help='Migrate metadata, timings, and audio')
    parser.add_argument('--metadata', action='store_true', help='Migrate metadata only')
    parser.add_argument('--audio', action='store_true', help='Migrate audio files only')
    parser.add_argument('--timings', action='store_true', help='Migrate word timings only')
    parser.add_argument('--verify', action='store_true', help='Verify current migration status')
    
    args = parser.parse_args()
    
    
    if not any(vars(args).values()):
        args.all = True
    
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " MONGODB MIGRATION TOOL ".center(58) + "║")
    logger.info("╚" + "=" * 58 + "╝\n")
    
    try:
        if args.all or args.metadata:
            migrate_metadata(clear_existing=True)
        
        if args.all or args.timings:
            migrate_timings()
        
        if args.all or args.audio:
            migrate_audio(clear_existing=True)
        
        if args.all or args.verify:
            verify_migration()
        
        logger.info("\n" + "=" * 60)
        logger.info("[OK] OPERATION COMPLETE!")
        logger.info("=" * 60 + "\n")
        return True
        
    except Exception as e:
        logger.error(f"\n[ERROR] Operation failed: {str(e)}", exc_info=True)
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
