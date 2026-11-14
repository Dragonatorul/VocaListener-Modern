"""Desktop entry point. Native dependencies are configured before importing Qt."""
import sys
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import configure_runtime, data_directory


def main():
    configure_runtime()
    # pythonw has no console streams. Keep startup failures available for support.
    data_directory().mkdir(parents=True, exist_ok=True)
    log = open(data_directory() / "application.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = log
    try:
        from PyQt6.QtWidgets import QApplication
        from vocalistener_gui import VocalListenerModern
        app = QApplication(sys.argv)
        window = VocalListenerModern()
        window.show()
        if "--smoke-test" in sys.argv:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1000, app.quit)
        return app.exec()
    except Exception:
        traceback.print_exc()
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, f"Unable to start. See {log.name}", "VocaListener Modern", 0x10)
        return 1


if __name__ == "__main__":
    sys.exit(main())
