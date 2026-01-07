import sqlite3
import os

# Adjust path for when running inside actions folder (DB is at ../data/questions.db relative to actions? 
# No, in container PWD is /app, so DB is at data/questions.db. 
# But this script will run from /app/actions/server_db_check.py or similar.
# Let's use absolute path /app/data/questions.db which is standard in our docker-compose.
DB_PATH = "/app/data/questions.db" 

def inspect():
    print(f"🔍 Checking DB at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        # Try relative just in case
        if os.path.exists("data/questions.db"):
             print("⚠️ Found at relative path 'data/questions.db' instead.")
             DB_PATH = "data/questions.db"
        else:
             return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("\n--- 🔍 INSPECTING LAST 10 QUESTIONS ---")
    try:
        # Check permissions
        try:
             c.execute("UPDATE questions SET id=id WHERE 1=0")
             print("✅ DB is Writable")
        except Exception as e:
             print(f"❌ DB is READY-ONLY: {e}")

        c.execute("SELECT id, subject, question_text, answer_text FROM questions ORDER BY id DESC LIMIT 10")
        rows = c.fetchall()
        
        if not rows:
            print("⚠️ Database is empty!")
        
        for r in rows:
            q_text = r[2] if r[2] else "EMPTY"
            a_text = r[3] if r[3] else "EMPTY (NULL or '')"
            
            # Print first 50 chars
            print(f"ID: {r[0]} | Sub: {r[1]}")
            print(f"   Q: {q_text[:50].replace(chr(10), ' ')}...")
            print(f"   A: '{a_text[:50].replace(chr(10), ' ')}...'")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error reading DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect()
