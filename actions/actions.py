# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List, Optional
import json
import random
import os
import sqlite3
import re
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

print("\n\n**************************************************")
print("LOADING ACTIONS.PY - VERSION CHECK: 12345")
print("**************************************************\n\n")

# PDF Libraries
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
# Word Library
from docx import Document
import uuid
from PIL import Image
import uuid
from PIL import Image

DB_PATH = "data/questions.db"
GENERATED_EXAMS_DIR = "files/generated_exams"

def init_db():
    """Initializes the questions database if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subject TEXT,
                  class_name TEXT,
                  difficulty TEXT,
                  question_text TEXT,
                  answer_text TEXT,
                  source_file TEXT,
                  image_path TEXT)''')
    
    # Migration for existing DB: Attempt to add the column if it's missing
    try:
        c.execute("ALTER TABLE questions ADD COLUMN image_path TEXT")
    except sqlite3.OperationalError:
        # Column likely already exists
        pass
        
    conn.commit()
    conn.close()
    
    # Ensure directories exist
    os.makedirs(GENERATED_EXAMS_DIR, exist_ok=True)
    os.makedirs("files/images", exist_ok=True) # Directory for uploaded images

# Call init_db immediately when actions load
init_db()

# Register Greek Font (DejaVu)
try:
    # Try Docker Path first, then Local Relative Path
    font_paths_to_try = ["/app/fonts/DejaVuSans.ttf", "fonts/DejaVuSans.ttf"]
    font_path = None
    
    for p in font_paths_to_try:
        if os.path.exists(p):
            font_path = p
            break
            
    if font_path:
        pdfmetrics.registerFont(TTFont('GreekFont', font_path))
        print(f"DEBUG: Loaded GreekFont from {font_path}")
        
        # Determine Bold Path based on found Regular Path
        base_dir = os.path.dirname(font_path)
        bold_path = os.path.join(base_dir, "DejaVuSans-Bold.ttf")
        
        if os.path.exists(bold_path):
             pdfmetrics.registerFont(TTFont('GreekFont-Bold', bold_path))
             print(f"DEBUG: Loaded GreekFont-Bold from {bold_path}")
        else:
             print("DEBUG: Bold font not found, falling back to regular for Bold.")
             pdfmetrics.registerFont(TTFont('GreekFont-Bold', font_path))
    else:
        # Fallback for Windows Local Dev ONLY
        print("DEBUG: DejaVuSans not found in standard paths.")
        if os.path.exists("C:/Windows/Fonts/arial.ttf"):
             print("DEBUG: Loading Arial from Windows.")
             pdfmetrics.registerFont(TTFont('GreekFont', "C:/Windows/Fonts/arial.ttf"))
             pdfmetrics.registerFont(TTFont('GreekFont-Bold', "C:/Windows/Fonts/arial.ttf"))
        else:
             print("ERROR: No suitable font found!")
except Exception as e:
    print(f"DEBUG: Failed to load font: {e}")

def check_user_access(tracker: Tracker) -> bool:
    """
    Checks if the user is authenticated via Metadata sent from the Frontend.
    Returns True if allowed, False otherwise.
    """
    # 1. Check latest message first (Fastest)
    metadata = tracker.latest_message.get("metadata", {})
    user_data = metadata.get("customData", {}) or metadata
    
    print(f"DEBUG AUTH (Latest): Role={user_data.get('role')}, User={user_data.get('username')}")
    
    # Check Metadata directly
    if user_data.get("role") == "member" or user_data.get("username"):
        return True

    # Check Slots (Backup)
    slot_role = tracker.get_slot("role")
    if slot_role == "member":
         print(f"DEBUG AUTH: Found role in SLOT: {slot_role}")
         return True

    # 2. Deep Scan: Check session history (Crucial for Webchat)
    # Webchat often sends metadata only ONCE at the start.
    print("DEBUG AUTH: Scanning history for metadata...")
    for i, event in enumerate(reversed(tracker.events)):
        # DEBUG: Print every event to see what's going on
        evt_type = event.get("event")
        evt_meta = event.get("metadata")
        if evt_meta:
             print(f"DEBUG EVENT [{i}] {evt_type}: HAS METADATA: {evt_meta}")
        
        # Check 'user' events and 'session_started' events
        evt_metadata = event.get("metadata", {})
        if not evt_metadata: continue
        
        evt_user_data = evt_metadata.get("customData", {}) or evt_metadata
        role = evt_user_data.get("role")
        username = evt_user_data.get("username")
        
        if role == "member" or username:
            print(f"DEBUG AUTH: Found auth in history! Role={role}")
            return True
            
    print("DEBUG AUTH: No auth found in history.")
    return False

def extract_questions_from_pdf(file_path: Text) -> List[Dict]:
    """
    Parses a PDF file and extracts questions/answers with Grade detection.
    
    Structure:
    - Looks for "Β’ ΓΥΜΝΑΣΙΟΥ", "Γ’ ΓΥΜΝΑΣΙΟΥ", etc. to set current context.
    - Looks for "Πρόβλημα X" / "Λύση" pairs.
    """
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # Normalize
    text = text.replace('\r', '\n')
    
    # Regex definitions
    # Grade Headers: "Β’ ΓΥΜΝΑΣΙΟΥ" or "Β ΓΥΜΝΑΣΙΟΥ"
    grade_pattern = re.compile(r'(?:^|\n)([ΑΒΓ])\’?\s*ΓΥΜΝΑΣΙΟΥ', re.IGNORECASE)
    
    # Question/Answer Markers (as previously defined)
    # We will iterate line by line or largely to handle state (Grade -> Question)
    # But regex split is powerful. Let's try to split by Grade Headers first?
    # No, splitting by grade headers might be safer to isolate sections.
    
    # Strategy:
    # 1. Split text into "Grade Blocks"
    # 2. For each block, extract Questions
    
    # Find all grade starts
    grade_matches = list(grade_pattern.finditer(text))
    
    if not grade_matches:
        # No grade headers found, treat whole text as one block (grade=None)
        return parse_questions_from_text(text, None)
    
    all_questions = []
    
    # Iterate through matches
    for i, match in enumerate(grade_matches):
        grade_letter = match.group(1) # Α, Β, or Γ
        start_idx = match.end()
        
        # End index is the start of the next match, or end of text
        if i + 1 < len(grade_matches):
             end_idx = grade_matches[i+1].start()
        else:
             end_idx = len(text)
             
        grade_text = text[start_idx:end_idx]
        
        # Map letter to full Class Name (as used in DB/Slots)
        # Assuming DB uses "Β Γυμνασίου" etc.
        class_map = {
            "Α": "Α Γυμνασίου",
            "Β": "Β Γυμνασίου",
            "Γ": "Γ Γυμνασίου"
        }
        grade_name = class_map.get(grade_letter.upper(), f"{grade_letter} Γυμνασίου")
        
        # print(f"DEBUG: Found Grade Section: {grade_name}")
        
        # Parse questions in this block
        questions = parse_questions_from_text(grade_text, grade_name)
        all_questions.extend(questions)
        
    return all_questions

def parse_questions_from_text(text: str, grade: Optional[str]) -> List[Dict]:
    """Helper to parse Q/A from a text block."""
    items = []
    
    question_pattern = r'(?:^|\n)(?:Q:|Ερώτηση:|Question:|Πρόβλημα\s*\d*[.:]?|Θέμα\s*[A-D1-40-9]*[.:]?|Problem\s*\d*[.:]?)\s*'
    answer_pattern = r'(?:^|\n)(?:A:|Απάντηση:|Answer:|Λύση:|Λύση)\s*'
    
    segments = re.split(question_pattern, text, flags=re.IGNORECASE)
    
    for segment in segments[1:]: 
        parts = re.split(answer_pattern, segment, flags=re.IGNORECASE)
        
        if len(parts) >= 2:
            q_text = parts[0].strip()
            a_text = parts[1].strip()
            
            if q_text and a_text:
                item = {"question": q_text, "answer": a_text}
                if grade:
                    item["detected_grade"] = grade
                items.append(item)
    return items

def extract_questions_from_docx(file_path: Text) -> Dict[Text, Any]:
    """
    Parses a .docx file for Metadata and Q&A.
    Returns: {
        "metadata": {"subject": ..., "grade": ..., "difficulty": ...},
        "questions": [{"question": ..., "answer": ..., "image_path": ...}]
    }
    """
    doc = Document(file_path)
    questions = []
    metadata = {}
    
    current_q = None
    
    # Metadata Regex
    meta_patterns = {
        "subject": re.compile(r'(?:Μάθημα|Subject):\s*(.*)', re.IGNORECASE),
        "grade": re.compile(r'(?:Τάξη|Grade|Class):\s*(.*)', re.IGNORECASE),
        "difficulty": re.compile(r'(?:Δυσκολία|Difficulty|Diff):\s*(.*)', re.IGNORECASE)
    }
    
    # Q&A Regex - Explicitly including uppercase unaccented forms to be safe
    # Matches "ΕΡΩΤΗΣΗ 1", "Ερώτηση:", "Question 5", "Q:"
    q_start_pattern = re.compile(r'(?:^)(?:Q:|Ερώτηση|ΕΡΩΤΗΣΗ|Question|Πρόβλημα|Θέμα)\s*\d*[.:]?\s*(.*)', re.IGNORECASE)
    # Matches "ΑΠΑΝΤΗΣΗ", "Απάντηση:", "Answer", "A:", "ΛΥΣΗ"
    # Added explicit check for single "ΑΠΑΝΤΗΣΗ" line which might be followed by answer on next line
    a_start_pattern = re.compile(r'(?:^)(?:A:|Απάντηση|ΑΠΑΝΤΗΣΗ|Answer|Λύση|ΛΥΣΗ)\s*\d*[.:]?\s*(.*)', re.IGNORECASE)

    with open("debug_log.txt", "a", encoding="utf-8") as f:
         f.write(f"--- Parsing Doc: {os.path.basename(file_path)} ---\n")

    for para in doc.paragraphs:
        text = para.text.strip()
        # Debug Log Paragraph start (limited length)
        # with open("debug_log.txt", "a", encoding="utf-8") as f:
        #    f.write(f"Para: {text[:50]}...\n")

        # 1. Image Extraction (Same as before)
        image_path = None
        if 'graphicData' in para._p.xml:
            for rId in para.part.rels.keys():
                if rId in para._p.xml:
                    rel = para.part.rels[rId]
                    if "image" in rel.target_ref:
                        image_blob = rel.target_part.blob
                        ext = rel.target_ref.split('.')[-1]
                        filename = f"{uuid.uuid4()}.{ext}"
                        save_path = f"files/images/{filename}"
                        with open(save_path, "wb") as f:
                            f.write(image_blob)
                        image_path = save_path
                        break

        # 2. Metadata Parsing (Only if we haven't found questions yet)
        if not questions and not current_q:
            for key, pattern in meta_patterns.items():
                match = pattern.match(text)
                if match:
                    metadata[key] = match.group(1).strip()
                    # Continue to next paragraph to avoid treating metadata as content
                    continue

        # 3. Content Parsing
        q_match = q_start_pattern.match(text)
        a_match = a_start_pattern.match(text)

        if q_match:
            # Debug
            with open("debug_log.txt", "a", encoding="utf-8") as f:
               f.write(f"MATCH Q: {q_match.group(0)}\n")

            # Save previous
            if current_q:
                questions.append(current_q)
            
            # Init new
            current_q = {
                "question": q_match.group(1), 
                "answer": None,  # Changed from "" to None to track state
                "image_path": image_path 
            }
        
        elif a_match:
            with open("debug_log.txt", "a", encoding="utf-8") as f:
               f.write(f"MATCH A: {a_match.group(0)}\n")

            if current_q:
                # Initialize answer (even if empty string) to signal we are in Answer mode
                current_q["answer"] = a_match.group(1).strip()
        
        else:
            # Continuation
            if current_q:
                content_to_add = text
                if content_to_add or image_path:
                    if current_q["answer"] is None:
                        # We are still in Question block (Answer not detected yet)
                        if content_to_add:
                             current_q["question"] += "\n" + content_to_add
                        if image_path and not current_q["image_path"]:
                             current_q["image_path"] = image_path
                    else:
                        # We are in Answer block
                        if content_to_add:
                            # If answer was empty, just set it, else append
                            if current_q["answer"]:
                                current_q["answer"] += "\n" + content_to_add
                            else:
                                current_q["answer"] = content_to_add
                        # Optionally handle images in answers? For now, ignore or attach to Q.
    
    # Append last
    if current_q:
        # Normalize None to empty string before saving
        if current_q["answer"] is None:
             current_q["answer"] = ""
        questions.append(current_q)
        
    return {"metadata": metadata, "questions": questions}

    return {"metadata": metadata, "questions": questions}

class ActionCheckUploadPermissions(Action):
    def name(self) -> Text:
        return "action_check_upload_permissions"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # --- AUTH CHECK ---
        # 1. User must be logged in
        if not check_user_access(tracker):
            dispatcher.utter_message(text="🚫 Αυτή η λειτουργία είναι διαθέσιμη μόνο για εγγεγραμμένους χρήστες.")
            return []

        # 2. User must be Administrator
        role = tracker.get_slot("role")
        # Debug Log
        print(f"DEBUG AUTH: Checking permissions for Upload. Role='{role}'")
        
        if not role or role.lower() != "administrator":
             dispatcher.utter_message(text="📢 Για την προσθήκη νέου υλικού, παρακαλώ επικοινωνήστε με τον διαχειριστή του συστήματος στο email: admin@schoolbot.com")
             return []
        
        # If Admin, Proceed to Form
        return [FollowupAction("upload_exam_form")]

class ActionUploadExamMaterial(Action):
    def name(self) -> Text:
        return "action_upload_exam_material"


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # --- AUTH CHECK ---
        if not check_user_access(tracker):
            dispatcher.utter_message(text="🚫 Αυτή η λειτουργία είναι διαθέσιμη μόνο για εγγεγραμμένους χρήστες. Παρακαλώ συνδεθείτε στην ιστοσελίδα!")
            return []
        # ------------------

        file_path = tracker.get_slot("upload_file_path")
        
        # Sanitize File Path (Remove quotes if user added them)
        # Fallback 2: History Scan (Crucial for Forms)
        # If slot is bad, look backwards in conversation history for the file path.
        if not file_path or len(file_path) < 5 or (not file_path.lower().endswith('.docx') and not file_path.lower().endswith('.pdf')):
            print("DEBUG: Slot invalid. Scanning history for file path...")
            for event in reversed(tracker.events):
                 if event.get("event") == "user":
                     msg_text = event.get("text", "").strip()
                     if len(msg_text) > 4 and ('.docx' in msg_text.lower() or '.pdf' in msg_text.lower()):
                         print(f"DEBUG: Found path in history: {msg_text}")
                         file_path = msg_text.strip().strip('"').strip("'")
                         break

        if file_path:
            # Clean up path (remove quotes)
            file_path = file_path.strip().strip('"').strip("'")
            
            # Helper to check variations
            def check_path_variations(path):
                candidates = [
                    path,
                    path + ".docx",
                    path.replace(".doc", ".docx"),
                    os.path.join("files", os.path.basename(path)),
                    os.path.join("files", os.path.basename(path) + ".docx"),
                    os.path.join("files", os.path.basename(path).replace(".doc", ".docx")),
                    os.path.join("/app/files", os.path.basename(path)),
                    os.path.join("/app/files", os.path.basename(path) + ".docx"),
                    os.path.join("/app/files", os.path.basename(path).replace(".doc", ".docx"))
                ]
                for c in candidates:
                    if os.path.exists(c):
                        return c
                return None

            found_path = check_path_variations(file_path)
            
            if found_path:
                 print(f"DEBUG: Resolved '{file_path}' to '{found_path}'")
                 file_path = found_path
            else:
                 print(f"DEBUG: File not found after trying variations of: {file_path}")
                 # Fallback logic continues, will error out later if strict check fails
            
            # Deep Debug to File
            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"\n--- New Upload Attempt ---\n")
                f.write(f"Final Path: {file_path}\n")
                f.write(f"Exists: {os.path.exists(file_path)}\n")
        
        # Default Slots
        
        # Default Slots
        subject = tracker.get_slot("subject")
        grade = tracker.get_slot("grade")
        difficulty = tracker.get_slot("difficulty")
        
        # 1. Filename Parsing (Fallback 1)
        if file_path:
            filename = os.path.basename(file_path)
            parts = filename.split('_')
            
            if len(parts) >= 3:
                subj_map = {"Math": "Μαθηματικά", "Physics": "Φυσική", "Chemistry": "Χημεία", "History": "Ιστορία"}
                if parts[0] in subj_map: subject = subj_map[parts[0]]
                
                grade_map = {"A": "Α Γυμνασίου", "B": "Β Γυμνασίου", "C": "Γ Γυμνασίου", "G": "Γ Γυμνασίου"}
                if parts[1] in grade_map: grade = grade_map[parts[1]]

                diff_map = {"Easy": "εύκολο", "Medium": "μέτριο", "Hard": "δύσκολο"}
                if parts[2] in diff_map: difficulty = diff_map[parts[2]]
        else:
             dispatcher.utter_message(text=f"Δεν βρέθηκε διαδρομή αρχείου.")
             return []

        # Validation
        if not os.path.exists(file_path):
            dispatcher.utter_message(text=f"Δεν βρέθηκε το αρχείο: {file_path}")
            return []

        try:
            parsed_data = {}
            questions = []
            
            if file_path.lower().endswith('.pdf'):
                # PDF uses old list logic for now
                questions = extract_questions_from_pdf(file_path)
            elif file_path.lower().endswith('.docx'):
                # New Docx Parsing returns Dict
                parsed_data = extract_questions_from_docx(file_path)
                questions = parsed_data.get("questions", [])
                metadata = parsed_data.get("metadata", {})
                
                # 2. Metadata Parsing (Highest Priority)
                if metadata.get("subject"): subject = metadata["subject"]
                if metadata.get("grade"): grade = metadata["grade"]
                if metadata.get("difficulty"): difficulty = metadata["difficulty"]
            else:
                 dispatcher.utter_message(text=f"Μη υποστηριζόμενος τύπος αρχείου. Παρακαλώ ανεβάστε .pdf ή .docx")
                 return []
            
            if not questions:
                dispatcher.utter_message(text="Δεν μπόρεσα να βρω ερωτήσεις. Ελέγξτε τη μορφοποίηση (ΕΡΩΤΗΣΗ ... / ΑΠΑΝΤΗΣΗ ...).")
                return []

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            count = 0
            for q in questions:
                final_grade = q.get("detected_grade", grade) # Grade might be detected per question block
                img = q.get("image_path")
                
                c.execute("INSERT INTO questions (subject, class_name, difficulty, question_text, answer_text, source_file, image_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (subject, final_grade, difficulty, q['question'], q['answer'], filename, img))
                count += 1
            
            conn.commit()
            conn.close()
            
            dispatcher.utter_message(text=f"Επιτυχία! Αποθηκεύτηκαν {count} ερωτήσεις από το {filename} ({subject}, {grade}, {difficulty}).")
            
        except Exception as e:
            dispatcher.utter_message(text=f"Σφάλμα κατά την επεξεργασία: {str(e)}")
            print(f"Error parsing file: {e}")

        return [SlotSet("upload_file_path", None)]

class ActionCreateExamNew(Action):

    def name(self) -> Text:
        return "action_create_exam_new"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # --- AUTH CHECK ---
        if not check_user_access(tracker):
            dispatcher.utter_message(text="🚫 Αυτή η λειτουργία είναι διαθέσιμη μόνο για εγγεγραμμένους χρήστες. Παρακαλώ συνδεθείτε στην ιστοσελίδα!")
            return []
        # ------------------

        print("DEBUG: Entered ActionCreateExam - IF YOU SEE THIS, IT WORKS")

        subject = tracker.get_slot("subject")
        difficulty = tracker.get_slot("difficulty")
        grade = tracker.get_slot("grade")
        include_answers = tracker.get_slot("include_answers")
        
        # 1. Dynamic Question Count
        num_questions = tracker.get_slot("num_questions")
        if not num_questions:
            num_questions = 3
        else:
            try:
                num_questions = int(num_questions)
            except:
                num_questions = 3
        
        print(f"DEBUG EXAM: Subject='{subject}', Grade='{grade}', Diff='{difficulty}', Num='{num_questions}'")

        # Normalize Grade Input
        grade_map_input = {
            "a": "Α Γυμνασίου", "α": "Α Γυμνασίου",
            "b": "Β Γυμνασίου", "β": "Β Γυμνασίου",
            "c": "Γ Γυμνασίου", "g": "Γ Γυμνασίου", "γ": "Γ Γυμνασίου"
        }
        
        if grade:
            raw_grade = str(grade).lower().strip()
            if raw_grade in grade_map_input:
                grade = grade_map_input[raw_grade]
            elif len(raw_grade) == 1:
                 grade = f"{grade.upper()} Γυμνασίου"

        # Accent Stripping & Lowercasing Helper
        def normalize_text(input_str):
            if not input_str: return ""
            # 1. Lowercase (Python handles Greek correctly)
            s = input_str.lower()
            
            # 2. Remove Accents
            replacements = {
                'ά': 'α', 'έ': 'ε', 'ή': 'η', 'ί': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ώ': 'ω',
                'ϊ': 'ι', 'ϋ': 'υ', 'ς': 'σ' # Normalize final sigma too
            }
            for char, repl in replacements.items():
                s = s.replace(char, repl)
            return s

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # Create custom function for SQL
        conn.create_function("NORMALIZE", 1, normalize_text)
        c = conn.cursor()
        
        # Build Query using custom function
        # NORMALIZE(subject) handles both casing and accents
        query = "SELECT * FROM questions WHERE 1=1"
        params = []
        
        if subject:
            query += " AND NORMALIZE(subject) = NORMALIZE(?)"
            params.append(subject)
        if difficulty:
            query += " AND NORMALIZE(difficulty) = NORMALIZE(?)"
            params.append(difficulty)
        if grade:
            query += " AND NORMALIZE(class_name) = NORMALIZE(?)"
            params.append(grade)
            
        print(f"DEBUG SQL: {query} | Params: {params}")
        
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(num_questions)
        
        c.execute(query, tuple(params))
        rows = c.fetchall()
        
        if not rows:
            # Fallback: Try looser Grade Match (e.g. match 'B' inside 'B Gymnasioy')
            print("DEBUG: Strict match failed. Trying loose grade match.")
            query = "SELECT * FROM questions WHERE REMOVE_ACCENTS(LOWER(subject)) = REMOVE_ACCENTS(LOWER(?))"
            params = [subject]
            
            # Simple Grade check
            # Just grab any grade starting with the letter if simple letter provided
            if len(grade) == 1 or "Γυμνασίου" not in grade:
                 # Logic for fallback
                 pass 
            
            # Re-execute query without grade strictness? No, that's dangerous.
            # Let's just report failure but with more info.
            
            c.execute("SELECT DISTINCT subject, class_name, difficulty FROM questions")
            available = c.fetchall()
            print(f"DEBUG: Available in DB: {[dict(row) for row in available]}")
            
            conn.close()
            dispatcher.utter_message(text=f"Δεν βρέθηκαν ερωτήσεις. Έψαξα για: {subject}, {grade}, {difficulty}.")
            return []
        
        conn.close()

        # Create PDF
        filename = f"Exam_{subject}_{difficulty}_{random.randint(1000,9999)}.pdf"
        filepath = os.path.join(GENERATED_EXAMS_DIR, filename)
        
        try:
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            
            # Header
            c.setFont("GreekFont", 16)
            c.drawString(50, height - 50, f"Διαγώνισμα: {subject}")
            c.setFont("GreekFont", 12)
            c.drawString(50, height - 70, f"Τάξη: {grade} | Δυσκολία: {difficulty}")
            c.drawString(50, height - 90, "-" * 80)
            
            y_position = height - 120
            
            def sanitize_text(t):
                if not t: return ""
                # Replace common non-printable chars
                t = t.replace('\r', '').replace('\t', '    ')
                # Filter out the specific rectangle char if possible, or just expect simple text
                # Simple ASCII/Greek filter could be too aggressive.
                # Let's just strip basic whitespace for now.
                return t
            
            for idx, row in enumerate(rows, 1):
                # Page Break Check
                if y_position < 150:
                    c.showPage()
            import re
            # Helper for simple text wrapping with Newline support
            def draw_multiline_text(c, text, x, start_y, font_name, font_size, max_width):
                if not text: return start_y
                c.setFont(font_name, font_size)
                
                # 1. Clean up weird chars (Fix for Squares)
                text = text.replace('\r', '').replace('\t', ' ')
                
                # 2. Split by explicit newlines first
                paragraphs = text.split('\n')
                
                current_y = start_y
                
                for paragraph in paragraphs:
                    words = paragraph.split(' ')
                    current_line = []
                    for word in words:
                        # Check word width
                        test_line = ' '.join(current_line + [word])
                        if c.stringWidth(test_line, font_name, font_size) < max_width:
                            current_line.append(word)
                        else:
                            # Draw current line
                            c.drawString(x, current_y, ' '.join(current_line))
                            current_y -= (font_size + 4) # Line spacing
                            current_line = [word]
                    
                    # Draw remaining part of paragraph
                    if current_line:
                        c.drawString(x, current_y, ' '.join(current_line))
                        current_y -= (font_size + 4)
                        
                return current_y

            answers_text = []
            
            # Check explicitly for affirmative values
            show_answers = str(include_answers).lower() in ['true', 'yes', 'nai', 'ναι', 'βέβαια', 'y']
            print(f"DEBUG ANSWERS: Slot='{include_answers}', Show={show_answers}")
            
            for i, row in enumerate(rows, 1):
                question_text = row['question_text']
                answer = row['answer_text']
                
                # --- HEURISTIC V4: Polyglot Strategy (Latin + Greek) ---
                # Normalize line endings
                question_text = question_text.replace('\r', '\n')
                
                # Split into lines
                lines = question_text.strip().split('\n')
                candidates = []
                
                if len(lines) > 1:
                    last_line = lines[-1].strip()
                    # Clean: Remove non-alphanumeric (keep Greek & Latin)
                    # We check if it is A,B,C,D,E or Α,Β,Γ,Δ,Ε
                    clean_last = re.sub(r'[^ΑΒΓΔΕA-E]', '', last_line)
                    
                    if len(clean_last) == 1 and len(last_line) < 5:
                        raw_ans = clean_last
                        # Map Latin to Greek just in case
                        mapping = {'A':'Α', 'B':'Β', 'C':'Γ', 'D':'Δ', 'E':'Ε'}
                        answer = mapping.get(raw_ans, raw_ans)
                        
                        question_text = '\n'.join(lines[:-1]).strip()
                        print(f"DEBUG: Extracted answer '{answer}' (was {raw_ans}) via LastLine Q{i}")

                # Fallback Regex (Global)
                if not answer:
                     # Check for A-E or Greek chars at end
                     match = re.search(r'[\n\s]+([ΑΒΓΔΕA-E])[\s\W]*$', question_text)
                     if match:
                         raw_ans = match.group(1)
                         mapping = {'A':'Α', 'B':'Β', 'C':'Γ', 'D':'Δ', 'E':'Ε'}
                         answer = mapping.get(raw_ans, raw_ans)
                         
                         question_text = question_text[:match.start()].strip()
                         print(f"DEBUG: Extracted answer '{answer}' (was {raw_ans}) via Regex Q{i}")
                # ---------------------------------------

                # Save extracted answer back to row-like object for later use if needed? 
                # Actually 'answer' var is what we use below.
                # Store it in a list to use for the Answer Key page
                answers_text.append(f"{i}. {answer if answer else '-'}")

                # Add Question Label
                header = f"Ερώτηση {i}:"
                c.setFont("GreekFont-Bold", 12)
                c.drawString(50, y_position, header)
                y_position -= 20
                
                # Draw Question Body
                y_position = draw_multiline_text(c, question_text, 50, y_position, "GreekFont", 12, width - 100)
                
                # Image Handling
                if row['image_path'] and os.path.exists(row['image_path']):
                    try:
                        img_path = row['image_path']
                        pil_img = Image.open(img_path)
                        img_w, img_h = pil_img.size
                        aspect = img_h / float(img_w)
                        display_w = 400
                        display_h = display_w * aspect
                        if display_h > 200: 
                            display_h = 200
                            display_w = display_h / aspect
                        
                        if y_position - display_h < 50:
                            c.showPage()
                            y_position = height - 50
                            
                        c.drawImage(img_path, 50, y_position - display_h, width=display_w, height=display_h, mask='auto')
                        y_position -= (display_h + 10)
                    except Exception as img_e:
                        print(f"Failed to draw image: {img_e}")
                
                y_position -= 20
                
                # Page Break for next question if needed
                if y_position < 50:
                     c.showPage()
                     y_position = height - 50

            # --- ANSWER KEY GENERATION ---
            print(f"DEBUG PDF: Finished Questions. ShowAnswers={show_answers}. AnswersList={answers_text}")
            
            if show_answers:
                # FORCE NEW PAGE for Answers
                c.showPage()
                y_position = height - 50
                
                c.setFont("GreekFont-Bold", 16)
                c.drawString(50, y_position, "Απαντήσεις (Answer Key)")
                y_position -= 40
                c.setFont("GreekFont", 12)
                
                for line in answers_text:
                    if y_position < 50:
                        c.showPage()
                        y_position = height - 50
                    c.drawString(50, y_position, line)
                    y_position -= 20
            # -----------------------------
            
            c.save()
            abs_path = os.path.abspath(filepath)
            # Create Public URL
            file_name = os.path.basename(filepath)
            public_url = f"https://104.155.53.205.nip.io/files/generated_exams/{file_name}"
            
            dispatcher.utter_message(text=f"Το διαγώνισμα δημιουργήθηκε! (v2 Security Check)\n\n{public_url}")
            
        except Exception as e:
            dispatcher.utter_message(text=f"Σφάλμα PDF: {e}")
            print(e)
            
        return []


class ActionSearchArticles(Action):

    def name(self) -> Text:
        return "action_search_articles"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        query = tracker.get_slot("query")
        if not query:
             dispatcher.utter_message(text="Τι ψάχνετε ακριβώς;")
             return []

        # Wordpress REST API URL (Plain Permalinks)
        url = f"https://ignatislask.sites.sch.gr/?rest_route=/wp/v2/posts&search={query}"
        
        try:
            import requests
            # Add headers to mimic a browser (avoids blocking)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            
            # verify=False prevents SSL Certificate errors (common in school networks)
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                posts = response.json()
                if posts:
                    # Get top 3 results
                    message_text = "Βρήκα τα εξής σχετικά άρθρα:\n"
                    for post in posts[:3]:
                        title = post['title']['rendered']
                        link = post['link']
                        message_text += f"- [{title}]({link})\n"
                    
                    dispatcher.utter_message(text=message_text)
                else:
                    dispatcher.utter_message(text=f"Δεν βρέθηκαν άρθρα για '{query}'.")
            else:
                dispatcher.utter_message(text=f"Σφάλμα σύνδεσης (Status: {response.status_code}).")
        
        except Exception as e:
            dispatcher.utter_message(text="Κάτι πήγε στραβά με την αναζήτηση.")
            print(f"Error accessing API: {e}")

        return []



class ActionSmartFaq(Action):

    def name(self) -> Text:
        return "action_smart_faq"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intent = tracker.latest_message['intent'].get('name')
        
        # Configuration for Hybrid FAQs: Intent -> (Search Keyword, Fallback Link)
        faq_map = {
            "faq_parent_briefing":          {"q": "ενημέρωση γονέων",      "url": "https://ignatislask.sites.sch.gr/?page_id=6"},
            "faq_model_exams_applications": {"q": "αιτήσεις πρότυπα",      "url": "https://ignatislask.sites.sch.gr/?cat=25"},
            "faq_model_exams_process":      {"q": "εισαγωγή πρότυπα",      "url": "https://ignatislask.sites.sch.gr/?p=2989"},
            "faq_model_exams_runners_up":   {"q": "πίνακας επιλαχόντων",   "url": "https://ignatislask.sites.sch.gr/?p=3561"},
            "faq_attendance_info":          {"q": "φοίτηση πρότυπα",       "url": "https://ignatislask.sites.sch.gr/?cat=32"},
            "faq_absences":                 {"q": "απουσίες μαθητών",      "url": "https://ignatislask.sites.sch.gr/?cat=32"},
            "faq_remedial_teaching":        {"q": "ενισχυτική διδασκαλία", "url": "https://ignatislask.sites.sch.gr/?p=411"},
        }

        config = faq_map.get(intent)
        
        if not config:
            # Fallback if mapped intent is missing config
            dispatcher.utter_message(text="Δεν βρήκα συγκεκριμένες πληροφορίες για αυτό.")
            return []

        search_query = config["q"]
        fallback_link = config["url"]
        
        # 1. Perform Search (Similar logic to ActionSearchArticles)
        search_results_text = ""
        try:
            import requests
            # Wordpress REST API
            url = f"https://ignatislask.sites.sch.gr/?rest_route=/wp/v2/posts&search={search_query}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(url, headers=headers, timeout=5, verify=False)
            
            if response.status_code == 200:
                posts = response.json()
                if posts:
                    search_results_text = f"🔎 Βρήκα επίσης αυτά τα σχετικά άρθρα για '{search_query}':\n"
                    # Top 3 results
                    for post in posts[:3]:
                        title = post['title']['rendered']
                        link = post['link']
                        search_results_text += f"- [{title}]({link})\n"
                    search_results_text += "\n"
        except Exception as e:
            print(f"SmartFAQ Search Error: {e}")
            # Silently fail search and just show the static link
            pass

        # 2. Construct Final Message
        final_message = search_results_text
        final_message += f"👉 Για την πλήρη και επίσημη ενημέρωση, δείτε εδώ:\n{fallback_link}"

        dispatcher.utter_message(text=final_message)
        return []
