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
    import uvicorn

    print(f"[RVC] Working directory: {ROOT}")
    print(f"[RVC] Open http://127.0.0.1:8000 in your browser")
    threading.Timer(1.5, open_browser).start()
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
