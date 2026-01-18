# Οδηγός Εκπαίδευσης Rasa Chatbot

Αυτό το έγγραφο εξηγεί πώς μαθαίνουμε στο Chatbot νέα πράγματα, από απλές ερωτήσεις μέχρι σύνθετες ροές όπως η Αναζήτηση, οι Ρόλοι και η Διαχείριση Λαθών.

---

## 1. Τα "Τετράδια" του Chatbot

Το Rasa μαθαίνει από τρία βασικά αρχεία:

1.  **`data/nlu.yml` (Κατανόηση):** Μαθαίνουμε στο Bot *τι λέει* ο χρήστης (Intents) και *τι σημαντικές λέξεις* περιέχει (Entities).
2.  **`data/stories.yml` (Ροή):** Μαθαίνουμε στο Bot *πώς να κάνει διάλογο* με βάση το ιστορικό.
3.  **`domain.yml` (Λεξικό):** Ορίζουμε όλες τις απαντήσεις (`utter_`), τις προθέσεις (`intents`), τα κενά μνήμης (`slots`) και τις φόρμες.

---

## 2. Πώς προσθέτω νέα γνώση; (Case Studies)

### Περίπτωση A: Απλή Ερώτηση vs Smart FAQ
*   **Static (Απλό):** Αν θέλετε μια σταθερή απάντηση, συνδέστε το Intent με ένα `utter_...` στο `rules.yml`.
*   **Smart (Υβριδικό):** Στο project μας, χρησιμοποιούμε το `action_smart_faq`.
    *   *Τι κάνει:* Δίνει μια σύντομη απάντηση ΚΑΙ ψάχνει στο Site για λεπτομέρειες.
    *   *Rules:* Intent: `faq_absences` -> Action: `action_smart_faq`.

### Περίπτωση B: Σύνθετη Ενέργεια (Search) -> Entities
Αν θέλετε το Bot να πιάσει *τι* ψάχνει ο χρήστης.
*   **nlu.yml:**
    ```yaml
    - intent: search_website
      examples: |
        - ψάχνω για [εκδρομή](query)
        - βρες μου άρθρα για [εξετάσεις](query)
    ```
    *Εδώ το `[εκδρομή](query)` λέει στο Bot: "Κράτα τη λέξη 'εκδρομή' στη μνήμη, στο κουτάκι (entity) 'query'"*.

### Περίπτωση Γ: Ρόλοι & Μνήμη (Slots)
Πώς θυμάται το Bot αν είστε Μαθητής ή Καθηγητής; Με τα **Slots**.
*   **domain.yml:**
    ```yaml
    slots:
      role:
        type: text
        mappings:
        - type: from_entity
          entity: role
    ```
*   **nlu.yml:**
    ```yaml
    - intent: inform_role
      examples: |
        - είμαι [μαθητής](role)
        - [εκπαιδευτικός](role)
    ```

### Περίπτωση Δ: Διαχείριση Λαθών (Fallback) -> Stories
Αν θέλετε το Bot να δίνει ευκαιρίες πριν παραιτηθεί (Reset).
*   **stories.yml:**
    ```yaml
    - story: User fails twice then reset
      steps:
      - intent: nlu_fallback
      - action: utter_please_repeat  # 1η φορά
      - intent: nlu_fallback
      - action: utter_please_repeat  # 2η φορά
      - intent: nlu_fallback
      - action: utter_default        # 3η φορά -> Reset
      - action: action_restart
    ```

---

## 3. Η Διαδικασία Εκπαίδευσης (Workflow)

Εδώ γίνεται συχνά μπέρδεμα. Υπάρχουν δύο είδη αλλαγών:

### Α. Άλλαξα Δεδομένα (yml αρχεία)
Αν αλλάξατε `nlu.yml`, `stories.yml` ή `domain.yml`:
1.  Τρέξτε:
    ```bash
    sudo docker-compose run rasa train
    ```
2.  Μετά κάντε restart για να φορτώσει το νέο μοντέλο:
    ```bash
    sudo docker-compose restart rasa
    ```

### Β. Άλλαξα Κώδικα Python (`actions.py`)
Αν αλλάξατε τη λογική (π.χ. πώς φτιάχνεται το PDF ή πώς μιλάει με το WordPress):
1.  Το `rasa train` **ΔΕΝ** αρκεί.
2.  Πρέπει να ξαναχτιστεί το Image:
    ```bash
    sudo docker-compose up -d --build --force-recreate
    ```

---

## 4. Χρήσιμα Tips
*   **Confusion Matrix:** Αν το bot μπερδεύει δύο intents (π.χ. "Γεια" με "Αντίο"), προσθέστε περισσότερα παραδείγματα στο NLU που να τα ξεχωρίζουν.
*   **Interactive Learning:** Χρησιμοποιήστε το `rasa interactive` στον υπολογιστή σας για να διορθώνετε το bot ενώ μιλάτε και να δημιουργείτε αυτόματα Stories.
