import streamlit as st
import sqlite3
import os
from PIL import Image
import uuid

# Configuration
DB_PATH = "data/questions.db"
IMAGES_DIR = "files/images"

# Ensure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Check/Create table with image_path (Simple check)
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subject TEXT,
                  class_name TEXT,
                  difficulty TEXT,
                  question_text TEXT,
                  answer_text TEXT,
                  source_file TEXT,
                  image_path TEXT)''')
    try:
        c.execute("ALTER TABLE questions ADD COLUMN image_path TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="Rasa Exam Admin", layout="wide")

st.title("🎓 Διαχείριση Τράπεζας Θεμάτων")
st.markdown("Προσθέστε νέες ερωτήσεις και σχήματα στη βάση του Bot.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Νέα Ερώτηση")
    
    subject = st.selectbox("Μάθημα", ["Φυσική", "Μαθηματικά", "Χημεία", "Άλλο"])
    grade = st.selectbox("Τάξη", ["Α Γυμνασίου", "Β Γυμνασίου", "Γ Γυμνασίου"])
    difficulty = st.selectbox("Δυσκολία", ["εύκολο", "μέτριο", "δύσκολο"])
    
    question_text = st.text_area("Κείμενο Ερώτησης", height=150)
    answer_text = st.text_area("Απάντηση / Λύση", height=100)
    
    uploaded_file = st.file_uploader("🖼️ Προσθήκη Εικόνας/Σχήματος (Προαιρετικό)", type=['png', 'jpg', 'jpeg'])

with col2:
    st.subheader("👁️ Προεπισκόπηση")
    
    st.info(f"**Μάθημα:** {subject} | **Τάξη:** {grade}")
    st.markdown(f"**Ερώτηση:**\n{question_text if question_text else '...'}")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Σχήμα Ερώτησης", use_container_width=True)
    
    st.markdown("---")
    st.markdown(f"**Απάντηση:**\n{answer_text if answer_text else '...'}")

    st.markdown("---")
    if st.button("💾 Αποθήκευση στη Βάση", type="primary"):
        if not question_text:
            st.error("Παρακαλώ γράψτε τουλάχιστον το κείμενο της ερώτησης.")
        else:
            image_path = None
            if uploaded_file is not None:
                # Generate unique filename
                ext = uploaded_file.name.split('.')[-1]
                filename = f"{uuid.uuid4()}.{ext}"
                save_path = os.path.join(IMAGES_DIR, filename)
                
                # Save Image
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                image_path = save_path # Save relative or absolute? Relative is better for Docker.
            
            # Save to DB
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""INSERT INTO questions 
                             (subject, class_name, difficulty, question_text, answer_text, source_file, image_path) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)""",
                          (subject, grade, difficulty, question_text, answer_text, "Manual_Entry", image_path))
                conn.commit()
                conn.close()
                st.success("Η ερώτηση αποθηκεύτηκε επιτυχώς!")
                st.balloons()
            except Exception as e:
                st.error(f"Σφάλμα κατά την αποθήκευση: {e}")

st.markdown("---")
st.markdown("---")
st.header("📂 Περιήγηση Ερωτήσεων")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Φίλτρα Αναζήτησης")

# Get unique values for filters
conn = sqlite3.connect(DB_PATH)
subjects = [r[0] for r in conn.execute("SELECT DISTINCT subject FROM questions WHERE subject IS NOT NULL").fetchall()]
grades = [r[0] for r in conn.execute("SELECT DISTINCT class_name FROM questions WHERE class_name IS NOT NULL").fetchall()]
difficulties = [r[0] for r in conn.execute("SELECT DISTINCT difficulty FROM questions WHERE difficulty IS NOT NULL").fetchall()]
conn.close()

selected_subject = st.sidebar.selectbox("Μάθημα", ["Όλα"] + subjects)
selected_grade = st.sidebar.selectbox("Τάξη", ["Όλα"] + grades)
selected_difficulty = st.sidebar.selectbox("Δυσκολία", ["Όλα"] + difficulties)
search_query = st.sidebar.text_input("Αναζήτηση Κειμένου", "")

# --- Build Query ---
query = "SELECT id, subject, class_name, difficulty, question_text, image_path FROM questions WHERE 1=1"
params = []

if selected_subject != "Όλα":
    query += " AND subject = ?"
    params.append(selected_subject)
if selected_grade != "Όλα":
    query += " AND class_name = ?"
    params.append(selected_grade)
if selected_difficulty != "Όλα":
    query += " AND difficulty = ?"
    params.append(selected_difficulty)
if search_query:
    query += " AND question_text LIKE ?"
    params.append(f"%{search_query}%")

query += " ORDER BY id DESC"

# --- Fetch Data ---
conn = sqlite3.connect(DB_PATH)
try:
    # Use pandas if available for better display, else raw list
    import pandas as pd
    df = pd.read_sql_query(query, conn, params=params)
    
    st.write(f"Βρέθηκαν **{len(df)}** ερωτήσεις.")
    
    if not df.empty:
        # Display as interactive dataframe
        st.dataframe(df, use_container_width=True)
        
        # Optional: Detailed View of selected row?
        # For now, just the table is enough as per request.
    else:
        st.info("Δεν βρέθηκαν ερωτήσεις με αυτά τα κριτήρια.")
        
except Exception as e:
    st.error(f"Error loading data: {e}")
finally:
    conn.close()

# --- Delete Section ---
st.markdown("---")
with st.expander("🗑️ Διαγραφή Ερώτησης", expanded=False):
    st.warning("Προσοχή! Η διαγραφή είναι οριστική.")
    
    # Reload connection for delete selector
    conn = sqlite3.connect(DB_PATH)
    all_questions = conn.execute("SELECT id, subject, question_text FROM questions ORDER BY id DESC").fetchall()
    conn.close()
    
    # Format: "ID: Subject - Text..."
    question_options = {q[0]: f"{q[0]}: {q[1]} - {q[2][:50]}..." for q in all_questions}
    
    selected_delete_id = st.selectbox("Επιλέξτε ερώτηση για διαγραφή:", options=list(question_options.keys()), format_func=lambda x: question_options[x])
    
    if st.button("Οριστική Διαγραφή ❌", type="primary"):
        if selected_delete_id:
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM questions WHERE id = ?", (selected_delete_id,))
                conn.commit()
                conn.close()
                st.success(f"Η ερώτηση {selected_delete_id} διαγράφηκε.")
                st.rerun()
            except Exception as e:
                st.error(f"Σφάλμα κατά τη διαγραφή: {e}")
