import os
import torch
import soundfile as sf
import numpy as np
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import logging

logger = logging.getLogger(__name__)

# Alternative: Start from api/ directory
import os
from pathlib import Path

# Get the api/ directory (3 levels up from processor.py)
API_DIR = Path(__file__).parent.parent.parent
MODEL_PATH = os.path.join(API_DIR, "models", "sinhala_asr")
# Alternative: Use absolute path based on current file location
# MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "sinhala_asr"))

if not os.path.exists(MODEL_PATH):
    print(f"ERROR: Model folder not found at {MODEL_PATH}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(__file__)}")
    raise FileNotFoundError(f"Model folder not found at {MODEL_PATH}")

logger.info(f"Loading model from {MODEL_PATH}")
processor = Wav2Vec2Processor.from_pretrained(MODEL_PATH, local_files_only=True)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_PATH, local_files_only=True)
model.eval()  # Set to evaluation mode

def get_word_timestamps(audio_path):
    """
    Extract words with timestamps from audio file
    Returns: List of dicts with 'word', 'start', 'end'
    """
    try:
        # Load audio using soundfile 
        # We expect 16kHz input from app.py
        speech, sr = sf.read(audio_path, dtype='float32')
        
        if sr != 16000:
            logger.warning(f"Audio sample rate is {sr}, expected 16000. Check app.py conversion.")
        
        # Ensure it's 1D array
        if len(speech.shape) > 1:
             speech = speech.squeeze()
        
        if len(speech) == 0:
            logger.error("Empty audio file")
            return []
        
        # Prepare input
        input_values = processor(
            speech, 
            return_tensors="pt", 
            sampling_rate=16000
        ).input_values
        
        # Get model predictions
        with torch.no_grad():
            logits = model(input_values).logits
        
        # Get predicted token IDs
        predicted_ids = torch.argmax(logits, dim=-1)
        
        # Decode to text (this gives us the full transcription)
        transcription = processor.batch_decode(predicted_ids)[0]
        
        logger.info(f"Transcription: {transcription}")
        
        # Get frame-level predictions for timestamp calculation
        # Each logit frame represents ~20ms of audio
        frame_duration = 0.02  # 20ms per frame
        
        # Convert logits to probabilities
        probs = torch.nn.functional.softmax(logits, dim=-1)
        predicted_ids_squeezed = predicted_ids.squeeze()
        
        # Extract word boundaries with proper CTC decoding
        words_data = []
        current_word = ""
        word_start = None
        last_char_index = None
        prev_token_id = None
        blank_id = processor.tokenizer.pad_token_id
        
        for i, token_id in enumerate(predicted_ids_squeezed):
            token_id = token_id.item()
            
            if token_id == blank_id:
                prev_token_id = token_id
                continue
            
            # Decode token
            char = processor.tokenizer.decode([token_id])
            
            # Handle word delimiter
            # Check using token ID directly (more robust)
            is_delimiter = (token_id == processor.tokenizer.word_delimiter_token_id)
            
            # Fallback string check if ID check fails or isn't set
            if not is_delimiter:
                is_delimiter = (char == "|") or (char == " ")
            
            if is_delimiter:
                if current_word:
                    # End at the last character, not the delimiter
                    # Use last_char_index + 1 to include the last frame
                    # STRICT MODE: 20ms buffer
                    w_start = (word_start * frame_duration) - 0.02
                    w_start = max(0.0, w_start)
                    
                    # End padding
                    end_idx = last_char_index if last_char_index is not None else i
                    w_end = ((end_idx + 1) * frame_duration) + 0.02

                    words_data.append({
                        "word": current_word.strip(),
                        "start": round(w_start, 3),
                        "end": round(w_end, 3)
                    })
                    current_word = ""
                    word_start = None
                    last_char_index = None
            else:
                # Handle repeated characters (CTC collapse)
                # Only collapse if current token == prev token (and prev wasn't blank - simplified here)
                # Actually standard CTC is: collapse identical consecutive tokens.
                # Blanks separate identicals. Since we handle blank above by continuing,
                # we need to know if we just saw a blank.
                
                if token_id == prev_token_id:
                    # Repeated token, ignore
                    pass
                else:
                    if word_start is None:
                        word_start = i * frame_duration
                    current_word += char
                    last_char_index = i
            
            prev_token_id = token_id
        # Add last word if exists
        if current_word:
            # Calculate strict boundaries with 1-frame buffer (20ms)
            # Start: Lead in by 20ms to catch the attack
            w_start = (word_start * frame_duration) - 0.02
            w_start = max(0.0, w_start)
            
            # End: Hold for 20ms after last character to catch decay
            end_idx = last_char_index if last_char_index is not None else len(predicted_ids_squeezed)
            w_end = ((end_idx + 1) * frame_duration) + 0.02
            
            words_data.append({
                "word": current_word.strip(),
                "start": round(w_start, 3),
                "end": round(w_end, 3)
            })
        
        logger.info(f"Extracted {len(words_data)} strict words: {words_data}")
        return words_data
        
    except Exception as e:
        logger.error(f"Error in get_word_timestamps: {str(e)}", exc_info=True)
        return []
