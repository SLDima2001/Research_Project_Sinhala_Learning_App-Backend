import sys
import os
import requests


sys.path.append(os.getcwd())

try:
    from text_to_image import PIXABAY_API_KEY
except ImportError:
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def check_counts(search_term):
    print(f"Checking results for: '{search_term}'")
    
    
    if PIXABAY_API_KEY:
        url = "https://pixabay.com/api/"
        params = {"key": PIXABAY_API_KEY, "q": search_term, "per_page": 80}
        try:
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json()
            hits = data.get("hits", [])
            print(f"  Pixabay Hits: {len(hits)}")
        except Exception as e:
            print(f"  Pixabay Error: {e}")
    else:
        print("  Pixabay: No API Key")

    
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query", "generator": "search", "gsrnamespace": "6",
        "gsrsearch": f'"{search_term}" filetype:bitmap', "gsrlimit": 100, "format": "json"
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        print(f"  Wikimedia Hits: {len(pages)}")
    except Exception as e:
        print(f"  Wikimedia Error: {e}")

if __name__ == "__main__":
    check_counts("dog")
    check_counts("tree")
    check_counts("butterfly")
