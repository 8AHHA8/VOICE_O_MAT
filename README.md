# VOICE-O-MAT

VOICE-O-MAT is a desktop audiobook generator and text-to-speech (TTS) application inspired by vintage reel-to-reel tape recorders. Powered by the XTTS v2 speech synthesis engine, it generates speech using audio samples as voice references.

The application combines modern AI-powered speech synthesis with a retro interface featuring a wooden enclosure, animated tape reels, LED indicators, mechanical sound effects, and an interactive balloon-style avatar.

## Features

### Text-to-Speech and Audiobook Generation

- **Multi-format text support** — Load text from supported document formats, including `.txt`, `.pdf`, and `.docx`.
- **Voice cloning** — Use authorized audio samples in `.wav`, `.mp3`, `.m4a`, `.ogg`, and `.flac` formats as voice references.
- **Multilingual speech synthesis** — Generate speech in Polish, English, German, Spanish, French, and Italian, subject to the capabilities of the selected model.
- **Speech customization** — Adjust speech speed and pitch using dedicated controls.
- **Audio preview** — Generate and listen to a short sample before processing the full text.
- **Built-in audio player** — Play previously generated recordings using the Play Last feature.
- **Automatic file saving** — Save generated audio recordings as WAV files in `Audio/output_audio/`.

### Interactive Retro Avatar

- **Animated balloon character** — A green, balloon-shaped avatar integrated into the graphical interface.
- **Audio-reactive lip-sync** — Animate the avatar's mouth according to audio volume using RMS-based measurements.
- **Idle animations** — Add subtle eye movements and gentle body swaying.
- **Mouse tracking** — Allow the avatar's eyes to follow the user's mouse cursor.
- **Manual rotation** — Use directional controls to tilt the avatar left or right.
- **Dynamic visual effects** — Use shading and dynamic line thickness to enhance the avatar's appearance.
- **Interaction modes** — Switch between wandering, mouse tracking, and manual rotation.

### Retro Graphical Interface

- Vintage reel-to-reel tape recorder aesthetic.
- Wooden textures and a custom color palette.
- Three-dimensional-inspired buttons and controls.
- Animated tape reels and LED status indicators.
- Mechanical button clicks and motor sound effects.
- Integrated text processing, speech generation, and audio playback controls.

## Requirements

The following software and hardware may be required, depending on the selected configuration:

- **Python:** 3.10–3.12, subject to compatibility with the installed dependencies.
- **Git:** Required to clone the repository.
- **FFmpeg:** Required for supported audio processing and format conversion operations.
- **NVIDIA GPU:** Optional, but recommended for accelerated speech synthesis.
- **CUDA-compatible PyTorch:** Required for NVIDIA GPU acceleration.

Python package dependencies are listed in `requirements.txt`.

The first launch may download the XTTS v2 model and its required files. Additional disk space and an internet connection may be necessary.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/8AHHA8/VOICE_O_MAT.git
cd VOICE_O_MAT
```

### 2. Create a Virtual Environment

**Windows:**

```bat
python -m venv venv
```

**Linux:**

```bash
python3 -m venv venv
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

If PowerShell blocks script execution, review your execution policy before changing it.

**Linux:**

```bash
source venv/bin/activate
```

Using a virtual environment helps isolate project dependencies from other Python installations.

### 4. Install System Dependencies

#### Windows

Install Git and FFmpeg if they are not already available on your system.

#### Linux — Ubuntu / Debian

Install the system packages required by the application and its audio dependencies:

```bash
sudo apt update
sudo apt install python3-tk python3-dev build-essential portaudio19-dev ffmpeg libmagic1
```

Some packages may only be necessary if the corresponding dependencies are used by the application. Package names may differ on other Linux distributions.

### 5. Install Python Dependencies

Upgrade pip and install the project's dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If installation fails, check the error message and verify that the Python version and package versions are compatible.

### 6. Configure PyTorch and CUDA (Optional)

An NVIDIA GPU can accelerate speech synthesis when supported by the installed model and libraries.

