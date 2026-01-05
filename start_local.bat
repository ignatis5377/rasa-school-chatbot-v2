@echo off
echo Starting Rasa servers for local testing...

:: 1. Start Action Server in a new window
echo Starting Action Server...
start "Rasa Action Server" cmd /k "rasa run actions -p 5056"

:: 2. Start Rasa Core with API and CORS enabled in a new window
echo Starting Rasa Core with API...
echo Please wait for "Rasa server is up and running" message.
start "Rasa Core Server" cmd /k "rasa run --enable-api --cors "*" --debug"

echo Done! Please wait approx 30 seconds for servers to boot.
pause
