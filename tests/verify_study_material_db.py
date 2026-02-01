import sqlite3
import os

DB_PATH = "test_study_material.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS study_materials
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subject TEXT,
                  grade TEXT,
                  filename TEXT,
                  title TEXT,
                  url TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def test_upload(subject, grade):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Logic from ActionUploadStudyMaterial
    subj_clean = subject.capitalize()
    grade_short = grade # simplification
    
    c.execute("SELECT COUNT(*) FROM study_materials WHERE subject = ? AND grade = ?", (subj_clean, grade_short))
    count = c.fetchone()[0]
    next_num = count + 1
    
    generated_title = f"{subj_clean}_{grade_short}_{next_num}"
    url = f"http://test/{generated_title}"
    
    c.execute("INSERT INTO study_materials (subject, grade, filename, title, url) VALUES (?, ?, ?, ?, ?)",
              (subj_clean, grade_short, "test.pdf", generated_title, url))
    conn.commit()
    conn.close()
    print(f"Uploaded: {generated_title}")

def test_provide(subject, grade):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    subj_clean = subject.capitalize()
    
    c.execute("SELECT title, url FROM study_materials WHERE subject LIKE ? AND grade = ?", (f"%{subj_clean}%", grade))
    rows = c.fetchall()
    conn.close()
    
    print(f"Results for {subject} {grade}:")
    for r in rows:
        print(r)

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    init_db()
    
    print("--- Test 1: Upload Math A (1st time) ---")
    test_upload("mathematics", "A")
    
    print("--- Test 2: Upload Math A (2nd time) ---")
    test_upload("mathematics", "A")
    
    print("--- Test 3: Upload Physics B ---")
    test_upload("physics", "B")
    
    print("--- Test 4: Provide Math A ---")
    test_provide("math", "A") # Should match LIKE %Math%
    
    print("--- Test 5: Provide Physics B ---")
    test_provide("physics", "B")

    # Clean up
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
