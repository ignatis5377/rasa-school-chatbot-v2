# Οδηγός GitHub και Δομής Έργου

Αυτός ο οδηγός εξηγεί τον ρόλο του GitHub στο έργο, πώς είναι οργανωμένα τα αρχεία και πού βρίσκονται τα κρίσιμα δεδομένα και οι ρυθμίσεις.

---

## 1. Γιατί χρησιμοποιούμε το GitHub;

Στο έργο μας, το GitHub δεν είναι απλά ένας χώρος αποθήκευσης (Backup). Εξυπηρετεί τρεις κρίσιμους ρόλους:

1.  **Συγχρονισμός (Deployment):** Είναι η "γέφυρα" ανάμεσα στον υπολογιστή ανάπτυξης (Local) και τον Server (Cloud/Linux). Όταν γράφουμε κώδικα τοπικά, τον στέλνουμε στο GitHub (`git push`) και μετά ο Server τον κατεβάζει (`git pull`).
2.  **Ιστορικό (Version Control):** Κρατάει αρχείο για κάθε αλλαγή. Αν κάτι χαλάσει, μπορούμε να γυρίσουμε πίσω στον χρόνο (Revert).
3.  **Συνεργασία:** Επιτρέπει σε πολλούς προγραμματιστές να δουλεύουν ταυτόχρονα.

---

## 2. Η Δομή των Αρχείων (Πού είναι τι;)

Όταν ανοίγετε τον φάκελο του έργου, θα δείτε τα εξής βασικά αρχεία και φακέλους:

### Α. Ο "Εγκέφαλος" του Chatbot (Rasa)
*   **`data/`:** Εδώ βρίσκονται τα δεδομένα εκπαίδευσης.
    *   `nlu.yml`: Τι καταλαβαίνει το bot (Προθέσεις/Φράσεις με νέα intents όπως `create_exam`, `search_website`).
    *   `rules.yml` & `stories.yml`: Πώς πρέπει να απαντάει (π.χ. Fallback Stories, Role-based paths).
    *   **`questions.db`:** Η βάση και οι ερωτήσεις. *Συχνά εξαιρείται από το Git.*
*   **`domain.yml`:** Το "λεξικό" του bot. Εδώ ορίζονται όλες οι απαντήσεις (responses), οι υποδοχές μνήμης (slots) και οι φόρμες.
*   **`config.yml`:** Οι τεχνικές ρυθμίσεις του μοντέλου AI (Pipeline, Policies).

### Β. Η Λογική & Ο Κώδικας (Python - `actions/`)
*   **`actions.py`:** **Το πιο σημαντικό αρχείο.** Περιέχει:
    *   `extract_questions_from_docx`: Parser για αρχεία Word.
    *   `ActionCreateExamNew`: Γεννήτρια PDF με ReportLab.
    *   `ActionSearchArticles`: Σύνδεση με WordPress API.
    *   `ActionHandleFallback`: custom fallback logic.
*   **`fonts/`:** Φάκελος που περιέχει την ελληνική γραμματοσειρά `DejaVuSans.ttf`.

### Γ. Υποδομή & Ρυθμίσεις Server
*   **`docker-compose.yml`:** Ορίζει τα services: `rasa`, `action-server`, `nginx`, `certbot`.
*   **`Dockerfile`:** Χτίζει το image του Action Server, εγκαθιστώντας βιβλιοθήκες (`reportlab`, `python-docx`).
*   **`credentials.yml`:** (SECRET) Κωδικοί διασύνδεσης.
*   **`endpoints.yml`:** Συνδέει το Rasa με τον Action Server.

---

## 3. Διαχείριση Files & Volumes (Docker)
Έχουμε ρυθμίσει ειδικούς "τόμους" (volumes) για να μην χάνονται δεδομένα όταν επανεκκινεί ο server:

1.  **`files/`**: Εδώ αποθηκεύονται τα Uploaded Docs και τα Generated PDFs.
    *   Στο `docker-compose.yml`, γίνεται mount ως: `./files:/app/files`.
2.  **`data/`**: Εδώ ζει η βάση δεδομένων `questions.db`.
    *   Mounted ως: `./data:/app/data`.
3.  **`fonts/`**: Οι γραμματοσειρές γίνονται mount για να τις βλέπει το ReportLab.

---

## 4. Ροή Εργασίας (Workflow) για Αλλαγές

Αν θέλετε να αλλάξετε κάτι (π.χ. το όνομα της βάσης ή ένα path):
1.  Ανοίγετε το αρχείο `actions/actions.py` (για λογική) ή `docker-compose.yml` (για υποδομή).
2.  Κάνετε την αλλαγή και δοκιμάζετε τοπικά (αν είναι εφικτό).
3.  Τρέχετε:
    ```bash
    git add .
    git commit -m "Περιγραφή αλλαγής"
    git push
    ```
4.  Στον Server (SSH):
    ```bash
    git pull
    # Αν αλλάξατε Python κώδικα ή Dockerfile:
    sudo docker-compose up -d --build --force-recreate
    # Αν αλλάξατε μόνο Rasa data:
    sudo docker-compose run rasa train
    ```

---

## 5. Συμπέρασμα
Το GitHub περιέχει τον **Κώδικα** και τη **Δομή**.
Ο Server περιέχει τα **Δεδομένα** (Βάση & Αρχεία) και την **Εκτέλεση**.
Γι' αυτό προσέχουμε πάντα να μην κάνουμε `git push` αρχεία βάσης (database) από τον υπολογιστή μας, αν δεν θέλουμε να διαγράψουμε αυτά του Server!
