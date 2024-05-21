#!/bin/bash
source .venv/bin/activate
pyinstaller --noconfirm --onefile --console --icon "evealert/img/eve.ico" "main.py"
cp -r "evealert/img" "dist/evealert/img"
cp -r "evealert/sound" "dist/evealert/sound"
rm -rf build
