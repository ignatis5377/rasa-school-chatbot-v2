# Ο Απόλυτος Οδηγός Εγκατάστασης Σχολικού Chatbot ("The Master Guide")

Αυτό το έγγραφο αποτελεί τον πλήρη, βήμα-προς-βήμα οδηγό για το στήσιμο του συστήματος από το μηδέν. Απευθύνεται σε τεχνικούς που θέλουν να αναπαράγουν ακριβώς την υποδομή μας.

---

## Φάση 1: Προετοιμασία & Τοπική Ανάπτυξη ("The Brain")

Πριν βγούμε στο ίντερνετ, χτίσαμε το "μυαλό" του Chatbot τοπικά.

### 1. Stack
*   **Python (3.10) & Rasa (3.x):** Ο πυρήνας.
*   **VS Code:** IDE.
*   **Git:** Version Control.

### 2. Ανάπτυξη Λογικής (Actions)
Στο `actions/actions.py`:
*   **Word Parser:** Αναλύει `.docx` αρχεία (Ερωτήσεις/Απαντήσεις) και εξάγει εικόνες.
*   **PDF Generator:** Χρησιμοποιεί το `reportlab` (με γραμματοσειρά **DejaVuSans**) για να φτιάχνει διαγωνίσματα με Inline Answers.
*   **Search Integration:** Συνδέει το bot με το **WordPress REST API** για αναζήτηση άρθρων.
*   **Search Integration:** Συνδέει το bot με το **WordPress REST API** για αναζήτηση άρθρων.
*   **Fallback Logic:** Μετράει τις αποτυχημένες προσπάθειες και κάνει reset μετά από 3 λάθη.

### 3. Διαχείριση (Backend)
*   **Admin App (`admin_app.py`):** Εφαρμογή Streamlit για άμεση εποπτεία της βάσης δεδομένων. Επιτρέπει φιλτράρισμα, αναζήτηση και προεπισκόπηση ερωτήσεων.

---

## Φάση 2: Containerization ("The Box")

Κλείσαμε τα πάντα σε Docker Containers για φορητότητα.

### 1. Τα Αρχεία Docker
*   **`Dockerfile`:** Εγκαθιστά Python βιβλιοθήκες και εξασφαλίζει ότι το `DejaVuSans.ttf` είναι στη σωστή θέση (`/app/fonts/`) για να μην σπάνε τα PDF.
*   **`docker-compose.yml`:** Σηκώνει **5 υπηρεσίες**: Rasa, Action Server, Nginx, Certbot, και **Admin App**.

### 2. Volumes
Ορίσαμε μόνιμους τόμους για να μην χάνονται τα αρχεία:
*   `./data:/app/data` (Βάση Δεδομένων & Rasa Models)
*   `./files:/app/files` (Uploaded Docs & Generated PDFs)

---

## Φάση 3: Το Σύννεφο (Google Cloud Platform)

### 1. Server Setup
*   **VM Instance:** Ubuntu 20.04 (e2-medium, 4GB RAM).
*   **Static IP:** Για σταθερή σύνδεση.
*   **Firewall:** Ανοίξαμε ports 80 (HTTP), 443 (HTTPS), 22 (SSH).

---

## Φάση 4: Εγκατάσταση στον Server (Deployment)

### 1. Εργαλεία
```bash
sudo apt update
sudo apt install docker.io docker-compose git
```

### 2. Permissions Fix (ΚΡΙΣΙΜΟ)
Για να μπορεί ο Docker Container να γράφει στη βάση δεδομένων (`questions.db`) και να σώζει εικόνες, έπρεπε να δώσουμε δικαιώματα στον φάκελο:
```bash
sudo chmod -R 777 data files
```
*Χωρίς αυτό, παίρνουμε "Read-only database error".*

### 3. Εκκίνηση
```bash
sudo docker-compose up -d --build --force-recreate
```

---

## Φάση 5: Ασφάλεια & Ιστός (Web Layer)

### 1. Nginx & SSL
*   Σερβίρουμε τα στατικά αρχεία (`/files/...`) μέσω Nginx.
*   Χρησιμοποιούμε **Certbot** για δωρεάν SSL (HTTPS).

### 2. WordPress Integration (Frontend)
Προσθέσαμε το Webchat Widget στο `footer.php` του σχολικού site.
*   **Payload Script:** Διαβάζει αν ο χρήστης είναι Admin/Member/Guest.
*   **Role-Based Greeting:** Το Bot ξεκινάει τη συζήτηση προσαρμοσμένα ("Καλώς ήρθατε κ. Καθηγητά" vs "Γεια σου μαθητή").

---

## Συμπέρασμα

Στήσαμε ένα πλήρες, μοντέρνο σύστημα DevOps:
*   **Code:** Python/Rasa με σύνθετη λογική (Search, PDF, Parsing).
*   **Infrastructure:** Docker/GCP με σωστά Permissions και Volumes.
*   **Security:** Nginx/SSL και Role-Based Access Control.
*   **UX:** Fallback mechanisms και Smart Search.

Το σύστημα είναι αυτόνομο, ασφαλές και έτοιμο για χρήση!
