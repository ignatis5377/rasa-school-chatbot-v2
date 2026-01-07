import sqlite3
import os

DB_PATH = "/app/data/questions.db"

def reset_db():
    print(f"🧹 CLeaning DB at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        if os.path.exists("data/questions.db"):
             DB_PATH = "data/questions.db"
        else:
             print("❌ DB Not found")
             return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute("SELECT COUNT(*) FROM questions")
        count = c.fetchone()[0]
        print(f"📉 Found {count} existing questions.")
        
        c.execute("DELETE FROM questions")
        conn.commit()
        print(f"✅ DELETED all {count} questions. Database is now clean and ready for fresh upload.")
        
    except Exception as e:
        print(f"❌ Error clearing DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_db()
