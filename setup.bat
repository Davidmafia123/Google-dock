@echo off
cls
echo --- [GDA] Setting up Google Dorking Automation Tool for Windows ---
echo.

:: 1. Check for Python 3
echo [1/5] Checking for Python 3...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your system's PATH.
    echo Please install Python 3.10 or higher and ensure it's added to PATH.
    pause
    exit /b 1
)
echo Python found.
echo.

:: 2. Create virtual environment
set VENV_DIR=venv
if exist "%VENV_DIR%" (
    echo [2/5] Virtual environment '%VENV_DIR%' already exists. Skipping creation.
) else (
    echo [2/5] Creating Python virtual environment in '.\%VENV_DIR%'...
    python -m venv %VENV_DIR%
)
echo.

:: 3. Activate virtual environment and upgrade pip
echo [3/5] Activating virtual environment and upgrading pip...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip >nul
echo Pip upgraded.
echo.

:: 4. Install project dependencies
echo [4/5] Installing project dependencies from pyproject.toml...
pip install -e ".[dev]"
echo Dependencies installed.
echo.

:: 5. Install Playwright browsers
echo [5/5] Installing Playwright browser binaries (this might take a few minutes)...
playwright install
echo Playwright browsers installed.
echo.

echo ---------------------------------
echo --- [GDA] Setup Complete! ---
echo ---------------------------------
echo.
echo To run the tool from a new terminal, first activate the virtual environment:
echo   call %VENV_DIR%\Scripts\activate.bat
echo.
echo Then, you can run the interactive runner:
echo   python runner.py
echo.
echo Or use the direct CLI command:
echo   gda --help
echo.
pause
