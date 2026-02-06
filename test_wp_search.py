
import requests
import json

base_url = "https://ignatislask.sites.sch.gr"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def test_search(query):
    print(f"\n--- Testing Search for: '{query}' ---")
    url = f"{base_url}/?rest_route=/wp/v2/posts&search={query}"
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            posts = response.json()
            print(f"Found {len(posts)} posts:")
            for post in posts:
                print(f"- {post['title']['rendered']} (ID: {post['id']})")
                # print(f"  Link: {post['link']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def test_categories():
    print("\n--- Listing Categories ---")
    url = f"{base_url}/?rest_route=/wp/v2/categories&per_page=50"
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            cats = response.json()
            for cat in cats:
                print(f"ID: {cat['id']} | Name: {cat['name']} | Count: {cat['count']}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    import sys
    # Reconfigure stdout for utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Test the problematic queries
    test_search("απουσίες")
    test_search("απουσιες") # Try without accents too
    test_search("ενισχυτική")
    test_search("ενισχυτική διδασκαλία")
    
    # List categories
    test_categories()
