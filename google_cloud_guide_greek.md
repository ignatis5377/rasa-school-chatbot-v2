# Οδηγός Μεταφοράς στο Google Cloud (Deployment)

Ακολουθήστε αυτά τα βήματα ακριβώς για να ενημερώσετε τον Server σας.

---

## Μέρος 1: Ανέβασμα κώδικα (GitHub Desktop) 🖥️

Επειδή είχατε δυσκολία με τις εντολές, θα χρησιμοποιήσουμε το γραφικό περιβάλλον.

1.  Ανοίξτε το **GitHub Desktop**.
2.  Πηγαίνετε: **File** -> **Add Local Repository**.
3.  Επιλέξτε τον φάκελο `C:\RasaFinalProject` και πατήστε **Add Repository**.
4.  Θα δείτε μια αλλαγή "Deployment Update..." (ή παρόμοιο). Πατήστε **Commit to main**.
5.  Πατήστε το κουμπί **Push origin** (πάνω δεξιά) για να ανέβει στο Cloud.
    *   *Σημείωση:* Αν σας ζητήσει όνομα, δώστε `rasa-bot` και πατήστε Publish. Βεβαιωθείτε ότι ξε-τσεκάρατε το "Keep this code private" αν θέλετε να είναι δημόσιο.

---

## Μέρος 2: Ενημέρωση Server (Google Cloud Console) ☁️

1.  Μπείτε στο **Google Cloud Console**.
2.  Πηγαίνετε: **Compute Engine** -> **VM instances**.
3.  Βρείτε το μηχάνημα `rasa-server` (IP: `104.155.53.205`).
4.  Πατήστε το κουμπί **SSH** (στα δεξιά). Θα ανοίξει ένα μαύρο παράθυρο στον Browser.

### Μέσα στο μαύρο παράθυρο (SSH):
Εκτελέστε τις παρακάτω εντολές (μία-μία).

**Βήμα 1: Μετάβαση στον Φάκελο**
```bash
cd rasa-school-chatbot-v2
```
*(Αν ο φάκελος δεν υπάρχει -πράγμα σπάνιο-, τρέξτε πρώτα: `git clone https://github.com/ignatis5377/rasa-school-chatbot-v2.git`)*

**Βήμα 2: Κατέβασμα Αλλαγών**
```bash
git pull
```
*(Αν κολλήσει και ζητάει κωδικό, δείτε την "Αντιμετώπιση Προβλημάτων" παρακάτω)*

**Βήμα 3: Επανεκκίνηση & Build**
Αυτό θα ξαναχτίσει τα containers με τις νέες βιβλιοθήκες και ρυθμίσεις.
```bash
sudo docker-compose down
sudo docker-compose up -d --build --force-recreate
```

> **⚠️ ΠΡΟΣΟΧΗ ΣΤΟ IP:**
> Πριν τρέξετε το `docker-compose up`, ελέγξτε αν το External IP του server έχει αλλάξει (μέσα στο Google Cloud Console). Αν δεν είναι πια `104.155.53.205`, πρέπει να ενημερώσετε το αρχείο `nginx/conf.d/default.conf`:
> `nano nginx/conf.d/default.conf` (και αλλάξτε το IP).

---

## Μέρος 3: Τελικός Έλεγχος & Σύνδεση ✅

