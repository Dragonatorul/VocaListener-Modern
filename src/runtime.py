"""Paths and process environment shared by source and installed applications."""
import os
from pathlib import Path
import shutil
import sys

APP_ROOT = Path(__file__).resolve().parent.parent
MODEL_NAMES = {"english": "english_us_arpa", "japanese": "japanese_mfa"}
_dll_directories = []


def data_directory():
    override = os.environ.get("VOCALISTENER_DATA_DIR")
    if override:
        return Path(override).resolve()
    if sys.platform == "win32":
        return Path(os.environ["LOCALAPPDATA"]) / "VocaListener-Modern" / "data"
    return Path.home() / ".local" / "share" / "VocaListener-Modern"


def work_directory():
    return data_directory() / "tmp"


def resource_directory():
    """Copy editable mappings once; upgrades preserve the user's changes."""
    destination = data_directory() / "res"
    for source in (APP_ROOT / "res").rglob("*.txt"):
        target = destination / source.relative_to(APP_ROOT / "res")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
    return destination


def configure_runtime():
    """Activate bundled native libraries without requiring a shell or Conda."""
    prefix = Path(sys.prefix)
    directories = [prefix, prefix / "Library" / "bin", prefix / "Scripts", prefix / "bin"]
    os.environ["PATH"] = os.pathsep.join(map(str, directories)) + os.pathsep + os.environ.get("PATH", "")
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONNOUSERSITE"] = "1"
    os.environ["MFA_ROOT_DIR"] = str(data_directory() / "mfa")
    os.environ["NUMBA_CACHE_DIR"] = str(data_directory() / "numba")
    os.environ["OMP_NUM_THREADS"] = "1"
    if sys.platform == "win32":
        # Keep the handles alive for Python 3.8+ extension module loading.
        for directory in directories:
            if directory.is_dir():
                _dll_directories.append(os.add_dll_directory(str(directory)))
        os.environ["QT_PLUGIN_PATH"] = str(prefix / "Library" / "plugins")


def python_executable():
    executable = Path(sys.executable)
    if executable.name.lower() == "pythonw.exe":
        executable = executable.with_name("python.exe")
    return str(executable)


def subprocess_options():
    options = {"encoding": "utf-8", "errors": "replace"}
    if sys.platform == "win32":
        options["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
    return options


def mfa_command():
    return [python_executable(), str(APP_ROOT / "src" / "mfa_entry.py")]


def model_paths(language):
    name = MODEL_NAMES.get(language, f"{language}_mfa")
    models = APP_ROOT / "models"
    if models.is_dir():
        dictionary, acoustic = models / f"{name}.dict", models / f"{name}.zip"
        if not dictionary.is_file() or not acoustic.is_file():
            raise ValueError(f"No bundled models for '{language}'. Choose English or Japanese.")
        return dictionary, acoustic
    return name, name  # Source builds may use MFA's developer-managed model cache.


def open_help():
    from PyQt6.QtCore import QUrl
    from PyQt6.QtGui import QDesktopServices
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(APP_ROOT / "docs" / "windows.html")))
