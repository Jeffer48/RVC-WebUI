# RVC Voice Converter

> Parameter guides: [Espanol](docs/PARAMETERS_ES.md) . [English](docs/PARAMETERS_EN.md)

---

## Quick Start (Release)

1. Download the latest release from GitHub
2. Choose the right version for your PC:
   - **`RVC-WebUI-CPU.exe`** -- Works on any PC, runs entirely on CPU
   - **`RVC-WebUI-CUDA.exe`** -- NVIDIA GPU required, much faster
3. Extract the `.zip` file
4. Run the `.exe` -- a terminal window and your browser will open automatically
5. Add your `.pth` models to the `voices/` folder
6. Upload an audio file and click **Generate**

> If you run the CPU build on a PC with an NVIDIA GPU, a warning will appear reminding you to download the CUDA version for better performance.

---

## Features

- Drag & drop audio upload (WAV or MP3, up to 10 minutes)
- Voice model selector populated automatically from the `voices/` directory
- Configurable pitch shift (transpose), F0 extraction method (PM or Harvest), and index rate
- Automatic model version detection (v1 / v2)
- Memory-safe processing for low-VRAM GPUs (4GB+)
- Progress bar with estimated chunk count based on audio duration
- Converted audio saved to `outputs/` and served directly in the browser

## Project Structure

```
RVC/
├── backend/
│   └── main.py               # FastAPI server (5 endpoints)
├── frontend/
│   ├── index.html            # UI
│   ├── style.css             # Styling (dark theme)
│   └── script.js             # Client logic (vanilla JS)
├── docs/
│   ├── PARAMETERS_ES.md      # Parameter guide (Spanish)
│   └── PARAMETERS_EN.md      # Parameter guide (English)
├── scripts/
│   └── setup.ps1             # Environment setup (CPU or CUDA)
├── voices/                   # RVC voice models (gitignored)
│   └── sample_voice/         # Example folder (keep this)
├── outputs/                  # Converted audio (auto-created)
├── launcher.py               # PyInstaller entry point
├── build_cpu.spec            # PyInstaller config (CPU build)
├── build_cuda.spec           # PyInstaller config (CUDA build)
├── start.bat                 # Windows launcher (dev)
├── requirements-cpu.txt      # Python dependencies (CPU)
├── requirements-cuda.txt     # Python dependencies (CUDA)
└── .gitignore
```

## Requirements (Development)

- **Python 3.11** (required; newer versions may cause dependency conflicts)

## Setup (Development)

Use the setup script to create the virtual environment and install dependencies:

```powershell
# CPU version (works on any PC)
.\scripts\setup.ps1 -Cpu

# CUDA version (requires NVIDIA GPU, much faster)
.\scripts\setup.ps1 -Cuda
```

The script will:
1. Create a `.venv` virtual environment with Python 3.11
2. Install all dependencies (CPU or CUDA PyTorch)

## Adding Voice Models

Place your `.pth` (and optionally `.index`) files inside a subfolder under `voices/`:

```
voices/
├── sample_voice/             # Kept in git (ignored otherwise)
│   └── README.txt
└── my_character/
    ├── my_character.pth      # Required
    └── my_character.index    # Optional (improves quality)
```

The `voices/` folder is gitignored except for `sample_voice/`. Each model is auto-detected at server startup and listed in the frontend dropdown.

You can also upload new voices directly from the web interface using the **"+ Add Voice"** button next to the voice selector.

## Running (Development)

Double-click `start.bat` or run manually:

```powershell
.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000` in your browser.

## Building the Executable

To generate standalone `.exe` files for distribution:

```powershell
# CPU build
.\scripts\setup.ps1 -Cpu
.venv\Scripts\pyinstaller build_cpu.spec
# Output: dist\RVC-WebUI-CPU.exe

# CUDA build (requires NVIDIA GPU on the build machine)
.\scripts\setup.ps1 -Cuda
.venv\Scripts\pyinstaller build_cuda.spec
# Output: dist\RVC-WebUI-CUDA.exe
```

The CUDA build must be done on a machine with an NVIDIA GPU and CUDA drivers installed, since PyInstaller bundles the actual CUDA-enabled PyTorch libraries.

## Hardware Support

The backend auto-detects the available device at startup:

| Build | Device | Requirements |
|---|---|---|
| `RVC-WebUI-CPU.exe` | `cpu` | Any Windows PC |
| `RVC-WebUI-CUDA.exe` | `cuda:0` | NVIDIA GPU + drivers |

### Low VRAM (4GB) Handling

The RVC pipeline automatically splits audio into overlapping chunks to fit within available VRAM:

| VRAM | Chunk size |
|---|---|
| <= 4GB | ~30 seconds |
| 5GB+ | ~38 seconds |
| 6GB+ (fp16) | ~60 seconds |

After each inference, `gc.collect()` and `torch.cuda.empty_cache()` are called to release GPU memory.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Redirects to the frontend |
| `/api/info` | GET | Returns `{device, chunk_seconds}` |
| `/api/voices` | GET | Lists available voice models |
| `/api/voices/upload` | POST | Upload a new voice model (multipart) |
| `/api/convert` | POST | Converts audio (multipart form) |

### POST `/api/convert`

Main parameters: `audio` (file), `voice` (str), `transpose` (int), `f0_method` (str), `index_rate` (float), `protect` (float), `rms_mix_rate` (float), `filter_radius` (int), `resample_sr` (int).

See [`docs/PARAMETERS_EN.md`](docs/PARAMETERS_EN.md) for detailed parameter explanations.

Response: `{"url": "/outputs/converted_{voice}_{timestamp}.wav", "filename": "..."}`

## License

This project uses [rvc-python](https://pypi.org/project/rvc-python/) (MIT) and is provided as-is.
