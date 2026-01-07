import sys
import os

# Add /app/actions to path so we can import 'actions' module
sys.path.append('/app/actions')

try:
    from actions import extract_questions_from_docx
except ImportError:
    # If running from inside actions folder, try relative
    try:
        from actions import extract_questions_from_docx
    except:
        # Maybe we are IN the actions folder, so just import actions?
        # No, actions.py is the file.
        # Let's try direct import assuming we are running as script
        # But actions.py has classes.
        pass

# Workaround to import 'extract_questions_from_docx' from 'actions.py'
import importlib.util
def load_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

try:
    actions_mod = load_module_from_path("actions", "/app/actions/actions.py")
    extract_func = actions_mod.extract_questions_from_docx
    print("✅ Successfully imported extract_questions_from_docx")
except Exception as e:
    print(f"❌ Failed to import actions.py: {e}")
    sys.exit(1)

FILE_PATH = "/app/files/Math_A_Easy_1.docx"

if not os.path.exists(FILE_PATH):
    print(f"❌ File not found at {FILE_PATH}")
    # Try local
    if os.path.exists("files/Math_A_Easy_1.docx"):
         FILE_PATH = "files/Math_A_Easy_1.docx"
    else:
         sys.exit(1)

print(f"📂 Parsing: {FILE_PATH}")
try:
    result = extract_func(FILE_PATH)
    questions = result.get("questions", [])
    print(f"📊 Found {len(questions)} questions.")
    
    for i, q in enumerate(questions, 1):
        q_short = q['question'][:30].replace('\n', ' ')
        a_short = q['answer'][:30].replace('\n', ' ') if q['answer'] else "EMPTY"
        print(f"Q{i}: {q_short}...")
        print(f"    ANS: '{a_short}'")
        if not q['answer']:
             print("    🚨 PROBLEM: Answer is empty!")

except Exception as e:
    print(f"❌ Error during parsing: {e}")

