import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

def calculate_similarity(word1, word2):
    """Calculate similarity ratio between two words (0.0 to 1.0)"""
    return SequenceMatcher(None, word1.lower(), word2.lower()).ratio()

def evaluate_pronunciation(spoken_words, target_sentence):
    """
    Compare spoken words against target sentence
    
    Args:
        spoken_words: List of dicts with 'word', 'start', 'end'
        target_sentence: Expected Sinhala sentence string
    
    Returns:
        Dict with feedback for each target word
        {
            "words": [...],  # List of word feedback
            "all_correct": bool,
            "score": int  # Number of correct words
        }
    """
    target_words = target_sentence.strip().split()
    feedback_report = []
    
    logger.info(f"Target words: {target_words}")
    logger.info(f"Spoken words: {[w['word'] for w in spoken_words]}")
    
    # Track which spoken words we've used
    used_spoken_indices = set()
    
    # Thresholds for matching
    MATCH_THRESHOLD = 0.4
    CORRECT_THRESHOLD = 0.7
    
    # First pass: Identify matches
    matches = {}  # target_index -> match info
    last_matched_target_index = -1
    
    for i, target_word in enumerate(target_words):
        target_word_clean = target_word.strip().lower()
        best_match = None
        best_similarity = 0.0
        best_index = -1
        
        # Find the best matching spoken word that hasn't been used
        for j, spoken_data in enumerate(spoken_words):
            if j in used_spoken_indices:
                continue
                
            spoken_word = spoken_data["word"].strip().lower()
            similarity = calculate_similarity(target_word_clean, spoken_word)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = spoken_data
                best_index = j
        
        # Check if we found a valid match
        if best_match and best_similarity >= MATCH_THRESHOLD:
            # Determine status: green (correct) or red (incorrect)
            status = "green" if best_similarity >= CORRECT_THRESHOLD else "red"
            matches[i] = {
                "status": status,
                "match": best_match,
                "sim": best_similarity,
                "target": target_word
            }
            used_spoken_indices.add(best_index)
            last_matched_target_index = i
    
    # Second pass: Build feedback report with proper status assignment
    for i, target_word in enumerate(target_words):
        if i in matches:
            # Matched word - correct or incorrect
            m = matches[i]
            feedback_report.append({
                "word": m["target"],
                "status": m["status"],
                "start": m["match"]["start"],
                "end": m["match"]["end"],
                "similarity": round(m["sim"], 2),
                "spoken": m["match"]["word"]
            })
            logger.info(f"Word '{target_word}' - Status: {m['status']}")
            
        elif i < last_matched_target_index:
            # Unmatched word BEFORE the last matched position -> Skipped (gray)
            feedback_report.append({
                "word": target_word,
                "status": "gray",
                "start": None,
                "end": None,
                "similarity": 0.0
            })
            logger.info(f"Word '{target_word}' - SKIPPED (gray)")
            
        else:
            # Unmatched word AT or AFTER the last matched position
            # This is a future word that hasn't been spoken yet (or wasn't recognized yet)
            # It should be "pending", not "gray" (skipped)
            feedback_report.append({
                "word": target_word,
                "status": "pending",
                "start": None,
                "end": None,
                "similarity": 0.0
            })
            # Match logic simplified: All future unmatched words are Pending.
            # Even if nothing has been matched yet, we wait (Pending).
            pass
    
    # Calculate results
    all_green = all(item["status"] == "green" for item in feedback_report)
    correct_count = sum(1 for item in feedback_report if item["status"] == "green")
    
    return {
        "words": feedback_report,
        "all_correct": all_green,
        "score": correct_count
    }