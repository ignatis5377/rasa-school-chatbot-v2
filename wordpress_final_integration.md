# Οδηγός Ενσωμάτωσης στο WordPress (Τελικό Βήμα)

Για να δουλεύει η ασφάλεια σωστά και να μην μπλέκουμε με PHP μέσα στα Widgets (που συχνά δεν δουλεύει), θα το κάνουμε σε **2 βήματα**.

### Βήμα 1: Το "Παρασκήνιο" (PHP)
Το WordPress δεν σε αφήνει να πειράξεις το `functions.php` για ασφάλεια. Κανένα πρόβλημα!
Θα χρησιμοποιήσουμε ένα **Plugin** (Πρόσθετο) που είναι ο σωστός και ασφαλής τρόπος.

1.  Στο μενού αριστερά, πήγαινε **Πρόσθετα (Plugins)** -> **Νέο Πρόσθετο (Add New)**.
2.  Ψάξε για το πρόσθετο: **Code Snippets** (ή "WPCode").
3.  Κάνε **Εγκατάσταση** και **Ενεργοποίηση**.
4.  Τώρα θα δεις ένα νέο μενού **Snippets** αριστερά. Πήγαινε **Snippets** -> **Add New**.
5.  Δώσε τίτλο (π.χ. "Rasa Chatbot User Data") και βάλε τον κώδικα:

```php
function add_chatbot_user_data() {
    $current_user = wp_get_current_user();
    $role = is_user_logged_in() ? 'member' : 'guest';
    $username = is_user_logged_in() ? $current_user->user_login : '';

    echo "<script>
        window.rasaUserRole = '$role';
        window.rasaUserName = '$username';
    </script>";
}
add_action('wp_footer', 'add_chatbot_user_data', 5);
```
6.  Πάτα **Save Changes and Activate**.

*Αυτό ήταν! Τώρα η πληροφορία περνάει στο site χωρίς να χαλάσουμε τίποτα.*

---

### Βήμα 2: Το Widget (Javascript)
Τώρα που η πληροφορία υπάρχει στη μνήμη (`window.rasaUserRole`), το Widget απλά τη διαβάζει.

**Πού το βάζω;**
Εκεί που έβαλες και το προηγούμενο script (στο Widget/HTML block). Σβήσε το παλιό και βάλε αυτό:

```html
<script>
  (function () {
    // 1. Καθαρισμός Μνήμης (ΓΙΑ ΝΑ ΞΕΚΙΝΑΕΙ ΑΠΟ ΤΗΝ ΑΡΧΗ)
    // Σβήνουμε ό,τι θυμάται ο Browser για το Chatbot
    localStorage.clear();
    sessionStorage.clear();

    let e = document.createElement("script"),
      t = document.head || document.getElementsByTagName("head")[0];
    e.src = "https://cdn.jsdelivr.net/npm/rasa-webchat@1.0.1/lib/index.js";
    e.async = !0;
    e.onload = () => {
      // 2. Debugging: Τι βλέπει ο Browser;
      const userRole = window.rasaUserRole || 'guest';
      const userName = window.rasaUserName || '';
      
      console.log("-----------------------------------------");
      console.log("🤖 RASA DEBUG INFO:");
      console.log("User Role:", userRole);
      console.log("User Name:", userName);
      console.log("-----------------------------------------");

      // 3. Κατασκευή του "Μυστικού Μηνύματος" (Payload)
      // Αντί για σκέτο "Γεια", στέλνουμε "Γεια{είμαι: μέλος}"
      // 3. Κατασκευή του "Μυστικού Μηνύματος" (Payload)
      // Στέλνουμε την ταυτότητα "καρφωτά" μέσα στο πρώτο μήνυμα για να την πιάσει σίγουρα το Bot.
      // Π.χ. "/greet{'role':'member', 'username':'Ignatis'}"
      let payload = "/greet";
      if (userRole === 'member') {
          payload += '{"role":"member", "username":"' + userName + '"}';
      }

      window.WebChat.default(
        {
          initPayload: payload,
          socketUrl: "https://104.155.53.205.nip.io",
          customData: { 
              "role": userRole, 
              "username": userName
          },
          title: "Ο Βοηθός του Σχολείου",
          subtitle: userRole === 'member' ? "Γεια σου " + userName + "!" : "Συνδεθείτε για λειτουργίες",
          params: {
              storage: "session" // Προσπάθεια να μην κρατάει μνήμη
          }
        },
        null
      );
    };
    t.insertBefore(e, t.firstChild);
  })();
</script>
```

### Τι πετύχαμε:
1.  Αν είσαι Guest -> `role: 'guest'` -> Το Bot απαγορεύει τα διαγωνίσματα.
2.  Αν είσαι Login -> `role: 'member'` -> Το Bot επιτρέπει τα πάντα!

Δοκίμασέ το:
1.  Μπες ως guest -> ζήτα διαγώνισμα (πρέπει να φας "πόρτα").
2.  Κάνε Login -> ζήτα διαγώνισμα (πρέπει να δουλέψει).

