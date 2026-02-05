
import os

file_path = "data/nlu.yml"

# The text to append. I am gathering this from previous context.
restored_content = """
- intent: upload_exam_material
  examples: |
    - θέλω να ανεβάσω αρχεία
    - ανέβασμα αρχείου
    - καταχώρηση νέου διαγωνίσματος
    - προσθήκη αρχείου
    - εχω ενα pdf για ανεβασμα
    - θέλω να προσθέσω ερωτήσεις
    - upload material
    - θελω να ανεβασω ενα διαγωνισμα
    - θέλω να ανεβάσω ένα διαγώνισμα
    - καταχωρηση υλικου
    - προσθηκη νεων θεματων
    - ανεβασμα θεματων εξετασεων
    - upload file
    - εισαγωγή αρχείου pdf
    - αποθήκευση διαγωνίσματος

- intent: upload_study_material
  examples: |
    - ανεβασμα υλικου μελετης
    - ανεβασμα υλικου διαβασματος
    - προσθήκη υλικου μελετης
    - θελω να ανεβασω σημειωσεις
    - αποθηκευση υλικου διαβασματος
    - καταχωρηση νεων σημειωσεων
    - ανεβασμα pdf μελετης
    - new study material
    - θελω να προσθεσω υλη για διαβασμα
    - ανεβασμα βοηθηματων
    - Θέλω να αναρτήσω υλικό για διάβασμα
    - θελω να αναρτησω υλικο για διαβασμα
    - Θελω να αναρτήσω υλικο για μελέτη
    - θελω να αναρτήσω υλικο για μελέτη
    - Θελω να αναρτήσω υλικο για μελετη
    - θελω να αναρτήσω υλικο για μελετη
    - Θελω να ανεβάσω υλικό για διαβασμα
    - θελω να ανεβάσω υλικό για διαβασμα
    - θελω να ανεβασω υλικό για μελέτη
    - θελω να ανεβασω υλικο για μελετη
    - Αναρτηση υλικού διαβασματος
    - αναρτηση υλικού διαβασματος
    - Αναρτηση υλικού μελετης
    
- intent: thankyou
  examples: |
    - Ευχαριστώ
    - ευχαριστώ πολύ
    - να σαι καλά
    - thanks
    - ty
    - thx
    - σε ευχαριστώ
    - τέλεια ευχαριστώ

- intent: deny
  examples: |
    - όχι
    - οχι
    - no
    - δεν θέλω
    - με τίποτα
    - όχι ευχαριστώ
    - οχι ευχαριστω
    - not really
    - nope
    - n

- intent: restart_conversation
  examples: |
    - Κάνε επανεκκίνηση
    - Ας ξεκινήσουμε από την αρχή
    - Πάμε από την αρχή
    - restart
    - επανεκκίνηση
    - αρχικη
    - ξεκινα παλι

- intent: inform_role_student
  examples: |
    - Μαθητής
    - Μαθητης
    - μαθητής
    - μαθητης
    - ΜΑΘΗΤΗΣ
    - ειμαι μαθητης
    - είμαι μαθητής
    - ρόλος μαθητή
    - επιλέγω μαθητής
    - student

- intent: inform_role_parent
  examples: |
    - Γονέας
    - Γονεας
    - γονέας
    - γονεας
    - γονιος
    - γονιός
    - κηδεμόνας
    - κηδεμόνας
    - ειμαι γονεας
    - είμαι γονιός
    - ρόλος γονέα
    - parent

- intent: inform_role_teacher
  examples: |
    - εκπαιδευτικός
    - εκπαιδευτικος
    - Εκπαιδευτικός
    - Εκπαιδευτικος
    - ΕΚΠΑΙΔΕΥΤΙΚΟΣ
    - ΚΑΘΗΓΗΤΗΣ
    - καθηγητής
    - ειμαι εκπαιδευτικος
    - ρόλος καθηγητή
    - teacher

- intent: ask_study_material
  examples: |
    - δωσε υλικο για διαβασμα
    - θελω υλικό για διαβασμα
    - μπορω να εχω υλικο για διαβασμα
    - θα ηθελα υλικο για διαβασμα
    - Υλικό για Διάβασμα
    - υλικό για διάβασμα
    - θέλω να διαβάσω
    - δώσε μου κάτι να διαβάσω
    - έχεις σημειώσεις;
    - σημειώσεις για μάθημα
    - υλικο μελετης
    - ΘΕΛΩ ΥΛΙΚΟ ΓΙΑ ΔΙΑΒΑΣΜΑ
    - ΥΛΙΚΟ ΓΙΑ ΔΙΑΒΑΣΜΑ
    - ΔΩΣΕ ΜΟΥ ΥΛΙΚΟ ΓΙΑ ΔΙΑΒΑΣΜΑ
    - Δωσε υλικο να διαβασω
    - υλικοΟ
    - υπαρχει τιποτα για διαβασμα;
    - θελω να μελετησω
    - βρες μου καμια σημειωση
    - ψαχνω υλικο για μαθηματικα
    - θελω να δω τι υλικο υπαρχει
    - δειξε μου σημειωσεις
    - διαβασμα
    - διάβασμα
    - ΔΙΑΒΑΣΜΑ
    - θελω διαβασμα
    - υλικο για μελετη
    - βοηθηματα
    - ασκησεις για διαβασμα
    - θελω να κανω επαναληψη
    - υπαρχει υλικο για διαβασμα;
    - θελω να προετοιμαστω για εξετασεις
    - που θα βρω σημειωσεις
    - δωσε μου σημειωσεις
    - εχεις ασκησεις;
    - θέλω να βρω υλικό για ανάγνωση
    - Θέλω υλικό για ανάγνωση
    - Θέλω να βρω υλικό για μελέτη
    - Θέλω υλικό για μελέτη
    - υλικό για ανάγνωση
    - υλικό για μελέτη
    - Δώσε μου υλικό για μελέτη
    - Δώσε μου υλικό για ανάγνωση
    - Πως μπορώ να βρω υλικό για μελέτη
    - Πως μπορώ να βρω υλικό για ανάγνωση
    - Πού μπορώ να βρω το υλικό για διάβασμα;
    - Έχει ανέβει υλικό μελέτης;
    - Μπορείς να μου δείξεις τις σημειώσεις;
    - Πού βρίσκω το υλικό που έδωσε ο καθηγητής;
    - Υπάρχει υλικό για επανάληψη;
    - Έχει ασκήσεις για εξάσκηση;
    - Πού μπορώ να κατεβάσω το υλικό;
    - Υπάρχει βοηθητικό υλικό για το διάβασμα;
    - Έχει αναρτηθεί νέο υλικό;
    - Μπορώ να δω παλιό υλικό μελέτης;

- intent: faq_regulations
  examples: |
    - Πού μπορώ να βρω τον κανονισμό λειτουργίας του σχολείου;
    - Σε ποιο σημείο της πλατφόρμας είναι ο κανονισμός;
    - Υπάρχει αρχείο ή έγγραφο με τον κανονισμό;
    - Μπορώ να κατεβάσω τον κανονισμό του σχολείου;
    - Έχει αναρτηθεί κάπου ο κανονισμός λειτουργίας;
    - Ποιος είναι ο κανονισμός λειτουργίας του σχολείου;
    - Πού μπορώ να δω τον κανονισμό;
    - Τι ισχύει για τη συμπεριφορά στο σχολείο;
    - Υπάρχουν κανόνες που πρέπει να ακολουθούμε;
    - Τι προβλέπεται αν δεν τηρηθεί ο κανονισμός;
    - Τι επιτρέπεται και τι όχι στο σχολείο;
    - Υπάρχουν κανόνες για την καθημερινή παρουσία στο σχολείο;
    - Πού αναφέρονται οι υποχρεώσεις των μαθητών;
    - Υπάρχουν κυρώσεις αν παραβιαστούν οι κανόνες;
    - Ο κανονισμός ισχύει και στις σχολικές δραστηριότητες;
"""

try:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Find the end of faq_contact_hours. 
    # The last known good line before corruption is probably under faq_contact_hours
    # We look for "- intent: upload_exam_material" or simply cut off after faq_contact_hours if possible.
    
    # Actually, searching for "intent: faq_contact_hours" and then finding the next intent usually works.
    start_tag = "- intent: faq_contact_hours"
    idx = content.find(start_tag)
    
    if idx == -1:
        print("Reference point not found!")
        exit(1)
        
    # Find the end of this block. It ends where the next intent starts (which is upload_exam_material).
    # Since we are restoring from upload_exam_material onwards, we want to cut right before it.
    
    # Let's verify where upload_exam_material starts.
    # If the file is corrupted, the text "upload_exam_material" might be intact (ASCII) but the Greek content inside might be broken.
    # So we should find the start of `faq_contact_hours` and keep it, then find where `upload_exam_material` WOULD be.
    
    # Actually, checking the previous `view_file` (Step 881), `faq_contact_hours` is followed by `upload_exam_material`.
    end_tag = "- intent: upload_exam_material"
    idx_end = content.find(end_tag)
    
    if idx_end != -1:
        print(f"Found cut-off point at {idx_end}. Truncating and appending...")
        # Keep content up to (but not including) upload_exam_material
        final_content = content[:idx_end] + restored_content
    else:
        # If we can't find it (maybe it's corrupted beyond recognition?),
        # we can try to find the end of the last GOOD intent.
        print("Couldn't find upload_exam_material tag. Trying fallback...")
        # Fallback: Find end of faq_contact_hours listing.
        # It ends with empty newlines usually.
        # Let's count indents or look for the last known example line.
        
        # Harder to do reliably. Let's assume the intent TAG itself is preserved because it's english.
        # If "intent: upload_exam_material" is missing, maybe "intent: upload_study_material" is there?
        pass 
        # For now, let's assume we can trigger off the start tag + some offset or just rewrite the file content if we had the FULL file.
        # But we don't have the full file in memory.
        
        # Alternative: Just look for the LAST newline after faq_contact_hours examples.
        # That's risky.
        
        # Let's just find "intent: faq_contact_hours" and iterate lines until we see "intent:" or EOF.
        lines = content.splitlines()
        cut_line = -1
        for i, line in enumerate(lines):
            if line.strip().startswith("- intent: faq_contact_hours"):
                # Fast forward to next intent
                for j in range(i+1, len(lines)):
                     if lines[j].strip().startswith("- intent:"):
                         cut_line = j
                         break
                break
        
        if cut_line != -1:
             print(f"Found cut-off line at {cut_line}")
             final_content = "\\n".join(lines[:cut_line]) + "\\n" + restored_content
        else:
            print("Could not find safe cut-off point.")
            exit(1)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_content)
        
    print("Restore complete.")

except Exception as e:
    print(f"Error: {e}")
