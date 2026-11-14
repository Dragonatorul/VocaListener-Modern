"""Stage source, models, notices, and a constructor recipe for one offline EXE."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import urllib.request
import yaml

ROOT = Path(__file__).resolve().parents[2]
MODEL_SOURCE = "9cbc4c96af41b8a0acbd98eb75888839af9f1e17"


def download(url, target, expected=None):
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        target.write_bytes(response.read())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    if expected and digest != expected:
        raise ValueError(f"Checksum mismatch: {target.name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--prefix", type=Path, required=True)
    parser.add_argument("--package-cache", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        parser.error("Use a numeric three-part version")
    stage = ROOT / "build" / "installer"
    app = stage / "app"
    if stage.exists():
        shutil.rmtree(stage)
    app.mkdir(parents=True)
    shutil.copytree(ROOT / "src", app / "src", ignore=shutil.ignore_patterns("__pycache__"))
    for language in ["english", "japanese"]:
        shutil.copytree(ROOT / "res" / language, app / "res" / language)
    shutil.copytree(ROOT / "docs", app / "docs")
    shutil.copytree(ROOT / "packaging" / "windows", app / "packaging" / "windows")
    shutil.copy2(ROOT / "LICENSE", app / "LICENSE")
    for model in json.loads((ROOT / "packaging/windows/models.json").read_text()):
        download(model["url"], app / "models" / model["filename"], model["sha256"])
    # Every pronunciation phone in both bundled dictionaries must be mapped.
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from clean_phonemes import load_mapping_dict
    for language, model in [("english", "english_us_arpa"), ("japanese", "japanese_mfa")]:
        mapping = load_mapping_dict(ROOT / f"res/{language}/synthV.txt")
        phones = set()
        for line in (app / "models" / f"{model}.dict").read_text(encoding="utf-8").splitlines():
            if "\t" in line:
                phones.update(line.rsplit("\t", 1)[1].split())
        missing = phones - mapping.keys()
        if missing:
            raise ValueError(f"Missing {language} phoneme mappings: {sorted(missing)}")
    notices = app / "third-party"
    notices.mkdir()
    for language, variant in [("english", "us_arpa"), ("japanese", "mfa")]:
        for kind in ["acoustic", "dictionary"]:
            base = f"https://raw.githubusercontent.com/MontrealCorpusTools/mfa-models/{MODEL_SOURCE}/{kind}/{language}/{variant}/v3.0.0"
            for filename in ["LICENSE", "meta.json"]:
                download(f"{base}/{filename}", notices / f"{language}-{kind}-{filename}")
    shutil.copy2(ROOT / "docs/third-party.md", notices / "README.md")
    # Preserve the actual redistributed packages' license texts and source metadata.
    packages = []
    for metadata in sorted((args.prefix / "conda-meta").glob("*.json")):
        record = json.loads(metadata.read_text(encoding="utf-8"))
        packages.append({key: record.get(key) for key in ["name", "version", "build", "url", "sha256", "license"]})
        package_name = f"{record['name']}-{record['version']}-{record['build']}"
        info = args.package_cache / package_name / "info"
        if (info / "licenses").is_dir():
            shutil.copytree(info / "licenses", notices / "packages" / package_name)
        if (info / "about.json").is_file():
            target = notices / "packages" / package_name
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(info / "about.json", target)
    (notices / "packages.json").write_text(json.dumps(packages, indent=2), encoding="utf-8")
    extras = [{str(file.resolve()): f"app/{file.relative_to(app).as_posix()}"} for file in app.rglob("*") if file.is_file()]
    extras.append({str((ROOT / "build/VocaListener-Modern.exe").resolve()): "VocaListener-Modern.exe"})
    recipe = {
        "name": "VocaListener-Modern", "version": args.version,
        "company": "VocaListener Modern contributors",
        "environment": str(args.prefix.resolve()),
        "channels": ["https://conda.anaconda.org/conda-forge"],
        "installer_type": "exe",
        "installer_filename": f"VocaListener-Modern-{args.version}-Windows-x64-Setup.exe",
        "default_prefix": "%LOCALAPPDATA%\\Programs\\VocaListener-Modern",
        "default_prefix_domain_user": "%LOCALAPPDATA%\\Programs\\VocaListener-Modern",
        "uninstall_name": "VocaListener Modern",
        "initialize_conda": False, "register_python": False, "register_envs": False,
        "check_path_spaces": False, "check_path_length": False,
        "keep_pkgs": False, "menu_packages": [],
        "license_file": str((ROOT / "LICENSE").resolve()),
        "post_install": str((ROOT / "packaging/windows/post_install.bat").resolve()),
        "pre_uninstall": str((ROOT / "packaging/windows/pre_uninstall.bat").resolve()),
        "extra_files": extras,
        "welcome_image_text": "VocaListener Modern",
        "header_image_text": "English singing to Synthesizer V",
        "conclusion_text": "Ready to use\nOpen VocaListener Modern from the Start menu. The User Guide is available there and in the app. All English and Japanese models and dependencies are included.",
    }
    (stage / "construct.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")


if __name__ == "__main__":
    main()
