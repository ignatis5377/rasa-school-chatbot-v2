import sqlite3
import os
import sys

# Force UTF-8 for Windows Console
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = "data/questions.db"

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at {DB_PATH}")
else:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    print("--- RAW DATA IN QUESTIONS TABLE ---")
    c.execute("SELECT id, subject, class_name, difficulty, source_file FROM questions")
    rows = c.fetchall()
    
    if not rows:
        print("❌ Table is EMPTY!")
    else:
        for row in rows:
            print(f"ID: {row['id']} | Subj: '{row['subject']}' | Class: '{row['class_name']}' | Diff: '{row['difficulty']}' | File: '{row['source_file']}'")
            
    conn.close()
