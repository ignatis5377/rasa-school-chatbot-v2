@echo off
echo Killing all Python and Rasa processes...
taskkill /F /IM python.exe /T
taskkill /F /IM rasa.exe /T
echo All processes killed. You can now restart the servers.
pause
