@echo off
"%PREFIX%\python.exe" -I "%PREFIX%\app\packaging\windows\shortcuts.py" install
exit /b %errorlevel%
