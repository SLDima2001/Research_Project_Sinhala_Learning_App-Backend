import os
import json
import logging
from pathlib import Path
from modules.speech_feedback.processor import get_word_timestamps
import time


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_existing_timings(filepath):
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load existing timings: {e}")
    return {}

def generate_timestamps():
    
    BASE_DIR = Path(__file__).parent
    AUDIO_DIR = BASE_DIR / "data" / "audio"
    OUTPUT_FILE = BASE_DIR / "data" / "word_timings.json"

    if not AUDIO_DIR.exists():
        logger.error(f"Audio directory not found: {AUDIO_DIR}")
        return

    logger.info(f"Scanning audio files in {AUDIO_DIR}...")
    audio_files = list(AUDIO_DIR.glob("*.wav"))
    
    if not audio_files:
        logger.warning("No .wav files found in audio directory.")
        return

    
    timings_data = load_existing_timings(OUTPUT_FILE)
    logger.info(f"Loaded {len(timings_data)} existing timing records.")
    
    files_to_process = [f for f in audio_files if f.stem not in timings_data]
    logger.info(f"Found {len(audio_files)} total files. {len(files_to_process)} remaining to process.")
    
    save_interval = 5
    processed_count = 0
    
    for i, audio_path in enumerate(files_to_process):
        try:
            filename = audio_path.stem 
            logger.info(f"[{i+1}/{len(files_to_process)}] Processing {filename}...")
            
            
            timestamps = get_word_timestamps(str(audio_path))
            
            if timestamps:
                timings_data[filename] = timestamps
            else:
                logger.warning(f"No words detected in {filename}")
                timings_data[filename] = [] 

            processed_count += 1

            
            if processed_count % save_interval == 0:
                logger.info(f"Saving progress ({len(timings_data)} records)...")
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(timings_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to process {audio_path.name}: {e}")

    
    logger.info(f"Saving final timestamps to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(timings_data, f, indent=2, ensure_ascii=False)
        
    logger.info("Done! Metadata generation complete.")

if __name__ == "__main__":
    generate_timestamps()
