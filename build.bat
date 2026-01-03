@echo off
REM Build DictationFlow as a standalone executable

echo Building DictationFlow...

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run PyInstaller
pyinstaller dictationflow.spec --clean

echo.
echo Build complete! Executable is in dist\DictationFlow.exe
echo.
pause
