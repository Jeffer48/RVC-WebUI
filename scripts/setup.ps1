<#
.SYNOPSIS
    RVC-WebUI environment setup script.
.DESCRIPTION
    Creates a Python 3.11 virtual environment and installs dependencies
    for CPU or CUDA (NVIDIA GPU) builds.
.PARAMETER Cpu
    Install PyTorch CPU version (works on any PC).
.PARAMETER Cuda
    Install PyTorch CUDA 12.4 version (requires NVIDIA GPU).
.EXAMPLE
    .\scripts\setup.ps1 -Cpu
    .\scripts\setup.ps1 -Cuda
#>

param(
    [switch]$Cpu,
    [switch]$Cuda
)

$ErrorActionPreference = "Stop"

if (-not $Cpu -and -not $Cuda) {
    Write-Error "You must specify -Cpu or -Cuda"
    Write-Host "Usage: .\scripts\setup.ps1 -Cpu    (for CPU-only)"
    Write-Host "Usage: .\scripts\setup.ps1 -Cuda   (for NVIDIA GPU)"
    exit 1
}

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location -LiteralPath $RootDir

Write-Host "=== RVC-WebUI Setup ===" -ForegroundColor Cyan

# Create virtual environment
if (-not (Test-Path -LiteralPath ".venv")) {
    Write-Host "[1/2] Creating virtual environment (Python 3.11)..." -ForegroundColor Yellow
    py -3.11 -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment. Is Python 3.11 installed?"
        exit 1
    }
} else {
    Write-Host "[1/2] Using existing .venv" -ForegroundColor Yellow
}

$Pip = ".venv\Scripts\pip.exe"
$Python = ".venv\Scripts\python.exe"

# Upgrade pip
& $Python -m pip install --upgrade pip --quiet

if ($Cpu) {
    Write-Host "[2/2] Installing dependencies (CPU)..." -ForegroundColor Yellow
    & $Pip install -r requirements-cpu.txt
} else {
    Write-Host "[2/2] Installing dependencies (CUDA 12.4)..." -ForegroundColor Yellow
    & $Pip install torch==2.12.0 torchaudio==2.11.0 --index-url https://download.pytorch.org/whl/cu124
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install CUDA PyTorch. Check your internet connection."
        exit 1
    }
    & $Pip install -r requirements-cuda.txt
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Dependency installation failed."
    exit 1
}

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
$device = & $Python -c "import torch; print('cuda' if torch.cuda.is_available() else 'cpu')"
Write-Host "PyTorch device: $device" -ForegroundColor $(if ($device -eq "cuda") { "Cyan" } else { "Yellow" })
Write-Host ""
Write-Host "Run 'start.bat' to launch the server." -ForegroundColor White
