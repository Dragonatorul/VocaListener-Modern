"""Create per-user Start menu links using only built-in Windows facilities."""
import os
from pathlib import Path
import subprocess
import sys

folder = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/VocaListener Modern"
if sys.argv[1] == "remove":
    for name in ["VocaListener Modern.lnk", "User Guide.lnk"]:
        (folder / name).unlink(missing_ok=True)
    if folder.is_dir() and not any(folder.iterdir()):
        folder.rmdir()
else:
    folder.mkdir(parents=True, exist_ok=True)
    os.environ["VOCALISTENER_SHORTCUT_DIR"] = str(folder)
    os.environ["VOCALISTENER_INSTALL_DIR"] = sys.prefix
    script = r'''
    $ErrorActionPreference = 'Stop'
    $shell = New-Object -ComObject WScript.Shell
    $root = $env:VOCALISTENER_INSTALL_DIR
    $link = $shell.CreateShortcut((Join-Path $env:VOCALISTENER_SHORTCUT_DIR 'VocaListener Modern.lnk'))
    $link.TargetPath = Join-Path $root 'VocaListener-Modern.exe'
    $link.WorkingDirectory = $root
    $link.Save()
    $help = $shell.CreateShortcut((Join-Path $env:VOCALISTENER_SHORTCUT_DIR 'User Guide.lnk'))
    $help.TargetPath = Join-Path $root 'app\docs\windows.html'
    $help.Save()
    '''
    powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    subprocess.run([str(powershell), "-NoProfile", "-NonInteractive", "-Command", script], check=True)
