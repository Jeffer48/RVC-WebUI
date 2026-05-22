# RVC Voice Converter

> 📖 **Parameter guides:** [Español](docs/PARAMETERS_ES.md) · [English](docs/PARAMETERS_EN.md)

---

## Quick Start (Release)

1. Download the latest release from GitHub
2. Extract the `.zip` file
3. Run `RVC-WebUI.exe`
4. A terminal window and your browser will open automatically
5. Add your `.pth` models to the `voices/` folder
6. Upload an audio file and click **Generate**

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
│   └── main.py              # FastAPI server (4 endpoints)
├── frontend/
│   ├── index.html           # UI
│   ├── style.css            # Styling (dark theme)
│   └── script.js            # Client logic (vanilla JS)
├── docs/
│   ├── PARAMETERS_ES.md     # Parameter guide (Spanish)
│   └── PARAMETERS_EN.md     # Parameter guide (English)
├── voices/                  # RVC voice models (gitignored)
│   └── sample_voice/        # Example folder (keep this)
├── outputs/                 # Converted audio (auto-created)
├── launcher.py              # PyInstaller entry point
├── build.spec               # PyInstaller build config
├── start.bat                # Windows launcher (dev)
├── requirements.txt         # Python dependencies
└── .gitignore
```

## Requirements (Development)

- **Python 3.11** (required; newer versions may cause dependency conflicts)
- Virtual environment (`.venv`)

Dependencies are installed automatically via `rvc-python`:

```
pip install rvc-python
```

This pulls in PyTorch, TorchAudio, FastAPI, Uvicorn, and all audio processing libraries.

## Setup (Development)

```powershell
# 1. Create virtual environment with Python 3.11
py -3.11 -m venv .venv

# 2. Activate it
.venv\Scripts\activate

# 3. Install dependencies
pip install rvc-python
```

## Adding Voice Models

Place your `.pth` (and optionally `.index`) files inside a subfolder under `voices/`:

```
voices/
├── sample_voice/            # Kept in git (ignored otherwise)
│   └── README.txt
└── my_character/
    ├── my_character.pth     # Required
    └── my_character.index   # Optional (improves quality)
```

The `voices/` folder is gitignored except for `sample_voice/`. Each model is auto-detected at server startup and listed in the frontend dropdown.

You can also upload new voices directly from the web interface using the **"+ Add Voice"** button next to the voice selector.

## Running (Development)

Double-click `start.bat` or run manually:

```powershell
.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000` in your browser.

## Hardware Support

The backend auto-detects the available device at startup:

| Machine | Device | Behavior |
|---|---|---|
| CPU only (e.g., dev laptop) | `cpu` | Full processing on CPU |
| NVIDIA GPU | `cuda:0` | GPU acceleration |

### Low VRAM (4GB) Handling

The RVC pipeline automatically splits audio into overlapping chunks to fit within available VRAM:

| VRAM | Chunk size |
|---|---|
| ≤ 4GB | ~30 seconds |
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
