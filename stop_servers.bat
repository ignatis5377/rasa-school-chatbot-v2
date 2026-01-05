@echo off
echo Stopping all Rasa/Python processes...
taskkill /F /IM python.exe
taskkill /F /IM ras.exe
echo Done. You can now start the servers again.
pause
