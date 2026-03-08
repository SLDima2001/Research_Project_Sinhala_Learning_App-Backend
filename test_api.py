"""
API Testing Script for Sinhala Handwriting Recognition
Tests all endpoints and functionality
File: test_api.py
"""

import requests
import base64
import numpy as np
from PIL import Image
import io
import json

# Configuration
API_URL = "http://localhost:5000/api"
TEST_USER_ID = "test_user_123"


def create_test_image():
    """Create a simple test image with handwriting-like content"""
    # Create white background
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    
    # Draw some random lines to simulate handwriting
    import cv2
    cv2.line(img, (50, 50), (150, 100), (0, 0, 0), 3)
    cv2.line(img, (150, 100), (100, 150), (0, 0, 0), 3)
    cv2.circle(img, (100, 100), 30, (0, 0, 0), 2)
    
    # Convert to PIL Image
    return Image.fromarray(img)


def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/png;base64,{base64_string}"


def test_health_check():
    """Test health check endpoint"""
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/health")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        
        print("[OK] Test Passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test Failed: {e}")
        return False


def test_get_all_letters():
    """Test get all letters endpoint"""
    print("\n" + "=" * 60)
    print("TEST 2: Get All Letters")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/get-all-letters")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Total Letters: {data.get('total', 0)}")
        
        # Show first 5 letters
        if data.get('success') and data.get('letters'):
            print("\nFirst 5 letters:")
            for letter in data['letters'][:5]:
                print(f"  {letter['id']}: {letter['character']} ({letter['romanized']})")
        
        assert response.status_code == 200
        assert data['success'] == True
        assert data['total'] == 59
        
        print("\n[OK] Test Passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test Failed: {e}")
        return False


def test_get_random_letter():
    """Test get random letter endpoint"""
    print("\n" + "=" * 60)
    print("TEST 3: Get Random Letter")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{API_URL}/get-letter",
            params={'user_id': TEST_USER_ID}
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        assert response.status_code == 200
        assert data['success'] == True
        assert 'session_id' in data
        assert 'letter' in data
        
        print("\n[OK] Test Passed!")
        return data  # Return for use in next test
        
    except Exception as e:
        print(f"[ERROR] Test Failed: {e}")
        return None


def test_submit_handwriting(session_data):
    """Test submit handwriting endpoint"""
    print("\n" + "=" * 60)
    print("TEST 4: Submit Handwriting")
    print("=" * 60)
    
    if not session_data:
        print("[ERROR] Skipping test - no session data")
        return False
    
    try:
        # Create test image
        test_image = create_test_image()
        image_base64 = image_to_base64(test_image)
        
        # Submit handwriting
        response = requests.post(
            f"{API_URL}/submit-handwriting",
            json={
                'session_id': session_data['session_id'],
                'image': image_base64
            }
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"\nResults:")
        print(f"  Score: {data.get('score', 0)}/100")
        print(f"  Is Correct: {data.get('is_correct', False)}")
        print(f"  Confidence: {data.get('confidence', 0):.2%}")
        print(f"  Predicted: {data.get('predicted_letter', '?')} ({data.get('predicted_romanized', '?')})")
        print(f"  Correct: {data.get('correct_letter', '?')}")
        print(f"  Model Mode: {data.get('model_mode', 'unknown')}")
        print(f"\n  Feedback: {data.get('feedback', '')}")
        
        if 'top_3_predictions' in data:
            print(f"\n  Top 3 Predictions:")
            for i, pred in enumerate(data['top_3_predictions'], 1):
                print(f"    {i}. {pred['letter']} ({pred['romanized']}): {pred['confidence']:.2%}")
        
        assert response.status_code == 200
        assert data['success'] == True
        
        print("\n[OK] Test Passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test Failed: {e}")
        return False


def test_direct_predict():
    """Test direct predict endpoint"""
    print("\n" + "=" * 60)
    print("TEST 5: Direct Prediction")
    print("=" * 60)
    
    try:
        # Create test image
        test_image = create_test_image()
        image_base64 = image_to_base64(test_image)
        
        # Get prediction
        response = requests.post(
            f"{API_URL}/predict",
            json={'image': image_base64}
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"\nPrediction Results:")
        print(f"  Predicted: {data.get('predicted_letter', '?')} ({data.get('predicted_romanized', '?')})")
        print(f"  Confidence: {data.get('confidence', 0):.2%}")
        print(f"  Model Mode: {data.get('model_mode', 'unknown')}")
        
        if 'top_3' in data:
            print(f"\n  Top 3 Predictions:")
            for i, pred in enumerate(data['top_3'], 1):
                print(f"    {i}. {pred['letter']} ({pred['romanized']}): {pred['confidence']:.2%}")
        
        assert response.status_code == 200
        assert data['success'] == True
        
        print("\n[OK] Test Passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test Failed: {e}")
        return False


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 60)
    print("TEST 6: Error Handling")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Invalid session
    print("\n6.1: Testing invalid session...")
    try:
        response = requests.post(
            f"{API_URL}/submit-handwriting",
            json={
                'session_id': 'invalid_session_123',
                'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=='
            }
        )
        assert response.status_code == 400
        print("  [OK] Invalid session handled correctly")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
    
    # Test 2: Missing image
    print("\n6.2: Testing missing image...")
    try:
        response = requests.post(
            f"{API_URL}/submit-handwriting",
            json={'session_id': 'test_123'}
        )
        assert response.status_code == 400
        print("  [OK] Missing image handled correctly")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
    
    # Test 3: Invalid endpoint
    print("\n6.3: Testing invalid endpoint...")
    try:
        response = requests.get(f"{API_URL}/invalid-endpoint")
        assert response.status_code == 404
        print("  [OK] Invalid endpoint handled correctly")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
    
    print(f"\n[OK] Error Handling: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests


def run_all_tests():
    """Run all API tests"""
    print("\n" + "=" * 60)
    print("SINHALA HANDWRITING API - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"\nAPI URL: {API_URL}")
    print(f"Test User: {TEST_USER_ID}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Get All Letters", test_get_all_letters()))
    
    session_data = test_get_random_letter()
    results.append(("Get Random Letter", session_data is not None))
    
    results.append(("Submit Handwriting", test_submit_handwriting(session_data)))
    results.append(("Direct Prediction", test_direct_predict()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK] PASS" if result else "[ERROR] FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("=" * 60)
    
    return passed == total


def test_connection():
    """Quick connection test"""
    print("\n" + "=" * 60)
    print("QUICK CONNECTION TEST")
    print("=" * 60)
    
    try:
        print(f"\nTrying to connect to {API_URL}...")
        response = requests.get(f"{API_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("\n[OK] Connection successful!")
            print(f"  API Status: {data.get('status', 'unknown')}")
            print(f"  Model Status: {data.get('model_status', 'unknown')}")
            return True
        else:
            print(f"\n[ERROR] Connection failed (Status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Connection failed - API not reachable")
        print("\nMake sure:")
        print("  1. Flask API is running (python app.py)")
        print("  2. API is running on http://localhost:5000")
        print("  3. No firewall is blocking the connection")
        return False
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    # Check if running quick test or full test
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        test_connection()
    else:
        # First check connection
        if test_connection():
            print("\nStarting full test suite in 3 seconds...\n")
            import time
            time.sleep(3)
            
            # Run all tests
            success = run_all_tests()
            sys.exit(0 if success else 1)
        else:
            print("\n⚠️  Cannot proceed with tests - API not reachable")
            sys.exit(1)
