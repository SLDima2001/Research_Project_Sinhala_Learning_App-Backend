import sys
import os
import hashlib

# Add current dir to sys.path
sys.path.append(os.getcwd())

try:
    from text_to_image import find_real_image
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def quick_check():
    print("Quick Check: Randomization Variety")
    
    # 1. First call
    img1, src1 = find_real_image("dog", randomize=True)
    h1 = hashlib.md5(img1).hexdigest() if img1 else "NONE"
    
    # 2. Second call
    img2, src2 = find_real_image("dog", randomize=True)
    h2 = hashlib.md5(img2).hexdigest() if img2 else "NONE"
    
    print(f"Call 1: {src1} ({h1[:8]})")
    print(f"Call 2: {src2} ({h2[:8]})")
    
    if h1 != h2 and h1 != "NONE":
        print("✅ SUCCESS: Different images returned.")
    else:
        print("❌ FAIL: Same image or no image.")

if __name__ == "__main__":
    quick_check()
