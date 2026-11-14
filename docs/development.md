# Development and Windows releases

## Source runs

End users should use the [Windows installer](https://github.com/Dragonatorul/VocaListener-Modern/releases/latest). Conda is a build/development tool only; it is not a prerequisite on end-user machines.

On Windows, create an environment from `packaging/windows/environment.yml`. On other platforms, adapt native dependency build selections in `environment.yml` as needed. The supported Windows package is built entirely from conda-forge, including CPU Kalpy and LGPL FFmpeg. Do not replace MFA or Kalpy independently; their interfaces must match.

```text
conda env create -f packaging/windows/environment.yml
conda activate vocalistener-runtime
python src/launch.py
```

For source runs without `models/`, first download MFA models with `mfa model download acoustic english_us_arpa` and `mfa model download dictionary english_us_arpa`; Japanese uses `japanese_mfa` for both commands. The installer supplies explicit local model paths and never needs these commands. User data is outside the checkout; `VOCALISTENER_DATA_DIR` overrides it for development and tests.

The legacy `run.sh` is a source-development shortcut. The desktop entry point is `src/launch.py`; it configures bundled DLLs, PATH, Qt plugins, UTF-8 subprocess output, local MFA state, and Numba caches before importing native dependencies. Conda environment names do not gate imports. The native installed launcher ignores external Python packages and invokes this entry point with the packaged interpreter. Processing uses that interpreter too.

`src/mfa_compat.py` repairs MFA 3.3.8's Windows executable probe: upstream adds shell quotes to a filename before passing it in a subprocess argument list. The compatibility layer removes those outer quotes while preserving binary discovery and all dependency checks. The installed test's folder with spaces is the regression check for this issue. The build also applies a checked two-line source patch quoting the CSV filenames in MFA's SQLite `.import` commands; otherwise alignment fails when user-data paths contain spaces. Reassess these compatibility fixes when updating MFA.

The builder also preserves Python's existing PE manifests and adds Microsoft's `activeCodePage=UTF-8` setting. The mandatory post-install script applies those interpreter executables after constructor links the original packages. This allows native OpenFst/Kalpy file APIs to use Unicode paths without changing the user's Windows locale. The installed check asserts the active code page and processes files under a Japanese-character path. Package inventories describe the upstream conda archives; the interpreter manifests are the documented local binary modification.

## Validation

```text
python -m unittest discover -s tests -p test_runtime.py -v
python -m compileall -q src packaging/windows
actionlint .github/workflows/windows-release.yml
```

`tests/test.py` and `tests/test_packages.py` are legacy developer diagnostics, not the installed-app release gate. `tests/smoke_installed.py` is the Windows integration check: it creates a tiny English audio fixture using Windows speech synthesis, drives the real wizard and worker through all five steps, and checks TextGrid, phonemes, pitch, SVP, help, and shortcuts. It repeats conversion with a checksum-pinned Japanese recording and transcript from the MFA 3.3.8 documentation (MIT licensed, Michael McAuliffe). The fixture is fetched before network blocking; the installed app never downloads it. Only file dialogs and modal error reporting are replaced for unattended execution.

## Build and publish

The `Windows installer` GitHub Actions workflow builds on branch pushes, pull requests, manual dispatch, and `v*` tags. Branch runs upload a test installer as an Actions artifact. Only version tags publish a GitHub Release, after both build and installed-app test succeed.

1. Update `VERSION` with a numeric `major.minor.patch` version and commit source, model, mapping, and documentation changes.
2. Push the commit and let its Windows workflow pass. Review installer test logs.
3. Tag that commit as `v<version>` and push the tag, for example `git tag v0.1.0` then `git push origin v0.1.0`.
4. Follow the tag workflow through publication and verify the release assets and checksum.

The tag must match `VERSION`. Only the publish job has repository write permission. No external release secret is needed. Tags should be immutable. If publication alone fails, inspect it before rerunning; existing releases are not overwritten automatically.

The builder compiles a native `/MT` Windows launcher, creates a pinned runtime, downloads checksum-verified English and Japanese models, preserves notices, and generates a constructor installer. Constructor relocates native packages at install time. The installer does not register its Python as the system default, modify the user's PATH, or require Conda activation. Per-user Start menu links open the app and offline HTML guide. Uninstallation removes program files and links while retaining user data.

The exact `.exe` is tested on a separate `windows-2025` runner: installation into a path with spaces, native launcher startup, no Conda activation, minimal Windows PATH, a Unicode user-data path, and outbound firewall blocks on the app's Python and launcher. This checks offline runtime closure without relying on development tools accidentally being on PATH. Hosted runners are Windows Server, not physical Windows 11; retain this distinction when reporting evidence. Singing alignment and voice-specific rendering require listening checks in Synthesizer V.

Release attachments: installer, `SHA256SUMS.txt`, `User-Guide.html`, `THIRD-PARTY.md`, `packages.json`, and `windows-runtime-explicit.txt`. Dependency resolution is fixed within each installer; the explicit list makes transitive choices inspectable. Top-level runtime/model versions are pinned in the repository. The installer is unsigned unless code-signing is explicitly configured later.
