@echo off
"%PREFIX%\python.exe" -I "%PREFIX%\app\packaging\windows\shortcuts.py" remove
exit /b %errorlevel%
