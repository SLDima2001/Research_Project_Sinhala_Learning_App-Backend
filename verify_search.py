import sys
import os
import hashlib
from collections import Counter


sys.path.append(os.getcwd())

try:
    from text_to_image import find_real_image
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def verify_diversity(sinhala_word, iterations=10):
    print(f"\nVerifying Diversity for: '{sinhala_word}' ({iterations} iterations)")
    hashes = []
    sources = []
    
    for i in range(iterations):
        try:
            image_bytes, source = find_real_image(sinhala_word, randomize=True)
            if image_bytes and len(image_bytes) > 2000:
                h = hashlib.md5(image_bytes).hexdigest()
                hashes.append(h)
                sources.append(source)
                print(f"  {i+1}: {source} ({h[:8]})")
            else:
                print(f"  {i+1}: FAILED/SMALL ({source})")
        except Exception as e:
            print(f"  {i+1}: ERROR - {e}")

    unique_count = len(set(hashes))
    print(f"\nFinal Result for '{sinhala_word}':")
    print(f"  Total Successes: {len(hashes)}/{iterations}")
    print(f"  Unique Images Found: {unique_count}")
    print(f"  Sources Used: {dict(Counter(sources))}")
    
    if unique_count >= 3:
        print("✅ SUCCESS: Strong diversity achieved.")
    elif unique_count >= 2:
        print("⚠️  WEAK: Limited diversity.")
    else:
        print("❌ FAIL: No variety.")

if __name__ == "__main__":
    
    verify_diversity("ගස", iterations=5)
    print("-" * 40)
    
    verify_diversity("බල්ලා", iterations=5)
