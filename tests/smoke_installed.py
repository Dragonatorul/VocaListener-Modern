"""Exercise the installed wizard and all five real processing steps offline."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import ctypes
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument("--prefix", type=Path, required=True)
parser.add_argument("--japanese-audio", type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.prefix / "app/src"))
from runtime import configure_runtime, data_directory, model_paths
configure_runtime()
assert ctypes.windll.kernel32.GetACP() == 65001, "Bundled Python must use UTF-8 native APIs"
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
assert shortcut.with_name("User Guide.lnk").is_file(), "Offline guide shortcut is missing"

def convert(language, audio, lyrics):
    window = VocalListenerModern()
    window.lang_input.setCurrentText(language)
    # Only the external file picker is replaced; the app handles input copying,
    # the profile, screen transition, worker, and subprocess pipeline itself.
    with patch.object(QFileDialog, "getOpenFileName", return_value=(str(audio), "")):
        window.open_audio_file()
        window.open_audio_file()
    window.text_area.setPlainText(lyrics)
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
        (directory / f"smoke-test-{language}.log").write_text(log, encoding="utf-8")
        print(log)
        assert not messages, messages
        assert processing.btn_start.text() == "Done", "Pipeline did not complete"
        assert processing.btn_save.isEnabled()
    work = Path(processing.tmp_dir)
    project = json.loads((work / "output.svp").read_text(encoding="utf-8"))
    notes = project["tracks"][0]["mainGroup"]["notes"]
    assert any(note["attributes"].get("languageOverride") == language for note in notes)
    assert project["tracks"][0]["mainRef"]["systemPitchDelta"]["points"], "Pitch curve is empty"
    assert list((work / "mfa_output").rglob("*.TextGrid")), "No real MFA output"
    assert (work / "pitch.txt").stat().st_size > 0
    processing.close()
    window.close()
    print(f"Installed offline {language} GUI conversion passed.")
    return notes


english_notes = convert("english", fixture, "Hello world. This is a simple singing test.")
assert any(note["phonemes"] == "hh" for note in english_notes), "No English HH alignment"
assert all(path.is_file() for path in model_paths("japanese"))
japanese_notes = convert("japanese", args.japanese_audio,
    "アカギツネさんは本を読んだことがたくさんありますけれども、読むべき本はまだまだいっぱい残っています。")
assert any(note["phonemes"] == "a" for note in japanese_notes), "No Japanese vowel alignment"
