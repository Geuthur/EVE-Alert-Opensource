@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
set PYTHON_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
set PYTHON_INSTALLER=python-installer.exe
set "PYTHON_INSTALL_PATH=%ProgramFiles%\Python3.12"

REM Überprüfen der Python-Version
set "PYTHON_CHECK_FAILED=true"
python.exe --version > python_version_output.txt 2>&1
set /p PYTHON_VERSION=<python_version_output.txt
del python_version_output.txt
echo !PYTHON_VERSION!
if not "!PYTHON_VERSION!"=="" (
    echo !PYTHON_VERSION! | findstr /r /c:"Python 3\.1[012]" >nul
    if !ERRORLEVEL! == 0 (
        echo Using !PYTHON_VERSION!
        set "PYTHON_CHECK_FAILED=false"
        goto :FOUND_PYTHON
    )
)
echo Something went wrong with Python Version Checking.
timeout /t 2 >nul

if "%PYTHON_CHECK_FAILED%"=="true" (
    set /p INSTALL_PYTHON="Python 3.10 to 3.12 not found. Do you want to download and install Python 3.12? (yes/no): "
    REM User selected: "!INSTALL_PYTHON!"
    if /i "!INSTALL_PYTHON!"=="yes" (
        goto :INSTALL_PYTHON
    ) else (
        echo Installation aborted.
        pause
        exit /b
    )
)

:FOUND_PYTHON
if "%PYTHON_CHECK_FAILED%"=="true" (
    echo Failed to set the correct Python version.
    pause
    exit /b
) else (
    goto :INSTALL_ALERT
)

:INSTALL_PYTHON
echo Downloading Python...
powershell -Command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile %PYTHON_INSTALLER%"
echo Installing Python...
start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=1 TargetDir="%PYTHON_INSTALL_PATH%"
if %ERRORLEVEL% neq 0 (
    echo Python installation failed.
    del "%PYTHON_INSTALLER%"
    pause
    goto :INSTALL_ALERT
)
del "%PYTHON_INSTALLER%"

REM PATH nach Installation aktualisieren
set "PATH=%PYTHON_INSTALL_PATH%;%PYTHON_INSTALL_PATH%\Scripts;%PATH%"
echo PATH updated to include new Python installation

REM Sicherstellen, dass die richtige Python-Version im PATH ist
set "PATH=%~dp0.venv\Scripts;%PATH%"

:INSTALL_ALERT
@echo on
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --icon "evealert/img/eve.ico" "main.py"
xcopy /E /I "evealert/img" "dist/evealert/img"
xcopy /E /I "evealert/sound" "dist/evealert/sound"
rd /S /Q build
pause
