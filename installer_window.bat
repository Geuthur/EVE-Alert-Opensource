@echo off
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed.
    pause
    exit /b
)
@echo on
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --icon "evealert/img/eve.ico" "main.py"
xcopy /E /I "evealert/img" "dist/evealert/img"
xcopy /E /I "evealert/sound" "dist/evealert/sound"
rd /S /Q build
pause
