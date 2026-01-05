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
st.header("📊 Υπάρχουσες Ερωτήσεις (Τελευταίες 10)")

conn = sqlite3.connect(DB_PATH)
df = conn.execute("SELECT id, subject, class_name, question_text, image_path FROM questions ORDER BY id DESC LIMIT 10").fetchall()
conn.close()

if df:
    # Custom display or DataFrame
    st.table(df)
else:
    st.write("Η βάση είναι ακόμα άδεια.")
