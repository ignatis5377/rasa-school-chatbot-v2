import os
import requests

def download_file(url, dest_folder, filename):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    filepath = os.path.join(dest_folder, filename)
    
    print(f"Downloading {filename}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Success! Saved to {filepath}")
    except Exception as e:
        print(f"Error downloading: {e}")

# URL for DejaVuSans (Reliable for Greek)
# Updated URL to raw.githubusercontent.com for reliability
FONT_URL = "https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/master/ttf/DejaVuSans.ttf"
OUTPUT_DIR = "fonts"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "DejaVuSans.ttf")
download_file(FONT_URL, OUTPUT_DIR, os.path.basename(OUTPUT_FILE))
