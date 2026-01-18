# Οδηγός Ενσωμάτωσης στο WordPress (Τελικό Βήμα)

Για να δουλεύει η ασφάλεια σωστά και να μην μπλέκουμε με PHP μέσα στα Widgets, χρησιμοποιούμε τη λύση "PHP in Snippets + JS in Footer".

---

### Βήμα 1: Το "Παρασκήνιο" (PHP - Ταυτοποίηση Ρόλων)

Χρησιμοποιούμε το Plugin **Code Snippets** για να περάσουμε τον ρόλο του χρήστη από το WordPress στη Javascript.

**Κώδικας (Snippet):**
```php
function add_chatbot_user_data() {
    $current_user = wp_get_current_user();
    
    // Default Role
    $rasa_role = 'guest';
    
    // Αν είναι συνδεδεμένος, βρίσκουμε τον ακριβή ρόλο
    if ( is_user_logged_in() ) {
        if ( in_array( 'administrator', (array) $current_user->roles ) ) {
            $rasa_role = 'administrator';
        } elseif ( in_array( 'editor', (array) $current_user->roles ) || in_array( 'author', (array) $current_user->roles ) ) {
            // Θεωρούμε τους Editors/Authors ως Εκπαιδευτικούς
            $rasa_role = 'teacher'; 
        } else {
            // Όλοι οι άλλοι (Subscribers) είναι Μαθητές/Γονείς
            $rasa_role = 'student'; 
        }
    }

    $username = is_user_logged_in() ? $current_user->user_login : '';

    // Περνάμε τα δεδομένα στη Javascript
    echo "<script>
        window.rasaUserRole = '$rasa_role';
        window.rasaUserName = '$username';
        console.log('WP Role Detection:', '$rasa_role');
    </script>";
}
add_action('wp_footer', 'add_chatbot_user_data', 5);
```
*Πάτα "Run Everywhere" στο Snippet.*

---

### Βήμα 2: Το Widget (Javascript - Σύνδεση με Chatbot)

Αυτός είναι ο κώδικας που μπαίνει στο **Custom HTML Widget** (ή στο `footer.php` μέσω του theme).

**Κώδικας:**
```html
<script>
  (function () {
    // 1. Καθαρισμός Μνήμης (Optional - για να μην κολλάει παλιά session)
    // localStorage.clear(); 
    
    let e = document.createElement("script"),
      t = document.head || document.getElementsByTagName("head")[0];
    e.src = "https://cdn.jsdelivr.net/npm/rasa-webchat@1.0.1/lib/index.js";
    e.async = !0;
    e.onload = () => {
      
      // 2. Ανάγνωση Ρόλου από PHP
      const userRole = window.rasaUserRole || 'guest';
      const userName = window.rasaUserName || '';
      
      // 3. Δυναμικό Payload
      // Στέλνουμε το /greet με metadata για να κάνει trigger το σωστό χαιρετισμό
      let payload = "/greet";
      if (userRole !== 'guest') {
          payload += '{"role":"' + userRole + '", "username":"' + userName + '"}';
      }

      // 4. Εμφάνιση Τίτλου
      let titleText = "Σχολικός Βοηθός";
      if (userRole === 'administrator') titleText += " (Admin Mode)";
      if (userRole === 'teacher') titleText += " (Teacher Mode)";

      window.WebChat.default(
        {
          initPayload: payload,
          socketUrl: "https://104.155.53.205.nip.io", // Η διεύθυνση του Server μας
          customData: { 
              "role": userRole, 
              "username": userName,
              "language": "el"
          },
          title: titleText,
          subtitle: userRole !== 'guest' ? "Γεια σου " + userName + "!" : "Συνδεθείτε για περισσότερα",
          params: {
              storage: "session"
          }
        },
        null
      );
    };
    t.insertBefore(e, t.firstChild);
  })();
</script>
```

---

### Τι πετύχαμε:

1.  **Guest:** Βλέπει απλό χαιρετισμό. Αν ζητήσει upload/exam, τρώει "πόρτα".
2.  **Student (Subscriber):** Το Chatbot τον αναγνωρίζει ("Γεια σου Γιώργο!") και επιτρέπει Διαγωνίσματα.
3.  **Teacher (Editor):** Το Chatbot επιτρέπει **ΚΑΙ** το "Ανέβασμα Υλικού".
4.  **Admin:** Full access.

*Σημείωση:* Η αναζήτηση άρθρων (Search) δουλεύει για όλους, καθώς γίνεται από την πλευρά του Server (Python) και όχι από τον Browser.
