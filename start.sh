#!/bin/bash

# Ορίζουμε τη θύρα του Core Server (χρησιμοποιούμε τη μεταβλητή PORT του Cloud Run)
RASA_CORE_PORT=${PORT:-5005}
# Ορίζουμε τη θύρα του Action Server (εσωτερικά)
RASA_ACTIONS_PORT=5055

# 1. (Removed) Action Server runs in separate container

# 2. Ξεκινάει τον Core Server ως την κύρια διεργασία (exec)
# Πρέπει να ακούει στη μεταβλητή PORT ($RASA_CORE_PORT) και σε 0.0.0.0
exec rasa run --enable-api --cors "*" --port $RASA_CORE_PORT -i 0.0.0.0 --credentials credentials.yml --endpoints endpoints.yml --model models