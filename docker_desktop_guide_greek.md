# Οδηγός Docker Desktop

Αυτό το έγγραφο εξηγεί τον ρόλο του Docker Desktop στον υπολογιστή σας (Windows) και πώς το χρησιμοποιούμε για να εξομοιώσουμε το περιβάλλον του Server.

---

## 1. Τι είναι το Docker Desktop;

Φανταστείτε το Docker σαν ένα **φορτηγό πλοίο** και την εφαρμογή μας σαν ένα **κοντέινερ (container)**.
*   Μέσα στο κοντέινερ υπάρχει όλο το λογισμικό (Python 3.10, Rasa 3.x, Βιβλιοθήκες) που χρειάζεται το Chatbot.
*   Το **Docker Desktop** είναι το λιμάνι στον υπολογιστή σας που "τρέχει" αυτά τα κοντέινερ.

**Γιατί το χρησιμοποιούμε;**
Εξασφαλίζει ότι το Chatbot θα τρέχει **ακριβώς το ίδιο** στον υπολογιστή σας (Windows) και στον Server (Linux). Αν δουλεύει στο Docker, δουλεύει παντού ("It works on my machine" problem solved).

---

## 2. Βασικές Ρυθμίσεις (Settings) για το Rasa

Το Rasa (Machine Learning) είναι "βαρύ" λογισμικό. Χρειάζεται πόρους.

**Πού θα το ρυθμίσετε:**
1.  Ανοίξτε το Docker Desktop -> Settings (Γρανάζι).
2.  Πηγαίνετε στο **Resources**.
3.  **Memory Limit (RAM):** Βάλτε τουλάχιστον **4 GB** (ιδανικά 6 GB).
    *   *Προσοχή:* Αν το αφήσετε στο Default (2 GB), η εκπαίδευση (`rasa train`) θα αποτύχει με "OOM Killed" (Out of Memory).
4.  **Swap:** Αυξήστε το στο 1 GB.

---

## 3. Διαχείριση Αρχείων (Volumes)

Το Docker είναι "κλειστό κουτί". Για να επιβιώσουν τα αρχεία μας (και να τα βλέπουμε εμείς στα Windows), χρησιμοποιούμε **Volumes (Καθρέφτες)**.

Στο `docker-compose.yml`, έχουμε ορίσει:

| Windows Φάκελος | Docker Φάκελος | Χρήση |
| :--- | :--- | :--- |
| `./data` | `/app/data` | Περιέχει την `questions.db` και τα μοντέλα του Rasa. |
| `./files` | `/app/files` | Εδώ σώζονται τα Uploaded Word docs και τα Generated PDFs. |
| `./fonts` | `/app/fonts` | Περιέχει τη γραμματοσειρά `DejaVuSans.ttf` για τα Ελληνικά PDF. |

*Τι σημαίνει αυτό:* Αν σβήσετε ένα αρχείο από το `files/` στα Windows, σβήνεται και από το Chatbot.

---

## 4. Ροή Εργασίας (Workflow) & Troubleshooting

### Πότε κάνω τι;
1.  **Άλλαξα κείμενα (Responses/Stories):**
    *   Χρειάζεται επανεκπαίδευση: `docker-compose run rasa train`.
    *   Μετά: `docker-compose up -d`.
2.  **Άλλαξα κώδικα Python (`actions.py`):**
    *   Πρέπει να ξαναχτιστεί το Image:
    *   `docker-compose up -d --build` (Προσθέστε το `--force-recreate` αν κολλήσει).

### Χρήσιμες Εντολές (Terminal)
*   `docker ps`: Δείχνει ποια κοντέινερ τρέχουν.
*   `docker-compose logs -f action-server`: Δείχνει ζωντανά τα λάθη στον κώδικα Python.
*   `docker system prune`: **ΠΡΟΣΟΧΗ!** Καθαρίζει παλιά αρχεία και ελευθερώνει χώρο στον δίσκο.

---

## 5. Το Περιβάλλον Containers (GUI)

Στην καρτέλα **Containers** του Docker Desktop, θα δείτε το `rasa-school-chatbot-v2`. Περιέχει:
1.  `rasa`: Ο εγκέφαλος.
2.  `action-server`: Τα χέρια (Custom Python Code).
3.  `nginx`: Η πόρτα (Web Server).
4.  `certbot`: Η ασφάλεια (SSL).

Αν κάποιο έχει **κόκκινο τετράγωνο**, κάντε κλικ πάνω του και δείτε την καρτέλα **Logs** για να βρείτε το σφάλμα (π.χ. "Port already in use" ή "File not found").
