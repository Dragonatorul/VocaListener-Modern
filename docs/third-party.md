# Bundled components and notices

The single Windows installer contains application source, an isolated Python runtime, PyQt6/Qt, NumPy, SciPy, librosa, SoundFile/libsndfile, MFA 3.3.8, CPU Kalpy 0.8.2/Kaldi, OpenFst, FFmpeg (LGPL build), SoX, Japanese tokenization libraries, and their resolved dependencies. No NVIDIA runtime is required.

Application source is MIT licensed. Each bundled dependency retains its own license, including GPL/LGPL components; the MIT license does not replace those licenses. The installed `app/third-party/packages/` directory preserves license texts and `about.json` source metadata from the exact conda-forge packages used. `packages.json` records versions, builds, package URLs, checksums, and declared licenses. The same inventory and explicit environment specification are attached to the release. Installed application source and packaging scripts are available under `app/src` and `app/packaging/windows`. Local compatibility changes add UTF-8 process settings to the Python interpreter manifests and quote two SQLite CSV paths in MFA; the patch scripts are included. Inventory checksums identify the original conda package archives.

Unmodified language resources are maintained by [Montreal Forced Aligner](https://github.com/MontrealCorpusTools/mfa-models) and licensed CC BY 4.0:

| Resource | Version | Attribution / source |
| --- | --- | --- |
| English US ARPA acoustic model | 3.0.0 | Michael McAuliffe and Morgan Sonderegger, 2024; [model release](https://github.com/MontrealCorpusTools/mfa-models/releases/tag/acoustic-english_us_arpa-v3.0.0) |
| English US ARPA dictionary | 3.0.0 | Gorman, Howell and Wagner, *Prosodylab-aligner*, 2011; [dictionary release](https://github.com/MontrealCorpusTools/mfa-models/releases/tag/dictionary-english_us_arpa-v3.0.0) |
| Japanese MFA acoustic model | 3.0.0 | Michael McAuliffe and Morgan Sonderegger, 2024; [model release](https://github.com/MontrealCorpusTools/mfa-models/releases/tag/acoustic-japanese_mfa-v3.0.0) |
| Japanese MFA dictionary | 3.0.0 | Michael McAuliffe and Morgan Sonderegger, 2024; [dictionary release](https://github.com/MontrealCorpusTools/mfa-models/releases/tag/dictionary-japanese_mfa-v3.0.0) |

Complete upstream license texts and attribution metadata are included in `app/third-party/`. Downloads are pinned by release URL and SHA-256 in `packaging/windows/models.json`. Application phoneme mappings are separate transformations; they do not modify the pretrained models or dictionaries. Targets follow Synthesizer V's English ARPAbet and Japanese romaji phonesets; Japanese mappings approximate length, devoicing, and some allophones. See the [Dreamtonics phoneme reference](https://dreamtonics.com/svstudio-resources/).

Synthesizer V, its voice databases, and Vocaloid are not included. Product names belong to their respective owners. This project is independently developed.
