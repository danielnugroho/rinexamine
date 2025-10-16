@echo off
REM Build script for RINEX Examiner on Windows
REM This script automates the PyInstaller build process

echo ============================================================
echo RINEX Examiner - Build Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6+ and try again
    pause
    exit /b 1
)

echo Step 1: Checking if PyInstaller is installed...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
) else (
    echo ✓ PyInstaller is installed
)

echo.
echo Step 2: Checking if hatanaka is installed (for CRX support)...
pip show hatanaka >nul 2>&1
if errorlevel 1 (
    echo Hatanaka not found. Do you want to install it? (Y/N)
    echo (If you choose N, CRX files won't be supported in the executable)
    set /p install_hatanaka=Install hatanaka? 
    if /i "%install_hatanaka%"=="Y" (
        pip install hatanaka
        if errorlevel 1 (
            echo WARNING: Failed to install hatanaka
            echo CRX support will not be available
        ) else (
            echo ✓ Hatanaka installed
        )
    ) else (
        echo Skipping hatanaka installation
    )
) else (
    echo ✓ Hatanaka is installed
)

echo.
echo Step 3: Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec
echo ✓ Cleaned

echo.
echo Step 4: Building executable...
echo This may take 1-3 minutes...
echo.

REM Build using the spec file for better control
if exist rinexamine.spec (
    echo Using custom spec file...
    pyinstaller rinexamine.spec
) else (
    echo Using default build options...
    pyinstaller --onefile --windowed --name="rinexamine" --hidden-import=hatanaka --collect-all hatanaka rinexamine.py
)

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Build failed!
    echo ============================================================
    echo Check the error messages above for details.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo SUCCESS! Build completed
echo ============================================================
echo.
echo Executable location: dist\rinexamine.exe
echo.
echo Next steps:
echo 1. Test: dist\rinexamine.exe
echo 2. Try loading different RINEX files
echo 3. Verify all features work correctly
echo.
echo File size:
dir dist\rinexamine.exe | find "rinexamine.exe"
echo.
echo ============================================================

pause
