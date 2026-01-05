@echo off
echo ==========================================
echo FORCE CLEANING AND RETRAINING MODEL
echo ==========================================

echo Deleting old models...
del /Q models\*.tar.gz

echo Training NEW model...
call rasa train --force

echo Training Complete. Starting Servers...
echo PLEASE WAIT 30 SECONDS AFTER THIS STARTS.

start_local.bat
