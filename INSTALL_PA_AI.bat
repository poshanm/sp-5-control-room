@echo off
title PA AI System - Installer v1.0
color 0A
setlocal enabledelayedexpansion

:: ============================================================
::  PA AI SYSTEM - ONE CLICK INSTALLER
::  SP5 Screening Plant - Electrical Department
:: ============================================================

echo.
echo  ============================================================
echo   PA AI SYSTEM - INSTALLER v1.0
echo   SP5 Screening Plant
echo  ============================================================
echo.
echo  Yeh installer PA System ke liye sab kuch setup karega:
echo    [1] Python check / install guide
echo    [2] Required packages install
echo    [3] Files copy to C:\PA_AI
echo    [4] Windows Startup me add
echo.
echo  ============================================================
echo.
pause

:: ============================================================
:: STEP 1: ADMIN CHECK
:: ============================================================
echo.
echo  [CHECK] Administrator permission check kar raha hai...
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo.
    echo  [ERROR] Administrator mode mein nahi chal raha!
    echo.
    echo  Kya karna hai:
    echo    - Yeh file pe Right Click karo
    echo    - "Run as administrator" select karo
    echo.
    pause
    exit /b 1
)
echo  [OK] Administrator mode confirmed.

:: ============================================================
:: STEP 2: PYTHON CHECK
:: ============================================================
echo.
echo  [CHECK] Python install check kar raha hai...
python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo.
    echo  [ERROR] Python nahi mila!
    echo.
    echo  Python install karo:
    echo    1. https://www.python.org/downloads/
    echo    2. Python 3.11 download karo
    echo    3. Install karte waqt "Add Python to PATH" tick karo
    echo    4. Install complete hone ke baad DOBARA yeh installer chalao
    echo.
    start https://www.python.org/downloads/release/python-3119/
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% mila.

:: ============================================================
:: STEP 3: PIP UPGRADE
:: ============================================================
echo.
echo  [SETUP] pip upgrade kar raha hai...
python -m pip install --upgrade pip --quiet
echo  [OK] pip ready.

:: ============================================================
:: STEP 4: PACKAGES INSTALL
:: ============================================================
echo.
echo  [INSTALL] Required Python packages install ho rahe hain...
echo  (Pehli baar mein thoda time lagega - internet connection chahiye)
echo.

set PACKAGES=pandas pyserial requests playsound psutil pystray Pillow pycaw comtypes python-telegram-bot openpyxl

for %%p in (%PACKAGES%) do (
    echo    Installing: %%p
    python -m pip install %%p --quiet 2>nul
    if !errorLevel! EQU 0 (
        echo    [OK] %%p
    ) else (
        echo    [WARN] %%p install mein problem - manually check karna
    )
)

echo.
echo  [OK] Packages installation complete.

:: ============================================================
:: STEP 5: FOLDER SETUP
:: ============================================================
echo.
echo  [SETUP] C:\PA_AI folder bana raha hai...

if not exist "C:\PA_AI" mkdir "C:\PA_AI"
if not exist "C:\PA_AI\audio" mkdir "C:\PA_AI\audio"
if not exist "C:\PA_AI\audio\bell" mkdir "C:\PA_AI\audio\bell"
if not exist "C:\PA_AI\audio\canteen" mkdir "C:\PA_AI\audio\canteen"
if not exist "C:\PA_AI\audio\canteen\9AM" mkdir "C:\PA_AI\audio\canteen\9AM"
if not exist "C:\PA_AI\audio\canteen\10AM" mkdir "C:\PA_AI\audio\canteen\10AM"
if not exist "C:\PA_AI\audio\canteen\5PM" mkdir "C:\PA_AI\audio\canteen\5PM"
if not exist "C:\PA_AI\audio\canteen\0530PM" mkdir "C:\PA_AI\audio\canteen\0530PM"
if not exist "C:\PA_AI\audio\emergency" mkdir "C:\PA_AI\audio\emergency"
if not exist "C:\PA_AI\audio\shift1" mkdir "C:\PA_AI\audio\shift1"
if not exist "C:\PA_AI\audio\shift2" mkdir "C:\PA_AI\audio\shift2"
if not exist "C:\PA_AI\audio\shift3" mkdir "C:\PA_AI\audio\shift3"
if not exist "C:\PA_AI\logs" mkdir "C:\PA_AI\logs"
if not exist "C:\PA_AI\texts" mkdir "C:\PA_AI\texts"
if not exist "C:\PA_AI\texts\canteen" mkdir "C:\PA_AI\texts\canteen"
if not exist "C:\PA_AI\texts\shift1" mkdir "C:\PA_AI\texts\shift1"
if not exist "C:\PA_AI\texts\shift2" mkdir "C:\PA_AI\texts\shift2"
if not exist "C:\PA_AI\texts\shift3" mkdir "C:\PA_AI\texts\shift3"
if not exist "C:\PA_AI\texts\emergency" mkdir "C:\PA_AI\texts\emergency"
if not exist "C:\PA_AI\dashboard" mkdir "C:\PA_AI\dashboard"
if not exist "C:\PA_AI\xml" mkdir "C:\PA_AI\xml"

