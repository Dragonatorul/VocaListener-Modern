"""Exercise the installed wizard and all five real processing steps offline."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument("--prefix", type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.prefix / "app/src"))
from runtime import configure_runtime, data_directory, model_paths
configure_runtime()
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from vocalistener_gui import VocalListenerModern

directory = data_directory()
directory.mkdir(parents=True, exist_ok=True)
fixture = directory / "hello.wav"
os.environ["VOCALISTENER_FIXTURE"] = str(fixture)
powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
subprocess.run([str(powershell), "-NoProfile", "-Command", '''
    $ErrorActionPreference = 'Stop'
    Add-Type -AssemblyName System.Speech
    $voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $voice.SetOutputToWaveFile($env:VOCALISTENER_FIXTURE)
    $voice.Speak('Hello world. This is a simple singing test.')
    $voice.Dispose()
'''], check=True)

app = QApplication([])
window = VocalListenerModern()
assert window.lang_input.currentText() == "english"
assert not window.radio_vocaloid.isEnabled()
assert (args.prefix / "app/docs/windows.html").is_file()
assert (args.prefix / "app/third-party/packages.json").is_file()
assert not (args.prefix / "app/res/russian").exists()
assert all(path.is_file() for path in model_paths("english"))
shortcut = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/VocaListener Modern/VocaListener Modern.lnk"
assert shortcut.is_file(), "Installer did not create a Start menu entry"

# Only the external file picker is replaced; the application handles the file,
# profile, screen transition, worker, and subprocess pipeline itself.
with patch.object(QFileDialog, "getOpenFileName", return_value=(str(fixture), "")):
    window.open_audio_file()
    window.open_audio_file()  # a second selection must not leave duplicate inputs
window.text_area.setPlainText("Hello world. This is a simple singing test.")
messages = []
with patch.object(QMessageBox, "critical", side_effect=lambda *a: messages.append(str(a[2]))), patch.object(QMessageBox, "warning", side_effect=lambda *a: messages.append(str(a[2]))):
    window.transition_to_screen_2()
    processing = window.screen2
    processing.btn_start.click()
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        app.processEvents()
        if messages or processing.btn_start.text() == "Done":
            break
        time.sleep(0.05)
    if processing.worker:
        processing.worker.wait(10000)
    log = processing.log_console.toPlainText()
    (directory / "smoke-test.log").write_text(log, encoding="utf-8")
    print(log)
    assert not messages, messages
    assert processing.btn_start.text() == "Done", "Pipeline did not complete"
    assert processing.btn_save.isEnabled()

work = Path(processing.tmp_dir)
project = json.loads((work / "output.svp").read_text(encoding="utf-8"))
notes = project["tracks"][0]["mainGroup"]["notes"]
assert any(note["phonemes"] == "hh" for note in notes), "No English HH alignment"
assert any(note["attributes"].get("languageOverride") == "english" for note in notes)
assert project["tracks"][0]["mainRef"]["systemPitchDelta"]["points"], "Pitch curve is empty"
assert list((work / "mfa_output").rglob("*.TextGrid")), "No real MFA output"
assert (work / "pitch.txt").stat().st_size > 0
processing.close()
window.close()
print("Installed offline English GUI conversion passed.")
