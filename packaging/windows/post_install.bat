@echo off
copy /Y "%PREFIX%\app\utf8-runtime\python.exe" "%PREFIX%\python.exe" >nul
if errorlevel 1 exit /b 1
copy /Y "%PREFIX%\app\utf8-runtime\pythonw.exe" "%PREFIX%\pythonw.exe" >nul
if errorlevel 1 exit /b 1
copy /Y "%PREFIX%\app\patches\mfa_alignment_base.py" "%PREFIX%\Lib\site-packages\montreal_forced_aligner\alignment\base.py" >nul
if errorlevel 1 exit /b 1
"%PREFIX%\python.exe" -I "%PREFIX%\app\packaging\windows\shortcuts.py" install
exit /b %errorlevel%
