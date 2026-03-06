"""
Sentence Data API Endpoints
Serves sentence data from metadata.csv to frontend
"""
from flask import jsonify
import csv
import os
import random

# Load sentences from metadata.csv
SENTENCES_FILE = os.path.join(os.path.dirname(__file__), 'data', 'metadata.csv')
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'data', 'audio')

def load_sentences():
    """Load sentences from metadata.csv"""
    sentences = []
    
    if not os.path.exists(SENTENCES_FILE):
        logger.error(f"Sentences file not found: {SENTENCES_FILE}")
        return []
    
    try:
        with open(SENTENCES_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='|')
            for row in reader:
                if len(row) >= 2:
                    filename = row[0].strip()
                    text = row[1].strip()
                    
                    # Check if audio file exists
                    audio_path = os.path.join(AUDIO_DIR, f"{filename}.wav")
                    has_audio = os.path.exists(audio_path)
                    
                    sentences.append({
                        'id': filename,
                        'text': text,
                        'words': text.split(),
                        'hasAudio': has_audio,
                        'audioPath': f"/api/audio/{filename}.wav" if has_audio else None
                    })
        
        logger.info(f"Loaded {len(sentences)} sentences from metadata.csv")
        return sentences
    
    except Exception as e:
        logger.error(f"Error loading sentences: {str(e)}")
        return []

# Load sentences on startup
SENTENCES_DATA = load_sentences()

def get_sentences_endpoint():
    """GET /api/sentences - Return all sentences"""
    try:
        # Return first 100 sentences for now (can paginate later)
        return jsonify({
            'sentences': SENTENCES_DATA[:100],
            'total': len(SENTENCES_DATA)
        }), 200
    except Exception as e:
        logger.error(f"Error in get_sentences: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_sentence_by_id(sentence_id):
    """GET /api/sentences/:id - Return specific sentence"""
    try:
        sentence = next((s for s in SENTENCES_DATA if s['id'] == sentence_id), None)
        
        if not sentence:
            return jsonify({'error': 'Sentence not found'}), 404
        
        return jsonify(sentence), 200
    except Exception as e:
        logger.error(f"Error in get_sentence_by_id: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_random_sentences(count=10):
    """GET /api/sentences/random?count=10 - Return random sentences"""
    try:
        available = [s for s in SENTENCES_DATA if s['hasAudio']]
        
        if not available:
            return jsonify({'error': 'No sentences with audio available'}), 404
        
        selected = random.sample(available, min(count, len(available)))
        
        return jsonify({
            'sentences': selected,
            'count': len(selected)
        }), 200
    except Exception as e:
        logger.error(f"Error in get_random_sentences: {str(e)}")
        return jsonify({'error': str(e)}), 500
