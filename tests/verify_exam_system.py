import os
import sqlite3
import shutil
from reportlab.pdfgen import canvas
from pypdf import PdfReader

# Import functions from actions (we need to adjust path or copy for standalone test)
# Since actions.py is in ../actions/, we can temporarily add it to path
import sys
sys.path.append(os.path.join(os.getcwd(), 'actions'))

# We will copy the functions here to avoid import issues with Rasa SDK if not installed/configured in this env
# (Rasa SDK might be there, but simpler to verify logic directly if we can import)
try:
    from actions import extract_questions_from_pdf, init_db, DB_PATH
except ImportError:
    # If import fails (e.g. rasa_sdk desc missing), we define mocks or copy specific logic
    # For now, let's try to import. If it fails, I will rewrite this script to contain the logic.
    print("Could not import actions. Will attempt to proceed or fail.")

TEST_PDF = "test_material.pdf"
TEST_DB = "data/questions.db" # using the real one or test one? safely use test one if possible, but actions.py hardcodes it.
# Let's use the real DB path from actions.py but maybe backup?
# Actually, actions.py uses "data/questions.db".

def create_dummy_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Question: What is 2+2?")
    c.drawString(100, 730, "Answer: 4")
    c.drawString(100, 700, "Q: What is the capital of France?")
    c.drawString(100, 680, "A: Paris")
    c.save()
    print(f"Created {filename}")

def test_flow():
    # 1. Create Dummy PDF
    create_dummy_pdf(TEST_PDF)
    
    # 2. Parse
    print("Testing Parser...")
    questions = extract_questions_from_pdf(TEST_PDF)
    print(f"Found {len(questions)} questions.")
    for q in questions:
        print(f"  Q: {q['question']} | A: {q['answer']}")
    
    if len(questions) < 2:
        print("FAIL: Parser didn't find 2 questions.")
        return

    # 3. Simulate DB Insert (using the logic from ActionUpload)
    print("Testing DB Insert...")
    # init_db() # Should be called on import
    
    conn = sqlite3.connect(TEST_DB)
    c = conn.cursor()
    # Clean up previous test runs for these questions
    c.execute("DELETE FROM questions WHERE source_file=?", (TEST_PDF,))
    
    for q in questions:
        c.execute("INSERT INTO questions (subject, class_name, difficulty, question_text, answer_text, source_file) VALUES (?, ?, ?, ?, ?, ?)",
                  ("Math", "B_GYMNASIOU", "Easy", q['question'], q['answer'], TEST_PDF))
    conn.commit()
    
    # Verify Count
    c.execute("SELECT count(*) FROM questions WHERE source_file=?", (TEST_PDF,))
    count = c.fetchone()[0]
    print(f"DB now has {count} questions from {TEST_PDF}")
    conn.close()
    
    if count != len(questions):
        print("FAIL: DB Insertion count mismatch.")
        return

    # 4. Simulate Generation
    print("Testing Generation...")
    # Logic from ActionCreateExam
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE subject='Math' AND difficulty='Easy'")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("FAIL: No questions found for generation.")
        return
        
    print(f"Retrieved {len(rows)} questions for Generation.")
    
    # 5. Cleanup
    os.remove(TEST_PDF)
    print("Test Complete. Success!")

if __name__ == "__main__":
    test_flow()
