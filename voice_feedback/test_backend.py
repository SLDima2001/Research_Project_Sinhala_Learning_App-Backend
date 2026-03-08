"""
Test script to verify backend functionality
Tests:
1. Sentence loading from metadata.csv
2. Audio file existence
3. ASR model pronunciation evaluation
4. Word timestamp extraction
"""
import os
import csv
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.speech_feedback.processor import get_word_timestamps
from modules.speech_feedback.evaluator import evaluate_pronunciation

def test_sentence_loading():
    """Test loading sentences from metadata.csv"""
    print("=" * 60)
    print("TEST 1: Loading Sentences from metadata.csv")
    print("=" * 60)
    
    sentences_file = os.path.join('data', 'metadata.csv')
    
    if not os.path.exists(sentences_file):
        print(f"❌ FAIL: {sentences_file} not found")
        return False
    
    sentences = []
    with open(sentences_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='|')
        sentences = list(reader)
    
    print(f"✅ PASS: Loaded {len(sentences)} sentences")
    print(f"\nSample sentences:")
    for i, row in enumerate(sentences[:3]):
        if len(row) >= 2:
            print(f"  {i+1}. ID: {row[0]}, Text: {row[1][:50]}...")
    
    return True

def test_audio_files():
    """Test audio file existence"""
    print("\n" + "=" * 60)
    print("TEST 2: Verifying Audio Files")
    print("=" * 60)
    
    audio_dir = os.path.join('data', 'audio')
    
    if not os.path.exists(audio_dir):
        print(f"❌ FAIL: {audio_dir} directory not found")
        return False
    
    wav_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
    print(f"✅ PASS: Found {len(wav_files)} WAV files")
    print(f"\nSample files:")
    for i, filename in enumerate(wav_files[:5]):
        filepath = os.path.join(audio_dir, filename)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  {i+1}. {filename} ({size_kb:.1f} KB)")
    
    return True

def test_asr_model():
    """Test ASR model with a sample audio file"""
    print("\n" + "=" * 60)
    print("TEST 3: Testing ASR Model (Word Timestamps)")
    print("=" * 60)
    
    audio_dir = os.path.join('data', 'audio')
    wav_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
    
    if not wav_files:
        print("❌ FAIL: No WAV files found")
        return False
    
    # Test with first audio file
    test_file = os.path.join(audio_dir, wav_files[0])
    print(f"\nTesting with: {wav_files[0]}")
    
    try:
        word_data = get_word_timestamps(test_file)
        print(f"✅ PASS: ASR model working!")
        print(f"\nExtracted {len(word_data)} words with timestamps:")
        for i, word_info in enumerate(word_data[:5]):
            print(f"  {i+1}. '{word_info['word']}' ({word_info['start']:.2f}s - {word_info['end']:.2f}s)")
        
        if len(word_data) > 5:
            print(f"  ... and {len(word_data) - 5} more words")
        
        return word_data
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return None

def test_pronunciation_evaluation(word_data):
    """Test pronunciation evaluation logic"""
    print("\n" + "=" * 60)
    print("TEST 4: Testing Pronunciation Evaluation")
    print("=" * 60)
    
    if not word_data:
        print("❌ SKIP: No word data from ASR test")
        return False
    
    # Create target sentence from extracted words
    target_sentence = " ".join([w['word'] for w in word_data])
    print(f"\nTarget sentence: {target_sentence[:100]}...")
    
    try:
        # Test with same words (should be all green)
        result = evaluate_pronunciation(word_data, target_sentence)
        print(f"\n✅ PASS: Evaluation working!")
        print(f"\nResults:")
        print(f"  All correct: {result['all_correct']}")
        print(f"  Score: {result['score']}/{len(result['words'])}")
        print(f"\nWord-level feedback:")
        for i, word_feedback in enumerate(result['words'][:5]):
            status_emoji = "🟢" if word_feedback['status'] == 'green' else "🔴" if word_feedback['status'] == 'red' else "⚪"
            print(f"  {i+1}. {status_emoji} '{word_feedback['word']}' - {word_feedback['status']}")
        
        if len(result['words']) > 5:
            print(f"  ... and {len(result['words']) - 5} more words")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BACKEND FUNCTIONALITY TEST SUITE")
    print("=" * 60)
    
    # Run tests
    test1 = test_sentence_loading()
    test2 = test_audio_files()
    word_data = test_asr_model()
    test4 = test_pronunciation_evaluation(word_data)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"1. Sentence Loading: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"2. Audio Files: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"3. ASR Model: {'✅ PASS' if word_data else '❌ FAIL'}")
    print(f"4. Pronunciation Evaluation: {'✅ PASS' if test4 else '❌ FAIL'}")
    
    all_passed = test1 and test2 and word_data and test4
    print(f"\n{'🎉 ALL TESTS PASSED!' if all_passed else '⚠️ SOME TESTS FAILED'}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
