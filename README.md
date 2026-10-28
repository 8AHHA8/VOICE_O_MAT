# VOICE-O-MAT

VOICE-O-MAT is an audiobook generator and text-to-speech application featuring a graphical interface inspired by a retro reel-to-reel tape recorder. Powered by the XTTS v2 text-to-speech engine, the application generates speech using audio samples as voice references.

The interface combines modern speech synthesis technology with a vintage aesthetic, including a wooden casing, animated tape reels, LED indicators, and mechanical sound effects.

## Features

- **Multi-format text support** — Load text from `.txt`, `.pdf`, `.docx`, and other supported document formats.
- **Voice cloning** — Use one or multiple audio samples in `.wav`, `.mp3`, `.m4a`, `.ogg`, or `.flac` format as voice references.
- **Multiple languages** — Generate speech in Polish, English, German, Spanish, French, and Italian.
- **Speech customization** — Adjust speech speed and pitch using dedicated sliders.
- **Audio preview** — Generate and listen to a short sample before processing the entire text.
- **Built-in audio player** — Browse and play previously generated `.wav` files using the Play Last feature.
- **Retro graphical interface** — Custom wooden styling, 3D-inspired buttons, animated tape reels, and LED indicators.
- **Mechanical sound effects** — Button clicks and motor sounds enhance the retro experience.
- **Automatic file saving** — Generated audio files are saved in the `Audio/output_audio/` directory.

## Requirements

The following software is required to run VOICE-O-MAT:

- Python 3.10–3.12
- Git, for cloning the repository
- FFmpeg
- An NVIDIA GPU with compatible CUDA support (optional, for accelerated audio generation)

Python package dependencies are listed in `requirements.txt`.

## Installation and Setup

### 1. Clone the Repository

Clone the project and navigate to its directory:

```bash
git clone https://github.com/8AHHA8/VOICE_O_MAT.git
cd VOICE_O_MAT
```

### 2. Create a Virtual Environment

Create an isolated Python environment for the project:

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**Windows — Command Prompt:**

```bat
venv\Scripts\activate.bat
```

**Windows — PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux:**

```bash
source venv/bin/activate
```

Using a virtual environment helps isolate the project's dependencies from other Python installations.

### 4. Install Dependencies

Upgrade `pip` and install the required Python packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Linux-Specific Dependencies (Ubuntu / Debian)

On Linux, some system-level dependencies may need to be installed before running VOICE-O-MAT.

Install the following packages:

```bash
sudo apt update
sudo apt install python3-tk portaudio19-dev ffmpeg libmagic1
```

Depending on the Python packages used by the application, additional development tools may be required:

```bash
sudo apt install python3-dev build-essential
```

After installing these packages, activate the virtual environment and install the Python dependencies as described above.

**Note:** These commands are intended for Ubuntu and Debian-based distributions. Other Linux distributions may use different package managers or package names. Additional system libraries may be necessary depending on the installed Python packages.

### 5. Install FFmpeg

FFmpeg is used for audio processing and format conversion.

#### Windows

1. Visit the [FFmpeg Builds website](https://www.gyan.dev/ffmpeg/builds/).
2. Download the `ffmpeg-release-full-shared` archive.
3. Extract it to a directory, for example:

   ```text
   C:\ffmpeg-shared\
   ```

4. Add the directory containing `ffmpeg.exe` and the required DLL files to the Windows `PATH` environment variable. For example:

   ```text
   C:\ffmpeg-shared\bin
   ```

5. Open a new terminal and verify the installation:

   ```bash
   ffmpeg -version
   ```

#### Linux (Ubuntu / Debian)

FFmpeg can be installed using the system package manager:

```bash
sudo apt update
sudo apt install ffmpeg
```

Verify the installation:

```bash
ffmpeg -version
```

### 6. Install PyTorch with CUDA (Optional)

If you have a compatible NVIDIA GPU, a CUDA-enabled version of PyTorch can accelerate audio generation.

For example, the following command installs a build for CUDA 12.1:

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Important:** Select a PyTorch version compatible with your Python version, NVIDIA driver, CUDA requirements, and the project's dependencies. If PyTorch is already specified in `requirements.txt`, check for version conflicts before installing or replacing it.

If you do not have a compatible NVIDIA GPU, follow the CPU configuration supported by the project's dependencies.

### 7. Run the Application

Start VOICE-O-MAT with:

```bash
python main.py
```

On the first launch, the application may download the XTTS v2 model and its required files. The download size may be approximately 1.8 GB, depending on the model files being retrieved. Initial setup time depends on your internet connection and hardware.

## Project Structure

The project separates application configuration, audio processing, model management, and graphical interface components.

```text
VOICE_O_MAT/
├── main.py                  # Main application entry point
├── config.py                # Application configuration, paths, and colors
├── requirements.txt         # Python dependencies
├── Audio/
│   ├── clicks.py            # Mechanical sound effects
│   ├── engine.py            # Audio engine integrating components
│   ├── generator.py         # Speech and audiobook generation
│   ├── model.py             # TTS model and VRAM management
│   ├── preview.py           # Preview generation and playback
│   ├── utils.py             # Document and audio utilities
│   └── output_audio/        # Generated WAV files
├── GUI/
│   ├── app.py               # Main graphical application
│   ├── controls.py          # Start, pause, and stop controls
│   ├── sections.py          # Interface layout and sections
│   ├── animations.py        # Tape reel and timer animations
│   ├── theme.py             # Colors and wood texture generation
│   └── widgets.py           # Custom interface widgets
└── README.md                # Project documentation
```

**Note:** This tree describes the expected project structure. Update it if the actual repository contains different filenames or directories.

## Interface Design

VOICE-O-MAT is designed to resemble a vintage reel-to-reel tape recorder while providing a modern text-to-speech workflow.

The visual design includes:

- Procedurally generated wood textures.
- Three-dimensional, tactile-looking buttons.
- Animated tape reels.
- LED status indicators.
- Mechanical sound effects.

The interface aims to make audiobook creation more engaging by combining speech synthesis with the appearance of classic audio equipment.

## Audio Output

Generated audio files are saved in WAV format in the following directory:

```text
Audio/output_audio/
```

Previously generated recordings can be accessed through the application's built-in audio player.

## Troubleshooting

### FFmpeg Is Not Recognized

If the terminal reports that `ffmpeg` is not recognized, check that FFmpeg is installed and its executable directory has been added to the system `PATH`. Restart the terminal after changing environment variables.

### Missing Tkinter on Linux

If Python reports that `tkinter` is unavailable, install the appropriate package for your distribution. On Ubuntu and Debian, use:

```bash
sudo apt install python3-tk
```

### Missing Audio Libraries on Linux

If audio-related dependencies fail to install or initialize, check whether PortAudio development files are installed:

```bash
sudo apt install portaudio19-dev
```

### CUDA or GPU Errors

Verify that your NVIDIA driver and installed PyTorch build are compatible. If GPU acceleration is unavailable, use a CPU configuration supported by the application.

## License and Responsible Use

VOICE-O-MAT is intended for educational and personal projects. It relies on third-party libraries and the XTTS v2 model.

Review the licenses and terms of use of all third-party dependencies and models before redistributing the application or using it commercially.

**Voice cloning and consent:** Use voice cloning only when you have the necessary authorization. Cloning a person's voice without permission, or using generated speech to impersonate or deceive others, may violate applicable laws or personal rights. Additional licensing restrictions may apply to commercial use.

## Author

GitHub repository: [8AHHA8/VOICE_O_MAT](https://github.com/8AHHA8/VOICE_O_MAT)