
import sqlite3
import os

# Adjust path for when running inside container where actions/ is just a subfolder
# But we run this from /app usually.
DB_PATH = "data/questions.db" 

def view_last_entries(limit=5):
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("SELECT id, title, subject, grade, url FROM study_materials ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        print(f"\n--- Last {limit} Entries ---")
        for r in rows:
            print(f"ID: {r[0]} | Title: {r[1]} | Subj: {r[2]} | Grade: {r[3]} | URL: {r[4]}")
    except Exception as e:
        print(f"Error reading DB: {e}")
    finally:
        conn.close()

def delete_entry_by_id(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM study_materials WHERE id = ?", (entry_id,))
        if c.rowcount > 0:
            print(f"Successfully deleted ID {entry_id}")
            conn.commit()
        else:
            print(f"No entry found with ID {entry_id}")
    except Exception as e:
        print(f"Error deleting: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    while True:
        choice = input("\n1. View Last Entries\n2. Delete Entry by ID\n3. Exit\nChoice: ")
        if choice == "1":
            view_last_entries()
        elif choice == "2":
            uid = input("Enter ID to delete: ")
            if uid.isdigit(): delete_entry_by_id(int(uid))
        elif choice == "3":
            break
