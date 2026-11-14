"""Regression checks for installed behavior; no Conda activation or Qt required."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import runtime


class RuntimeTests(unittest.TestCase):
    def test_conversion_modules_import_without_conda_activation(self):
        env = dict(os.environ)
        env.pop("CONDA_DEFAULT_ENV", None)
        result = subprocess.run([sys.executable, "-c", "import parse_output, clean_phonemes, pitch_phonemes_to_synthv"], cwd=ROOT / "src", env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_cli_failure_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "audio.wav").touch()
            result = subprocess.run([sys.executable, str(ROOT / "src/main.py"), "--input_dir", temp, "--tmp_dir", str(directory / "work"), "--step", "3"], capture_output=True, text=True, env={**os.environ, "VOCALISTENER_DATA_DIR": str(directory / "data")})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TextGrid file missing", result.stdout)

    def test_user_resources_are_writable_and_preserved(self):
        with tempfile.TemporaryDirectory(prefix="Voca User ") as temp:
            with patch.dict(os.environ, {"VOCALISTENER_DATA_DIR": temp}):
                mapping = runtime.resource_directory() / "english/synthV.txt"
                self.assertTrue(mapping.is_file())
                mapping.write_text("user customization", encoding="utf-8")
                runtime.resource_directory()
                self.assertEqual(mapping.read_text(), "user customization")
                self.assertEqual(runtime.work_directory(), Path(temp).resolve() / "tmp")

    def test_models_use_bundled_paths_and_reject_missing_languages(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "models").mkdir()
            for suffix in ["dict", "zip"]:
                (root / f"models/english_us_arpa.{suffix}").touch()
            with patch.object(runtime, "APP_ROOT", root):
                self.assertEqual(runtime.model_paths("english"), (root / "models/english_us_arpa.dict", root / "models/english_us_arpa.zip"))
                with self.assertRaises(ValueError):
                    runtime.model_paths("russian")

    def test_textgrid_to_svp_without_activation(self):
        from parse_output import parse_textgrid_with_silence
        from clean_phonemes import remap_phones
        from pitch_phonemes_to_synthv import convert_phonemes_to_svp
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            textgrid = directory / "audio.TextGrid"
            textgrid.write_text('name = "phones"\nxmin = 0\nxmax = 0.5\ntext = "HH"\nxmin = 0.5\nxmax = 1\ntext = "AH0"\n', encoding="utf-8")
            words, phones = directory / "words.json", directory / "phones.json"
            parse_textgrid_with_silence(textgrid, words, phones)
            mapped = remap_phones(phones, ROOT / "res/english/synthV.txt", directory / "mapped.json")
            output = directory / "output.svp"
            convert_phonemes_to_svp(mapped, output)
            notes = json.loads(output.read_text())["tracks"][0]["mainGroup"]["notes"]
            self.assertEqual([note["phonemes"] for note in notes], ["hh", "ah"])
            self.assertEqual(notes[1]["onset"], 705600000)
            self.assertEqual(notes[1]["attributes"]["languageOverride"], "english")


if __name__ == "__main__":
    unittest.main()
