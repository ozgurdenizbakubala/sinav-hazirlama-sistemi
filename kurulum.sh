#!/bin/bash
# Sinav Hazirlama Sistemi - Linux Kurulum Scripti

cd "$(dirname "$0")"

echo "================================================="
echo "  Sinav Hazirlama Sistemi - Kurulum"
echo "================================================="
echo ""
echo "  [1] Uygulamayi calistir"
echo "  [2] Masaustune kisayol olustur"
echo "  [3] Gerekli kutuphaneleri yukle"
echo "  [4] Cikis"
echo ""
read -p "Seciminiz (1-4): " SECIM

case $SECIM in
1)
    echo "Uygulama baslatiliyor..."
    python3 main.py
    ;;
2)
    echo "Kisayol olusturuluyor..."
    python3 kisayol_olustur.py
    ;;
3)
    echo "Kutuphaneler yukleniyor..."
    pip3 install Pillow reportlab opencv-python numpy
    echo "Tamamlandi!"
    ;;
4)
    exit 0
    ;;
*)
    echo "Gecersiz secim."
    ;;
esac
