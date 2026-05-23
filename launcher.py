import os
import sys
import threading
import webbrowser
from pathlib import Path

if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).parent
else:
    ROOT = Path(__file__).parent

os.chdir(ROOT)


def open_browser():
    webbrowser.open("http://127.0.0.1:8000")


def _check_gpu_mismatch():
    import ctypes

    try:
        ctypes.windll.LoadLibrary("nvcuda.dll")
        has_nvidia_driver = True
    except OSError:
        has_nvidia_driver = False

    import torch

    if has_nvidia_driver and not torch.cuda.is_available():
        print("=" * 60)
        print("  WARNING: NVIDIA GPU detected but PyTorch is CPU-only!")
        print("  You are running the CPU build on a machine with an")
        print("  NVIDIA graphics card. Download the CUDA build for")
        print("  much faster performance (GPU acceleration).")
        print("=" * 60)
        print()


if __name__ == "__main__":
    print("[RVC] Starting RVC WebUI...")

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

    import uvicorn

    if getattr(sys, "frozen", False):
        import torch.jit
        torch.jit.script = lambda fn: fn

    print("[RVC] Loading modules...")
    import backend.main

    _check_gpu_mismatch()

    print(f"[RVC] Working directory: {ROOT}")
    print(f"[RVC] Server ready at http://127.0.0.1:8000")
    threading.Timer(1.5, open_browser).start()
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
