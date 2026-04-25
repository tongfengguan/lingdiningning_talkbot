@echo off
:: Set current directory
cd /d "%~dp0"

echo [1/2] Launching Python Bot...
if not exist "venv\Scripts\python.exe" (
    echo Error: venv not found. Please run 'python -m venv venv'.
    pause
    exit /b
)
:: Start Bot in a new window
start "NingNing_Bot" cmd /c ".\venv\Scripts\activate && python main.py"

timeout /t 3

echo [2/2] Launching Cloudflare Tunnel...
:: Change the path if it is different
set "CF_PATH=D:\Software\Cloudflared\cloudflared.exe"

if exist "%CF_PATH%" (
    start "CF_Tunnel" cmd /c ""%CF_PATH%" tunnel --url http://127.0.0.1:8080"
) else (
    echo Error: %CF_PATH% not found.
)

echo ----------------------------------------------------
echo Done! 
echo 1. Check the Tunnel window for the https URL.
echo 2. Copy it to your NapCat HTTP Client config.
echo ----------------------------------------------------
pause
