@echo off
REM ============================================================
REM  Resume AI Assistant - one-click launcher
REM  Starts the backend (FastAPI + Ollama) and a public tunnel.
REM ============================================================

cd /d "%~dp0"

echo ============================================================
echo  Starting Resume AI Assistant...
echo  Make sure Ollama is running (qwen3:8b).
echo ============================================================
echo.

REM 1) Start the backend in its own window (serves frontend + API on port 8000)
start "Resume AI - Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn api:app --port 8000"

REM Give the backend a few seconds to boot before opening the tunnel
timeout /t 6 /nobreak >nul

REM 2) Start the public Cloudflare tunnel in its own window
REM    The public https://xxx.trycloudflare.com link appears in that window.
set "CLOUDFLARED=cloudflared"
if exist "%ProgramFiles(x86)%\cloudflared\cloudflared.exe" set "CLOUDFLARED=%ProgramFiles(x86)%\cloudflared\cloudflared.exe"
if exist "%ProgramFiles%\cloudflared\cloudflared.exe" set "CLOUDFLARED=%ProgramFiles%\cloudflared\cloudflared.exe"
start "Resume AI - Public Link" cmd /k ""%CLOUDFLARED%" tunnel --url http://localhost:8000"

echo.
echo Two windows opened:
echo   1) Backend  - keep it running
echo   2) Public Link - look for the https://...trycloudflare.com URL
echo.
echo Close those windows (or press Ctrl+C in them) to stop the server.
pause
