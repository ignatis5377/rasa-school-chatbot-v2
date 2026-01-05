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
font_url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
download_file(font_url, "fonts", "DejaVuSans.ttf")
