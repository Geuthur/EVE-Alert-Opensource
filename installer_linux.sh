#!/bin/bash
if ! command -v python &> /dev/null
then
    echo "Python is not installed."
    exit
fi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --icon "evealert/img/eve.ico" "main.py"
cp -r "evealert/img" "dist/evealert/img"
cp -r "evealert/sound" "dist/evealert/sound"
rm -rf build
