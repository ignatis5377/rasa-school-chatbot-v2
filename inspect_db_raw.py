import sqlite3
import unicodedata

# Connect to the database
conn = sqlite3.connect('data/questions.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Fetch a few random questions to inspect
c.execute("SELECT id, question_text, answer_text, image_path FROM questions ORDER BY RANDOM() LIMIT 5")
rows = c.fetchall()

print("\n" + "="*60)
print("🔍 INTERNAL DB INSPECTION (RAW DATA)")
print("="*60)

for row in rows:
    q_text = row['question_text']
    a_text = row['answer_text']
    img = row['image_path']
    
    print(f"\n🆔 ID: {row['id']}")
    print(f"🖼️ Image Path: {repr(img)}")
    print(f"📝 Answer Column: {repr(a_text)}")
    print("-" * 20)
    print("📜 QUESTION TEXT (REPR - SHOWS HIDDEN CHARS):")
    print(repr(q_text))
    print("-" * 20)
    
    # Analyze the last few characters specifically
    if q_text:
        tail = q_text[-20:] if len(q_text) > 20 else q_text
        print(f"🧐 TAIL HEX ANALYSIS (Last 20 chars): '{repr(tail)}'")
        for char in tail:
            print(f"   - '{char}': U+{ord(char):04X} ({unicodedata.name(char, 'UNKNOWN')})")

conn.close()
print("\n" + "="*60)
