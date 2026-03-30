@echo off
title Sinav Hazirlama Sistemi - Kurulum
cd /d "%~dp0"

:MENU
cls
echo =================================================
echo   Sinav Hazirlama Sistemi - Kurulum Menusu
echo =================================================
echo.
echo   [1] Uygulamayi calistir
echo   [2] Masaustune kisayol olustur
echo   [3] Gerekli kutuphaneleri yukle (pip)
echo   [4] .exe olustur (PyInstaller)
echo   [5] Cikis
echo.
set /p SECIM=Seciminiz (1-5): 

if "%SECIM%"=="1" goto CALISTIR
if "%SECIM%"=="2" goto KISAYOL
if "%SECIM%"=="3" goto KUTUPHANE
if "%SECIM%"=="4" goto EXE
if "%SECIM%"=="5" goto CIKIS

echo Gecersiz secim.
pause
goto MENU

:CALISTIR
cls
echo Uygulama baslatiliyor...
python main.py
if errorlevel 1 (
    echo.
    echo HATA: Uygulama baslatilamadi.
    echo Python yuklu mu? python --version komutunu deneyin.
)
pause
goto MENU

:KISAYOL
cls
echo Masaustune kisayol olusturuluyor...
python kisayol_olustur.py
pause
goto MENU

:KUTUPHANE
cls
echo Kutuphaneler yukleniyor...
echo.
pip install Pillow reportlab opencv-python numpy
echo.
echo Tamamlandi!
pause
goto MENU

:EXE
cls
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller yuklu degil, yukleniyor...
    pip install pyinstaller
)
echo.
echo .exe olusturuluyor, bekleyin...
python setup_exe.py
echo.
pause
goto MENU

:CIKIS
exit
