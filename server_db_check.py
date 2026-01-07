import sqlite3
import os

DB_PATH = "data/questions.db"

def inspect():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("\n--- 🔍 INSPECTING LAST 10 QUESTIONS ---")
    try:
        c.execute("SELECT id, subject, question_text, answer_text FROM questions ORDER BY id DESC LIMIT 10")
        rows = c.fetchall()
        
        if not rows:
            print("⚠️ Database is empty!")
        
        for r in rows:
            q_preview = r[2][:30].replace('\n', ' ') if r[2] else "EMPTY"
            a_preview = r[3][:30].replace('\n', ' ') if r[3] else "EMPTY"
            print(f"ID: {r[0]} | Sub: {r[1]}")
            print(f"   Q: {q_preview}...")
            print(f"   A: '{a_preview}'")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error reading DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect()
