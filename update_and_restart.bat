@echo off
echo Installing new requirements for Word and Images...
pip install python-docx pillow

echo.
echo Restarting Servers...
call start_local.bat
