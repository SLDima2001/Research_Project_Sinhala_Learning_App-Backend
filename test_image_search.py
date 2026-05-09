"""Quick test of the image search functions"""
import requests
import json
import sys


print("=== Test 1: Wikipedia API for 'tree' ===")
try:
    r = requests.get(
        'https://en.wikipedia.org/w/api.php',
        params={
            'action': 'query',
            'titles': 'tree',
            'prop': 'pageimages',
            'piprop': 'thumbnail',
            'pithumbsize': '512',
            'format': 'json',
        },
        timeout=10,
        headers={'User-Agent': 'SinhalaLearningApp/1.0'}
    )
    data = r.json()
    pages = data.get('query', {}).get('pages', {})
    for pid, pdata in pages.items():
        if pid == "-1":
            print("  Page not found")
            continue
        thumb = pdata.get('thumbnail', {})
        url = thumb.get('source', '')
        if url:
            print(f"  Found image URL: {url[:80]}...")
            img_r = requests.get(url, timeout=10, headers={'User-Agent': 'SinhalaLearningApp/1.0'})
            print(f"  Image downloaded: {img_r.status_code}, {len(img_r.content)} bytes")
        else:
            print("  No thumbnail found")
except Exception as e:
    print(f"  FAILED: {e}")


print("\n=== Test 2: Wikimedia Commons API for 'dog' ===")
try:
    r = requests.get(
        'https://commons.wikimedia.org/w/api.php',
        params={
            'action': 'query',
            'generator': 'search',
            'gsrnamespace': '6',
            'gsrsearch': 'dog filetype:bitmap',
            'gsrlimit': '3',
            'prop': 'imageinfo',
            'iiprop': 'url|mime|size',
            'iiurlwidth': '512',
            'format': 'json',
        },
        timeout=10,
        headers={'User-Agent': 'SinhalaLearningApp/1.0'}
    )
    data = r.json()
    pages = data.get('query', {}).get('pages', {})
    found = False
    for pid, pdata in sorted(pages.items(), key=lambda x: x[1].get('index', 999)):
        imageinfo = pdata.get('imageinfo', [{}])[0]
        thumb_url = imageinfo.get('thumburl', '')
        mime = imageinfo.get('mime', '')
        print(f"  Page: {pdata.get('title', '?')}, mime: {mime}")
        if thumb_url and mime in ('image/jpeg', 'image/png', 'image/webp'):
            print(f"  Downloading: {thumb_url[:80]}...")
            img_r = requests.get(thumb_url, timeout=10, headers={'User-Agent': 'SinhalaLearningApp/1.0'})
            print(f"  Image downloaded: {img_r.status_code}, {len(img_r.content)} bytes")
            found = True
            break
    if not found:
        print("  No suitable image found")
except Exception as e:
    print(f"  FAILED: {e}")


print("\n=== Test 3: Translation test ===")
try:
    from deep_translator import GoogleTranslator
    result = GoogleTranslator(source='sinhala', target='english').translate('ගස')
    print(f"  'ගස' -> '{result}'")
except Exception as e:
    print(f"  Translation failed: {e}")

print("\n=== All tests complete ===")
