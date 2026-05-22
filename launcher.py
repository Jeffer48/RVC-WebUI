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

    print(f"[RVC] Working directory: {ROOT}")
    print(f"[RVC] Server ready at http://127.0.0.1:8000")
    threading.Timer(1.5, open_browser).start()
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
