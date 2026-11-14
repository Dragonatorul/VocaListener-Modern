"""Preserve Python's PE manifest while enabling UTF-8 native file APIs."""
import argparse
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


def prepare(prefix, destination, mt):
    outputs = []
    for name in ["python.exe", "pythonw.exe"]:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(prefix / name, target)
        manifest = target.with_suffix(".manifest")
        subprocess.run([str(mt), "-nologo", f"-inputresource:{target};#1", f"-out:{manifest}"], check=True)
        tree = ET.parse(manifest)
        root = tree.getroot()
        namespace = "{urn:schemas-microsoft-com:asm.v3}"
        application = root.find(f"{namespace}application")
        if application is None:
            application = ET.SubElement(root, f"{namespace}application")
        settings = application.find(f"{namespace}windowsSettings")
        if settings is None:
            settings = ET.SubElement(application, f"{namespace}windowsSettings")
        key = "{http://schemas.microsoft.com/SMI/2019/WindowsSettings}activeCodePage"
        codepage = settings.find(key)
        if codepage is None:
            codepage = ET.SubElement(settings, key)
        codepage.text = "UTF-8"
        tree.write(manifest, encoding="utf-8", xml_declaration=True)
        subprocess.run([str(mt), "-nologo", "-manifest", str(manifest), f"-outputresource:{target};#1"], check=True)
        outputs.append(target)
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--mt", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.prefix, args.destination, args.mt)