1.  Περιμένετε **5 λεπτά** να τελειώσει το "Build" και να σηκωθεί ο Rasa Server.
2.  Ανοίξτε το site σας: [https://ignatislask.sites.sch.gr/](https://ignatislask.sites.sch.gr/).
3.  Ελέγξτε αν το widget εμφανίζεται και απαντάει.

---

## Αντιμετώπιση Προβλημάτων (Troubleshooting) 🔧

### 1. Πρόβλημα "Permission denied" (PDF/Create Exam)
Αν το Chatbot πει "Permission denied" όταν φτιάχνει PDF ή δεν αποθηκεύει ερωτήσεις.
**Λύση:**
```bash
# Δίνουμε δικαιώματα σε ΟΛΟΥΣ τους κρίσιμους φακέλους (Data + Files)
sudo chmod -R 777 data files
```
*Αυτό επιτρέπει στον Docker User (1001) να γράφει στη βάση δεδομένων.*

### 2. Πρόβλημα Σύνδεσης (Password Authentication)
Αν στο `git pull` σας ζητάει Username/Password:
*   **Λύση:** Κάντε το Repository **Public** από τα Settings στο GitHub site. Έτσι δεν θα ζητάει κωδικούς.
*   **Εναλλακτικά:** Username = GitHub User, Password = Personal Access Token (όχι ο κωδικός σας).

### 3. Πρόβλημα Docker (KeyError / Version Issue)
Αν δείτε σφάλμα `KeyError: 'ContainerConfig'` ή παλιά έκδοση Docker.
**Λύση:**
```bash
sudo curl -SL https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo docker-compose up -d --build
```

### 4. Πρόβλημα SSL (Connection Refused)
Αν το site δεν ανοίγει (HTTPS Error) ή λέει "cannot load certificate".
**Λύση:**
```bash
# 1. Σταματάμε τον Web Server
sudo docker-compose stop nginx

# 2. Τρέχουμε το Certbot για ανανέωση (Βεβαιωθείτε για το IP!)
sudo docker run -it --rm --name certbot \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  -p 80:80 \
  certbot/certbot certonly --standalone -d 104.155.53.205.nip.io

# 3. Ξεκινάμε πάλι
sudo docker-compose restart nginx
```

### 5. Προβολή Logs (Για Errors του Chatbot)
Αν το bot απαντάει "Something went wrong", δείτε τι φταίει (π.χ. WordPress Error):
```bash
sudo docker-compose logs -f action-server
```

### 7. Πρόβλημα "Expired Key" στο SSH
Αν δείτε μήνυμα "invalid ssh key entry - expired key":
*   Η Google δημιουργεί προσωρινά κλειδιά που λήγουν γρήγορα.
*   **Λύση:** Κλείστε τελείως το μαύρο παράθυρο SSH και πατήστε ξανά το κουμπί **SSH**.
*   **Λύση 2:** Αν επιμένει, κάντε **Reset** (Επανεκκίνηση) στο VM από το κουμπί "Reset" πάνω στην μπάρα του Google Cloud Console.

### 8. Πρόβλημα "Bad Permissions" στο Κλειδί (Windows)
Αν δείτε μήνυμα `WARNING: UNPROTECTED PRIVATE KEY FILE!`, σημαίνει ότι τα Windows δίνουν πρόσβαση σε πολλούς χρήστες στο αρχείο κλειδιού.
**Λύση (PowerShell):**
Τρέξτε αυτές τις εντολές στο PowerShell για να διορθώσετε τα δικαιώματα:
```powershell
# 1. Μετάβαση στο φάκελο .ssh
cd $env:USERPROFILE\.ssh

# 2. Αφαίρεση όλων των δικαιωμάτων
icacls google_compute_engine /inheritance:r

# 3. Ανάθεση δικαιωμάτων ΜΟΝΟ στον χρήστη σας
icacls google_compute_engine /grant:r "$($env:USERNAME):(R)"
```

### 6. Εναλλακτική Πρόσβαση στο Admin App (Χωρίς SSH Tunnel)
Αν σας δυσκολεύει το SSH Tunneling για να δείτε το Admin App (`streamlt`), μπορείτε να ανοίξετε την πόρτα 8501 στο Firewall.

1.  Πηγαίνετε στο **Google Cloud Console** -> **VPC network** -> **Firewall**.
2.  Πατήστε **Create Firewall Rule**.
3.  Ονομάστε το `allow-streamlit`.
4.  Στο **Targets**, επιλέξτε "All instances in the network".
5.  Στο **Source IPv4 ranges**, βάλτε `0.0.0.0/0` (ή μόνο την IP του σπιτιού σας για ασφάλεια).
6.  Στο **Protocols and ports**, τσεκάρετε το **tcp** και γράψτε `8501`.
7.  Πατήστε **Create**.

Τώρα μπορείτε να μπείτε απευθείας από τον browser σας:
`http://104.155.53.205:8501`
