@echo off
call .venv/Scripts/activate
@echo on
pyinstaller --noconfirm --onefile --console --icon "evealert/img/eve.ico" "main.py"
xcopy /E /I "evealert/img" "dist/evealert/img"
xcopy /E /I "evealert/sound" "dist/evealert/sound"
rd /S /Q build
