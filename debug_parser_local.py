import re
import os
from docx import Document

# Mocking the regex patterns from actions.py
q_start_pattern = re.compile(r'(?:^)(?:Q:|Ερώτηση|ΕΡΩΤΗΣΗ|Question|Πρόβλημα|Θέμα)\s*\d*[.:]?\s*(.*)', re.IGNORECASE)
a_start_pattern = re.compile(r'(?:^)(?:A:|Απάντηση|ΑΠΑΝΤΗΣΗ|Answer|Λύση|ΛΥΣΗ)\s*\d*[.:]?\s*(.*)', re.IGNORECASE)

def parse_docx(file_path):
    print(f"Opening: {file_path}")
    if not os.path.exists(file_path):
        print("File not found!")
        return

    doc = Document(file_path)
    
    questions = []
    current_q = None
    
    print("\n--- RAW ITERATION VS REGEX ---")
    
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text: continue
        
        print(f"[{i}] '{text}'")
        
        q_match = q_start_pattern.match(text)
        a_match = a_start_pattern.match(text)
        
        if q_match:
            print(f"   MATCH QUESTION -> New Q")
            if current_q: questions.append(current_q)
            current_q = {"question": q_match.group(1), "answer": ""}
            
        elif a_match:
            print(f"   MATCH ANSWER -> Switch to A mode")
            if current_q:
                # Capture text after "ANSWER" label (e.g. "ANSWER: B")
                captured = a_match.group(1).strip()
                current_q["answer"] = captured
        
        else:
            print(f"   CONTINUATION")
            if current_q:
                if current_q["answer"] == "" and not a_match: 
                    # We are in Question body (and haven't seen Answer label yet)
                    if current_q["answer"]:
                        current_q["answer"] += "\n" + text
                    else:
                         current_q["question"] += "\n" + text
                         
    if current_q: questions.append(current_q)
    
    print("\n\n--- FINAL RESULTS ---")
    for idx, q in enumerate(questions, 1):
        print(f"Q{idx}: {q['question'][:50]}...")
        print(f"    ANS: '{q['answer']}'")
        if not q['answer']:
            print("    EMPTY ANSWER (Bug confirmed)")

# Run on the file
parse_docx("files/Math_A_Easy_1.docx")