Check whether PyTorch can access CUDA:

```bash
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda)"
```

For additional GPU information, run:

```bash
nvidia-smi
```

If you need to install or replace PyTorch, use the official installation selector:

https://pytorch.org/get-started/locally/

**Important:** PyTorch, TorchAudio, TorchCodec (if used), the NVIDIA driver, and the TTS dependencies must be compatible. Do not install an arbitrary CUDA build over the versions required by the project.

CPU execution may be possible, but performance and supported configurations depend on the selected model and installed dependencies.

### 7. Run the Application

Start VOICE-O-MAT from the project directory:

```bash
python main.py
```

On the first launch, the application may download the required model files. Startup time depends on your internet connection, available hardware, model size, and whether the files are already cached locally.

## Usage

The general workflow is:

1. Launch VOICE-O-MAT.
2. Load a supported text document or enter text using the available controls.
3. Select one or more authorized audio samples to use as voice references.
4. Choose the desired language and adjust the available speech settings.
5. Generate and listen to a preview, if available.
6. Start audiobook generation.
7. Observe the interface animations and avatar behavior.
8. Access the resulting WAV files in the configured output directory.

The exact controls and available options depend on the installed version of the application.

## Project Structure

The following is an indicative project structure based on the described application architecture. Update it to match the actual files in the repository.

```text
VOICE_O_MAT/
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── Audio/
│   ├── clicks.py
│   ├── engine.py
│   ├── generator.py
│   ├── model.py
│   ├── preview.py
│   ├── utils.py
│   └── output_audio/
└── GUI/
    ├── app.py
    ├── avatar.py
    ├── controls.py
    ├── sections.py
    ├── animations.py
    ├── theme.py
    └── widgets.py
```

## Audio Output

Generated recordings are saved in WAV format in:

```text
Audio/output_audio/
```

Previously generated recordings can be accessed through the built-in audio player, where supported.

The application does not require sentiment metadata files as part of the described workflow.

## Troubleshooting

### FFmpeg Is Not Recognized

If the terminal reports that `ffmpeg` is not recognized, verify that FFmpeg is installed and its executable directory is included in the system `PATH`.

Open a new terminal and check the installation:

```bash
ffmpeg -version
```

### Tkinter Is Missing on Linux

Install Tkinter for the Python installation being used:

```bash
sudo apt install python3-tk
```

If Tkinter remains unavailable, verify that the virtual environment uses a compatible Python installation.

### Audio Libraries Fail to Initialize

On Ubuntu or Debian, install the PortAudio development files:

```bash
sudo apt install portaudio19-dev
```

Also verify that the selected audio backend is supported by your operating system.

### CUDA or GPU Errors

Check the NVIDIA driver and verify CUDA availability in PyTorch:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If GPU inference is unavailable, verify the installed PyTorch build and model requirements. Switch to CPU execution only if the application's configuration and dependencies support it.

### Model Download or Loading Errors

Check your internet connection, available disk space, and access to the model repository. Ensure that the installed TTS package supports the configured XTTS v2 model.

### Slow Speech Generation

Inference speed depends on the selected model, text length, hardware, and runtime configuration. Use a compatible GPU configuration when available and close other memory-intensive applications if GPU memory is limited.

### Avatar Animations Do Not Work

Verify that the avatar component is present and initializes correctly. Check the application logs for missing modules or runtime errors. Ensure that the relevant animation and audio-processing components are included in the current version.

## License and Responsible Use

VOICE-O-MAT uses third-party libraries and AI models, including XTTS v2.

Before redistributing the application or using it commercially, review the licenses, usage restrictions, and attribution requirements of the project, its dependencies, and its model weights.

**Voice cloning and consent:** Use voice references only when you have the necessary authorization. Do not use generated speech to impersonate or deceive others. Voice cloning may be subject to applicable laws, privacy requirements, and personal rights.

## Author

GitHub repository: https://github.com/8AHHA8/VOICE_O_MAT