echo  [OK] Folder structure ready.

:: ============================================================
:: STEP 6: FILES COPY
:: ============================================================
echo.
echo  [COPY] PA_AI files copy ho rahe hain C:\PA_AI mein...

:: Installer ke saath wala PA_AI folder dhundho
set "SOURCEDIR=%~dp0PA_AI"

if not exist "%SOURCEDIR%" (
    echo.
    echo  [ERROR] PA_AI folder nahi mila installer ke paas!
    echo  Ensure karo ki INSTALL_PA_AI.bat aur PA_AI folder ek saath hain.
    echo.
    pause
    exit /b 1
)

:: Saari files copy karo (subfolders ke saath)
xcopy "%SOURCEDIR%\*" "C:\PA_AI\" /E /Y /Q
if %errorLevel% EQU 0 (
    echo  [OK] Files copy complete.
) else (
    echo  [WARN] Kuch files copy nahi hui, manually check karo.
)

:: ============================================================
:: STEP 7: emergency.txt blank create karo agar nahi hai
:: ============================================================
if not exist "C:\PA_AI\texts\emergency.txt" (
    echo. > "C:\PA_AI\texts\emergency.txt"
    echo  [OK] emergency.txt created.
)

:: ============================================================
:: STEP 8: STARTUP SHORTCUT BANAO
:: ============================================================
echo.
echo  [SETUP] Windows Startup shortcut bana raha hai...

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "BATFILE=C:\PA_AI\PA_AUTO_START.bat"
set "SHORTCUT=%STARTUP%\PA_AI_AutoStart.lnk"

:: PA_AUTO_START.bat update karo naye PC ke liye
echo @echo off > "%BATFILE%"
echo cd C:\PA_AI >> "%BATFILE%"
echo start "" pythonw master_pa_controller.py >> "%BATFILE%"
echo start "" pythonw pa_tray_monitor.py >> "%BATFILE%"
echo start "" pythonw telegram_control.py >> "%BATFILE%"

:: PowerShell se shortcut banao
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%BATFILE%'; $s.WorkingDirectory = 'C:\PA_AI'; $s.Description = 'PA AI System AutoStart'; $s.Save()" 2>nul

if exist "%SHORTCUT%" (
    echo  [OK] Startup shortcut banaya: %SHORTCUT%
) else (
    echo  [WARN] Startup shortcut manually banana padega.
    echo         Yeh file shortcut banao Startup folder mein:
    echo         %BATFILE%
)

:: ============================================================
:: STEP 9: AZURE KEY CHECK
:: ============================================================
echo.
echo  ============================================================
echo   [IMPORTANT] AZURE TTS KEY CONFIGURE KARO
echo  ============================================================
echo.
echo  master_pa_controller.py mein AZURE_KEY update karna zaroori hai!
echo.
echo  File location: C:\PA_AI\master_pa_controller.py
echo  Line dhundho: AZURE_KEY = "..."
echo  Apni Azure key wahan paste karo.
echo.
echo  Telegram Token bhi check karo:
echo  File: C:\PA_AI\telegram_control.py
echo  Line: TOKEN = "..."
echo.

:: ============================================================
:: STEP 10: FINAL - SYSTEM START KARO?
:: ============================================================
echo  ============================================================
echo   INSTALLATION COMPLETE!
echo  ============================================================
echo.
echo  Summary:
echo    [OK] Python %PYVER%
echo    [OK] Packages installed
echo    [OK] Files in C:\PA_AI
echo    [OK] Startup shortcut added
echo.
echo  COM Port Check:
echo    - master_pa_controller.py mein COM4 set hai (relay ke liye)
echo    - Agar dusra COM port hai to change karo
echo.

choice /C YN /M "  Abhi PA System start karein?"
if %errorLevel% EQU 1 (
    echo.
    echo  [START] PA System start ho raha hai...
    cd C:\PA_AI
    start "" pythonw master_pa_controller.py
    start "" pythonw pa_tray_monitor.py
    start "" pythonw telegram_control.py
    echo  [OK] Scripts start ho gaye. Tray icon mein green circle dikhega.
) else (
    echo  [INFO] Manually start karne ke liye:
    echo         C:\PA_AI\PA_AUTO_START.bat chalao
)

echo.
echo  ============================================================
echo   Installation complete! Press any key to exit.
echo  ============================================================
echo.
pause
exit /b 0
