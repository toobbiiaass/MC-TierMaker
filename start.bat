@echo off
setlocal

set PYFILE=TierMaker.py

python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed.
    pause
    exit /b
)

python -m pip install --upgrade pip

python -m pip install requests pillow numpy

IF NOT EXIST "%PYFILE%" (
    echo The file %PYFILE% was not found!
    pause
    exit /b
)

echo Starting %PYFILE%...
python "%PYFILE%"

pause
