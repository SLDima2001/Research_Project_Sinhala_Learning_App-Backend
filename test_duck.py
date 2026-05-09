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

def test_google_style(sinhala_word, iterations=5):
    print(f"\nTesting Google-style Variety for: '{sinhala_word}' ({iterations} iterations)")
    hashes = []
    sources = []
    
    for i in range(iterations):
        res, src = find_real_image(sinhala_word, randomize=True)
        if res and len(res) > 2000:
            h = hashlib.md5(res).hexdigest()
            hashes.append(h)
            sources.append(src)
            print(f"  {i+1}: {src} ({h[:8]})")
        else:
            print(f"  {i+1}: FAILED")
            
    print(f"\nFinal for '{sinhala_word}':")
    print(f"  Unique: {len(set(hashes))}/{len(hashes)}")
    print(f"  Dist: {dict(Counter(sources))}")

if __name__ == "__main__":
    test_google_style("ගස", 5) 
    print("-" * 40)
    test_google_style("බල්ලා", 5) 
