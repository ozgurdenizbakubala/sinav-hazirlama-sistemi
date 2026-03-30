@echo off
title Sinav Hazirlama Sistemi - Build
cd /d "%~dp0"

echo =================================================
echo   Sinav Hazirlama Sistemi - Installer Olusturucu
echo =================================================
echo.
echo Bu script asagidakileri yapacak:
echo   1. PyInstaller ile .exe olustur
echo   2. NSIS ile kurulum paketi olustur
echo.
echo Gereksinimler:
echo   - Python + pip (yuklu olmali)
echo   - NSIS (https://nsis.sourceforge.io) yuklu olmali
echo.
pause

echo.
echo [1/4] Gerekli kutuphaneler kontrol ediliyor...
pip install Pillow reportlab opencv-python numpy pyinstaller --quiet
echo Tamam.

echo.
echo [2/4] .exe olusturuluyor (5-10 dakika surebilir)...
python setup_exe.py
if errorlevel 1 (
    echo HATA: exe olusturulamadi!
    pause
    exit /b 1
)

echo.
echo [3/4] NSIS ile installer olusturuluyor...
where makensis >nul 2>&1
if errorlevel 1 (
    echo UYARI: NSIS bulunamadi.
    echo NSIS'i indirin: https://nsis.sourceforge.io/Download
    echo NSIS kurulduktan sonra bu scripti tekrar calistirin.
    pause
    exit /b 1
)
makensis installer.nsi
if errorlevel 1 (
    echo HATA: NSIS hatasi!
    pause
    exit /b 1
)

echo.
echo [4/4] Tamamlandi!
echo.
echo =================================================
echo   SinavHazirlamaSistemi_Kurulum.exe olusturuldu!
echo   Bu dosyayi ogretmenlere dagitabilirsiniz.
echo =================================================
echo.
pause
