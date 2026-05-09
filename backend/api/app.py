import os
import glob
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("backend_debug.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



ffmpeg_patterns = [
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages', 'Gyan.FFmpeg*', '*', 'bin', 'ffmpeg.exe'),
    'ffmpeg'  
]

found_ffmpeg = False
for pattern in ffmpeg_patterns:
    matches = glob.glob(pattern)
    if matches:
        ffmpeg_exe = matches[0]
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_dir
        logger.info(f"Found FFmpeg at: {ffmpeg_exe}")
        found_ffmpeg = True
        break

from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from modules.speech_feedback.processor import get_word_timestamps
from modules.speech_feedback.evaluator import evaluate_pronunciation
from pymongo import MongoClient
from bson.binary import Binary
import base64
from datetime import datetime
import csv
import random
import json
from pydub import AudioSegment
from pydub.utils import which
import io



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'


CORS(app)
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)


MONGO_URI = "mongodb+srv://root:Dima2001@customerfeedback.83hfgpu.mongodb.net/?retryWrites=true&w=majority&appName=customerfeedback"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['customerfeedback']


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
AUDIO_DIR = os.path.join(DATA_DIR, 'audio')
SENTENCES_FILE = os.path.join(DATA_DIR, 'metadata.csv')
TIMINGS_FILE = os.path.join(DATA_DIR, 'word_timings.json')


def load_sentences():
    """Load sentences from MongoDB"""
    sentences = []
    
    try:
        
        metadata_collection = db['metadata']
        timings_collection = db['word_timings']
        
        metadata_docs = list(metadata_collection.find())
        if not metadata_docs:
            logger.warning("No metadata found in MongoDB")
            return []
        
        
        timings_doc = timings_collection.find_one()
        timings = timings_doc if timings_doc else {}
        
        logger.info(f"Loaded {len(metadata_docs)} metadata records from MongoDB")
        logger.info(f"Loaded timings from MongoDB")
        
        for doc in metadata_docs:
            
            filename = doc.get('filename', '')
            text = doc.get('text', '')
            
            if not filename or not text:
                continue
            
            
            word_count = len(text.split())
            if word_count <= 6:
                difficulty = 'easy'
            elif word_count <= 8:
                difficulty = 'medium'
            else:
                difficulty = 'hard'
            
            sentences.append({
                'id': filename,
                'text': text,
                'words': text.split(),
                'difficulty': difficulty,
                'hasAudio': True,
                'audioPath': f"/api/audio/{filename}.wav",
                'timings': timings.get(filename, [])
            })
        
        logger.info(f"Loaded {len(sentences)} unique sentences from MongoDB")
        return sentences
    
    except Exception as e:
        logger.error(f"Error loading sentences from MongoDB: {str(e)}")
        return []



