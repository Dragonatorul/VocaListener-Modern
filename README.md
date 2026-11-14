# VocaListener Modern

Convert a recording of your singing and its exact lyrics into an editable **Synthesizer V `.svp` project**, with aligned phonemes and a pitch curve. English is the default; Japanese is also available. Processing runs locally on the CPU.

## Windows 11: one download

1. Open the [latest release](https://github.com/Dragonatorul/VocaListener-Modern/releases/latest).
2. Download **`VocaListener-Modern-<version>-Windows-x64-Setup.exe`** under Assets.
3. Run the installer, choose **Just Me**, and launch **VocaListener Modern** from the Start menu.

The installer contains Python, Qt, Montreal Forced Aligner (MFA), Kaldi/Kalpy, audio tools, English and Japanese models, pronunciation dictionaries, and phoneme mappings. No separate Python, Conda, Anaconda, WSL, Linux, Bash, CUDA, or model download is required. Installation and conversion work offline after the download. Windows 11 on Intel/AMD x64 is the supported target; ARM64 builds are not supplied.

Read the [user guide](docs/windows.html) for conversion steps, file locations, troubleshooting, and uninstall instructions. It is also attached to each release as **User-Guide.html**, installed in the Start menu as **User Guide**, and available through **Get Help** and **Tutorial** inside the app.

## Use

Choose English or Japanese, select a clear vocal recording, enter the exact lyrics (or choose a UTF-8 text file), and click **Next**. Click **Start Processing**, then **Save Output File** when all five steps finish. Open the saved `.svp` in your Synthesizer V editor and select a voice that supports the chosen language.

Use a short, clean, unaccompanied WAV recording for the best starting result. Alignment models are trained on speech, so singing timing and pronunciation often need manual adjustment. Japanese mappings approximate some distinctions, including geminates and devoiced vowels; audition the result in a Japanese-capable voice. The app does not include the Synthesizer V editor or commercial voice databases, needed only to edit/render the exported project. Vocaloid export and microphone recording are not implemented; those controls are disabled or marked as placeholders. Russian is not included in the Windows package or language selector.

## Development and releases

See [development and release instructions](docs/development.md). GitHub Actions builds a native Windows installer, installs it on a separate Windows runner, and checks the GUI and actual conversion offline before publishing a version tag. Each release includes a SHA-256 checksum, resolved runtime package list, and third-party notices.

## License and origins

Application source: [MIT](LICENSE). Bundled components retain [their own licenses](docs/third-party.md); model licenses and package notices are installed alongside the application. Most of the original project was written using AI.

This is a fresh implementation, not a port of the original VocaListener from Nagoya Institute of Technology.
