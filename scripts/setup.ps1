# Shadowing App Setup Script for Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Shadowing App Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

# Check Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Node.js not found. Please install Node.js 20+" -ForegroundColor Red
    exit 1
}

# Check FFmpeg
$ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] FFmpeg: $ffmpegVersion" -ForegroundColor Green
} else {
    Write-Host "[WARNING] FFmpeg not found. Installing via winget..." -ForegroundColor Yellow
    winget install FFmpeg
}

# Check Ollama (optional)
$ollamaVersion = ollama --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Ollama: $ollamaVersion" -ForegroundColor Green
} else {
    Write-Host "[INFO] Ollama not found. LLM evaluation will use basic mode." -ForegroundColor Yellow
    Write-Host "       To install: winget install Ollama.Ollama" -ForegroundColor Yellow
}

# Setup backend
Write-Host "`nSetting up backend..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "..\backend"
Push-Location $backendPath

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"
pip install -r requirements.txt

Pop-Location

# Setup frontend
Write-Host "`nSetting up frontend..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "..\frontend"
Push-Location $frontendPath

Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
npm install

Pop-Location

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nTo start the application:" -ForegroundColor Yellow
Write-Host "1. Backend:  cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "2. Frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "`nOpen http://localhost:5173 in your browser" -ForegroundColor Cyan
