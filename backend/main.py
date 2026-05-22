import dataclasses as _dc
from dataclasses import field as _field

_orig_get_field = _dc._get_field


def _patched_get_field(cls, a_name, a_type, kw_only=False):
    try:
        return _orig_get_field(cls, a_name, a_type, kw_only)
    except ValueError as e:
        if "mutable default" in str(e):
            default_val = getattr(cls, a_name)
            setattr(cls, a_name, _field(default_factory=type(default_val)))
            return _orig_get_field(cls, a_name, a_type, kw_only)
        raise


_dc._get_field = _patched_get_field

import gc
import os
import sys
import tempfile
from datetime import datetime
from typing import Optional

import soundfile as sf
import torch

_orig_torch_load = torch.load


def _patched_torch_load(*args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _orig_torch_load(*args, **kwargs)


torch.load = _patched_torch_load

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from rvc_python.infer import RVCInference

if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
    _DATA_DIR = sys._MEIPASS  # type: ignore[attr-defined]
else:
    _BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
    _DATA_DIR = _BASE_DIR

VOICES_DIR = os.path.join(_BASE_DIR, "voices")
VOICES_DIR = os.path.abspath(VOICES_DIR)

OUTPUTS_DIR = os.path.join(_BASE_DIR, "outputs")
OUTPUTS_DIR = os.path.abspath(OUTPUTS_DIR)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

FRONTEND_DIR = os.path.join(_DATA_DIR, "frontend")
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
MAX_DURATION = 600

print(f"[RVC Server] Device: {DEVICE}")
print(f"[RVC Server] Voices directory: {VOICES_DIR}")
print(f"[RVC Server] Outputs directory: {OUTPUTS_DIR}")

app = FastAPI(title="RVC Voice Converter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")

rvc = RVCInference(models_dir=VOICES_DIR, device=DEVICE)


def _detect_model_version(pth_path: str) -> str:
    cpt = torch.load(pth_path, map_location="cpu")
    weight = cpt.get("weight", {})
    emb = weight.get("enc_p.emb_phone.weight")
    if emb is not None and emb.shape[1] == 256:
        return "v1"
    return "v2"


@app.get("/")
async def root():
    return RedirectResponse("/static/index.html")


@app.get("/api/info")
async def server_info():
    return {
        "device": DEVICE,
        "chunk_seconds": rvc.config.x_center,
    }


@app.get("/api/voices")
async def list_voices():
    voices = []
    if os.path.isdir(VOICES_DIR):
        for name in sorted(os.listdir(VOICES_DIR)):
            voice_dir = os.path.join(VOICES_DIR, name)
            if os.path.isdir(voice_dir):
                pth_files = [
                    f for f in os.listdir(voice_dir) if f.endswith(".pth")
                ]
                if pth_files:
                    voices.append(name)
    return {"voices": voices}


@app.post("/api/voices/upload")
async def upload_voice(
    pth: UploadFile = File(...),
    index: Optional[UploadFile] = File(None),
    overwrite: bool = False,
):
    if not pth.filename or not pth.filename.lower().endswith(".pth"):
        raise HTTPException(400, "A .pth model file is required")

    base_name = pth.filename.rsplit(".", 1)[0]
    if not base_name:
        raise HTTPException(400, "Invalid filename")

    voice_dir = os.path.join(VOICES_DIR, base_name)

    if os.path.isdir(voice_dir) and not overwrite:
        raise HTTPException(409, f"Voice '{base_name}' already exists")

    os.makedirs(voice_dir, exist_ok=True)

    pth_path = os.path.join(voice_dir, f"{base_name}.pth")
    with open(pth_path, "wb") as f:
        f.write(await pth.read())

    if index is not None and index.filename:
        index_base = index.filename.rsplit(".", 1)[0]
        if index_base != base_name:
            raise HTTPException(400, "Index file must have the same name as the model file")
        index_path = os.path.join(voice_dir, f"{base_name}.index")
        with open(index_path, "wb") as f:
            f.write(await index.read())

    rvc.set_models_dir(VOICES_DIR)
    print(f"[RVC] Voice '{base_name}' uploaded")

    return {"success": True, "voice": base_name}


@app.post("/api/convert")
async def convert_audio(
    audio: UploadFile = File(...),
    voice: str = Form(...),
    transpose: int = Form(0),
    f0_method: str = Form("rmvpe"),
    index_rate: float = Form(0.5),
    protect: float = Form(0.33),
    rms_mix_rate: float = Form(0.25),
    filter_radius: int = Form(3),
    resample_sr: int = Form(0),
):
    if f0_method not in ("pm", "harvest", "crepe", "rmvpe"):
        raise HTTPException(400, "f0_method must be pm, harvest, crepe, or rmvpe")
    if not (0.0 <= index_rate <= 1.0):
        raise HTTPException(400, "index_rate must be between 0.0 and 1.0")
    if not (0.0 <= protect <= 0.5):
        raise HTTPException(400, "protect must be between 0.0 and 0.5")
    if not (0.0 <= rms_mix_rate <= 1.0):
        raise HTTPException(400, "rms_mix_rate must be between 0.0 and 1.0")
    if not (0 <= filter_radius <= 7):
        raise HTTPException(400, "filter_radius must be between 0 and 7")
    if resample_sr != 0 and not (16000 <= resample_sr <= 48000):
        raise HTTPException(400, "resample_sr must be 0 or between 16000 and 48000")

    voice_dir = os.path.join(VOICES_DIR, voice)
    if not os.path.isdir(voice_dir):
        raise HTTPException(404, f"Voice '{voice}' not found")

    pth_files = [f for f in os.listdir(voice_dir) if f.endswith(".pth")]
    if not pth_files:
        raise HTTPException(404, f"No .pth file found for voice '{voice}'")
    pth_path = os.path.join(voice_dir, pth_files[0])
    version = _detect_model_version(pth_path)

    print(f"[RVC] Loading voice '{voice}' as {version}: {pth_path}")

    tmp_input = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_output = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

    def cleanup():
        for p in (tmp_input.name, tmp_output.name if tmp_output else None):
            if p:
                try:
                    os.unlink(p)
                except OSError:
                    pass

    try:
        content = await audio.read()
        tmp_input.write(content)
        tmp_input.flush()
        tmp_input.close()
        tmp_output.close()

        try:
            info = sf.info(tmp_input.name)
            duration = info.duration
        except Exception:
            raise HTTPException(400, "Invalid audio file. Provide a valid WAV or MP3.")

        if duration > MAX_DURATION:
            raise HTTPException(
                413,
                f"Audio too long: {duration:.1f}s exceeds the maximum of {MAX_DURATION}s.",
            )

        rvc.load_model(voice, version=version)
        rvc.set_params(
            f0method=f0_method,
            f0up_key=transpose,
            index_rate=index_rate,
            protect=protect,
            rms_mix_rate=rms_mix_rate,
            filter_radius=filter_radius,
            resample_sr=resample_sr,
        )
        rvc.infer_file(tmp_input.name, tmp_output.name)

        rvc.unload_model()
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_name = f"converted_{voice}_{timestamp}.wav"
        out_path = os.path.join(OUTPUTS_DIR, out_name)

        os.rename(tmp_output.name, out_path)
        tmp_output = None

        out_size = os.path.getsize(out_path)
        if out_size == 0:
            raise HTTPException(500, "Conversion produced empty output")

        cleanup()

        return {
            "url": f"/outputs/{out_name}",
            "filename": out_name,
        }

    except HTTPException:
        cleanup()
        raise
    except Exception as e:
        cleanup()
        raise HTTPException(500, f"Conversion error: {str(e)}")