@app.route('/api/sentences/random/<difficulty>', methods=['GET'])
def get_random_sentences_by_difficulty(difficulty):
    """Get random sentences filtered by difficulty"""
    try:
        count = int(request.args.get('count', 40))
        
        
        filtered_sentences = [s for s in SENTENCES_DATA if s.get('difficulty') == difficulty.lower()]
        
        if not filtered_sentences:
            return jsonify({
                'success': True,
                'sentences': [],
                'count': 0
            })
            
        
        num_sentences = min(count, len(filtered_sentences))
        selected_sentences = random.sample(filtered_sentences, num_sentences)
        
        return jsonify({
            'success': True,
            'sentences': selected_sentences,
            'count': len(selected_sentences)
        })
    except Exception as e:
        logger.error(f"Error in get_random_sentences_by_difficulty: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


SENTENCES_DATA = load_sentences()


UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected")

@socketio.on('process_voice')
def handle_voice(data):
    """
    Process voice input from React Native app
    Expected data format:
    {
        'audio': 'base64_encoded_audio_string',
        'target': 'සිංහල වාක්‍යය'
    }
    """
    try:
        logger.info("Received process_voice request")
        
        
        if 'audio' not in data or 'target' not in data:
            logger.error("Missing required fields")
            emit('error', {'message': 'Missing audio or target text'})
            return
        
        audio_base64 = data['audio']
        target_text = data['target']
        
        logger.info(f"Target text: {target_text}")
        logger.info(f"Audio data length: {len(audio_base64)}")
        
        
        try:
            
            if ',' in audio_base64:
                audio_base64 = audio_base64.split(',')[1]
            
            audio_bytes = base64.b64decode(audio_base64)
            logger.info(f"Decoded audio bytes: {len(audio_bytes)}")
        except Exception as e:
            logger.error(f"Base64 decode error: {str(e)}")
            emit('error', {'message': 'Invalid audio data format'})
            return
        
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{UPLOAD_FOLDER}/temp_{timestamp}.wav"
        temp_mongo_filename = f"user_recording_{timestamp}.wav"
        
        try:
            
            
            audio_io = io.BytesIO(audio_bytes)
            
            
            try:
                audio = AudioSegment.from_file(audio_io)
                logger.info(f"Detected audio: {audio.frame_rate}Hz, {audio.channels} channels, {len(audio)}ms")
                
                
                audio = audio.set_frame_rate(16000).set_channels(1)
                
                
                audio.export(temp_filename, format="wav")
                logger.info(f"Converted and saved audio to {temp_filename}")
                
                
                converted_audio = AudioSegment.from_file(temp_filename)
                converted_bytes = converted_audio.export(format="wav").read()
                
            except Exception as e:
                logger.warning(f"Pydub conversion failed: {e}, trying direct save...")
                
                with open(temp_filename, "wb") as f:
                    f.write(audio_bytes)
                logger.info(f"Saved audio directly to {temp_filename}")
                converted_bytes = audio_bytes
                
        except Exception as e:
            logger.error(f"File save error: {str(e)}")
            emit('error', {'message': 'Failed to save audio file'})
            return
        
        
        try:
            audio_collection = db['user_recordings']
            audio_doc = {
                'filename': temp_mongo_filename,
                'audio_data': Binary(converted_bytes),
                'target_text': target_text,
                'timestamp': datetime.now(),
                'file_size': len(converted_bytes),
                'format': 'wav'
            }
            result = audio_collection.insert_one(audio_doc)
            logger.info(f"Stored user recording in MongoDB with ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"Failed to store audio in MongoDB: {str(e)}")
            
        
        
        try:
            logger.info("Running ASR model...")
            raw_timestamps = get_word_timestamps(temp_filename)
            logger.info(f"ASR output: {raw_timestamps}")
        except Exception as e:
            logger.error(f"ASR processing error: {str(e)}", exc_info=True)
            emit('error', {'message': f'ASR processing failed: {str(e)}'})
            return
        
        
        try:
            logger.info("Evaluating pronunciation...")
            final_feedback = evaluate_pronunciation(raw_timestamps, target_text)
            logger.info(f"Evaluation result: {final_feedback}")
            logger.info(f"Word statuses: {[(w['word'], w['status']) for w in final_feedback['words']]}")
        except Exception as e:
            logger.error(f"Evaluation error: {str(e)}", exc_info=True)
            emit('error', {'message': f'Evaluation failed: {str(e)}'})
            return
        
        
        emit('feedback_ui_update', final_feedback)
        logger.info(f"Feedback sent to client - Correct: {final_feedback['score']}/{len(final_feedback['words'])}")
        
        
        try:
            os.remove(temp_filename)
        except:
            pass
        
    except Exception as e:
        logger.error(f"Unexpected error in handle_voice: {str(e)}", exc_info=True)
        emit('error', {'message': f'Server error: {str(e)}'})

@socketio.on('process_partial_audio')
def handle_partial_voice(data):
    """
    Process partial voice input for real-time feedback
    """
    try:
        
        if 'audio' not in data or 'target' not in data:
            return
        
        audio_base64 = data['audio']
        target_text = data['target']
        
        logger.info(f"Processing partial audio: {len(audio_base64)} chars for target: {target_text}")
        
        
        
        try:
            if ',' in audio_base64:
                audio_base64 = audio_base64.split(',')[1]
            audio_bytes = base64.b64decode(audio_base64)
        except Exception:
            return
        
        
        temp_filename = f"{UPLOAD_FOLDER}/stream_temp_{request.sid}.wav"
        
        try:
            audio_io = io.BytesIO(audio_bytes)
            audio = AudioSegment.from_file(audio_io)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(temp_filename, format="wav")
        except Exception as e:
            logger.warning(f"Partial audio conversion failed: {e}")
            
            with open(temp_filename, "wb") as f:
                f.write(audio_bytes)
        
        
        
        raw_timestamps = get_word_timestamps(temp_filename)
        
        
        final_feedback = evaluate_pronunciation(raw_timestamps, target_text)
        
        
        logger.info(f"Partial Result: words={len(final_feedback['words'])}, correct={final_feedback['score']}, statuses={[(w['word'], w['status']) for w in final_feedback['words']]}")
        emit('partial_feedback_update', final_feedback)
        
        
        try:
            os.remove(temp_filename)
        except:
            pass
        
    except Exception as e:
        logger.error(f"Partial processing error: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return {'status': 'healthy', 'service': 'Sinhala Learning App Backend'}, 200

@app.route('/api/sentences', methods=['GET'])
def get_sentences():
    """GET /api/sentences - Return all sentences (paginated)"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return jsonify({
            'sentences': SENTENCES_DATA[start:end],
            'total': len(SENTENCES_DATA),
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Error in get_sentences: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentences/<sentence_id>', methods=['GET'])
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

@app.route('/api/sentences/random', methods=['GET'])
def get_random_sentences():
    """GET /api/sentences/random?count=10 - Return random sentences"""
    try:
        count = int(request.args.get('count', 10))
        available = [s for s in SENTENCES_DATA if s['hasAudio']]
        
        if not available:
            
            available = SENTENCES_DATA
        
        selected = random.sample(available, min(count, len(available)))
        
        return jsonify({
            'sentences': selected,
            'count': len(selected)
        }), 200
    except Exception as e:
        logger.error(f"Error in get_random_sentences: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve audio files from MongoDB"""
    try:
        
        if '..' in filename or filename.startswith('/'):
            return jsonify({'error': 'Invalid filename'}), 400
        
        
        audio_collection = db['audio']
        
        
        possible_filenames = [
            filename,
            f"{filename}.wav" if not filename.endswith('.wav') else filename
        ]
        
        for fname in possible_filenames:
            audio_doc = audio_collection.find_one({'filename': fname})
            if audio_doc:
                logger.info(f"Serving audio from MongoDB: {fname}")
                audio_data = audio_doc['audio_data']
                return send_file(
                    io.BytesIO(audio_data),
                    mimetype='audio/wav',
                    as_attachment=False
                )
        
        logger.warning(f"Audio file not found in MongoDB for: {filename}")
        return jsonify({'error': 'Audio file not found'}), 404
        
    except Exception as e:
        logger.error(f"Error serving audio from MongoDB: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask-SocketIO server...")
    logger.info("Server will be accessible at http://0.0.0.0:5002")
    socketio.run(app, host='0.0.0.0', port=5002, debug=False)
