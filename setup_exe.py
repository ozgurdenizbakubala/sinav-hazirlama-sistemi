# -*- coding: utf-8 -*-
"""PyInstaller ile .exe olusturucu."""
import subprocess, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))

def sep(src, dst="."): return f"{src}{os.pathsep}{dst}"

data_files = [
    sep(os.path.join(BASE, "DejaVuSans.ttf")),
    sep(os.path.join(BASE, "DejaVuSans-Bold.ttf")),
    sep(os.path.join(BASE, "logo.ico")),
    sep(os.path.join(BASE, "logo.png")),
]

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm", "--clean",
    "--onedir",
    "--windowed",
    "--name", "SinavHazirlamaSistemi",
    "--icon", os.path.join(BASE, "logo.ico"),
    "--hidden-import", "PIL._tkinter_finder",
    "--hidden-import", "reportlab.graphics",
    "--hidden-import", "reportlab.lib.pagesizes",
    "--hidden-import", "cv2",
]
for d in data_files:
    cmd += ["--add-data", d]

cmd.append(os.path.join(BASE, "main.py"))

print("PyInstaller calistiriliyor...")
result = subprocess.run(cmd, cwd=BASE)
if result.returncode == 0:
    dist = os.path.join(BASE, "dist", "SinavHazirlamaSistemi")
    print(f"\nEXE basariyla olusturuldu!")
    print(f"Konum: {dist}")
    print("NOT: sinav.db dosyasini da o klasore kopyalayin.")
else:
    print("\nHata! PyInstaller yuklu mu? pip install pyinstaller")
