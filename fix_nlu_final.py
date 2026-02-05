
import os

file_path = "data/nlu.yml"

try:
    # Read with fallback encoding or ignore errors
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    print(f"Read {len(content)} characters.")

    # Write back with strict utf-8
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Successfully rewrote data/nlu.yml with UTF-8 encoding.")

except Exception as e:
    print(f"Error: {e}")
