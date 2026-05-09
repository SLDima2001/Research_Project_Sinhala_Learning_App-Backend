"""
Simple API Test Script (No ML Dependencies Required)
Tests REST API endpoints without requiring torch/transformers
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"✅ PASS: {response.json()}")
            return True
        else:
            print(f"❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        print("Make sure the backend is running: python app.py")
        return False

def test_get_sentences():
    """Test GET /api/sentences"""
    print("\n" + "=" * 60)
    print("TEST 2: GET /api/sentences")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/sentences?page=1&per_page=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS: Retrieved {len(data['sentences'])} sentences")
            print(f"Total in database: {data['total']}")
            print(f"\nSample sentences:")
            for i, sentence in enumerate(data['sentences'][:3]):
                print(f"  {i+1}. ID: {sentence['id']}")
                print(f"     Text: {sentence['text'][:60]}...")
                print(f"     Has Audio: {sentence['hasAudio']}")
            return True
        else:
            print(f"❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_get_random_sentences():
    """Test GET /api/sentences/random"""
    print("\n" + "=" * 60)
    print("TEST 3: GET /api/sentences/random")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/sentences/random?count=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS: Retrieved {data['count']} random sentences")
            print(f"\nRandom sentences:")
            for i, sentence in enumerate(data['sentences']):
                print(f"  {i+1}. ID: {sentence['id']}")
                print(f"     Text: {sentence['text'][:60]}...")
            return True
        else:
            print(f"❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_get_sentence_by_id():
    """Test GET /api/sentences/:id"""
    print("\n" + "=" * 60)
    print("TEST 4: GET /api/sentences/:id")
    print("=" * 60)
    try:
        
        response = requests.get(f"{BASE_URL}/api/sentences?page=1&per_page=1")
        if response.status_code != 200:
            print("❌ FAIL: Could not get sentence ID")
            return False
        
        sentence_id = response.json()['sentences'][0]['id']
        
        
        response = requests.get(f"{BASE_URL}/api/sentences/{sentence_id}")
        if response.status_code == 200:
            sentence = response.json()
            print(f"✅ PASS: Retrieved sentence by ID")
            print(f"\nSentence details:")
            print(f"  ID: {sentence['id']}")
            print(f"  Text: {sentence['text']}")
            print(f"  Words: {len(sentence['words'])}")
            print(f"  Has Audio: {sentence['hasAudio']}")
            return True
        else:
            print(f"❌ FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("\n" + "=" * 60)
    print("BACKEND API TEST SUITE")
    print("=" * 60)
    print("\n⚠️  Make sure backend is running: python app.py\n")
    
    
    test1 = test_health()
    test2 = test_get_sentences()
    test3 = test_get_random_sentences()
    test4 = test_get_sentence_by_id()
    
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"1. Health Check: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"2. GET /api/sentences: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"3. GET /api/sentences/random: {'✅ PASS' if test3 else '❌ FAIL'}")
    print(f"4. GET /api/sentences/:id: {'✅ PASS' if test4 else '❌ FAIL'}")
    
    all_passed = test1 and test2 and test3 and test4
    print(f"\n{'🎉 ALL TESTS PASSED!' if all_passed else '⚠️ SOME TESTS FAILED'}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
