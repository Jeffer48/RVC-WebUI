# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH)  # noqa: F821

block_cipher = None

# Include rvc-python base models (downloaded at first run)
rvc_base = ROOT / ".venv" / "Lib" / "site-packages" / "rvc_python" / "base_model"
rvc_configs = ROOT / ".venv" / "Lib" / "site-packages" / "rvc_python" / "configs"

datas = [
    ("frontend", "frontend"),
]

if rvc_base.is_dir():
    datas.append((str(rvc_base), "rvc_python/base_model"))
if rvc_configs.is_dir():
    datas.append((str(rvc_configs), "rvc_python/configs"))

for pkg in ["rvc_python", "fairseq"]:
    pkg_path = ROOT / ".venv" / "Lib" / "site-packages" / pkg
    if pkg_path.is_dir():
        for f in pkg_path.rglob("*.py"):
            rel = f.relative_to(pkg_path.parent)
            parts = rel.parts
            if parts[0] == "rvc_python" and len(parts) > 1 and parts[1] in ("configs", "base_model"):
                continue
            datas.append((str(f), str(rel)))

a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "backend",
        "backend.main",
        "uvicorn.logging",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "PIL",
        "notebook",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="RVC-WebUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
)
