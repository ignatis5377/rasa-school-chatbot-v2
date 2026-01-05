import os
import sqlite3
import sys

# sys.path.append(os.path.join(os.getcwd(), 'actions')) # Not needed if running from root
from actions.actions import extract_questions_from_pdf, init_db, DB_PATH

def test_manual_upload(filename, subject, grade, difficulty):
    idx_path = os.path.join("files_to_upload", filename)
    if not os.path.exists(idx_path):
        print(f"Error: File '{filename}' not found in 'files_to_upload' folder.")
        return

    print(f"--- Processing {filename} ---")
    questions = extract_questions_from_pdf(idx_path)
    
    if not questions:
        print("FAIL: No questions found. Check regex or file format.")
        return

    print(f"SUCCESS: Found {len(questions)} questions.")
    for i, q in enumerate(questions, 1):
        grade_info = q.get('detected_grade', 'No Grade Detected')
        # Safe print for Windows consoles
        try:
             print(f"  #{i} [{grade_info}] Q: {q['question'][:50]}... | A: {q['answer'][:50]}...")
        except UnicodeEncodeError:
             print(f"  #{i} [{grade_info}] (Content has special chars)")

    # Save to DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Optional: Clear previous entries for this file to avoid duplicates during testing
    c.execute("DELETE FROM questions WHERE source_file=?", (filename,))
    
    for q in questions:
        final_grade = q.get("detected_grade", grade)
        c.execute("INSERT INTO questions (subject, class_name, difficulty, question_text, answer_text, source_file) VALUES (?, ?, ?, ?, ?, ?)",
                  (subject, final_grade, difficulty, q['question'], q['answer'], filename))
    conn.commit()
    conn.close()
    print(f"Saved to DB with tags: {subject}, {grade}, {difficulty}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python test_parsing.py <filename> <subject> <grade> <difficulty>")
        print("Example: python test_parsing.py math_example.pdf Math B_Gymnasiou Medium")
    else:
        test_manual_upload(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
