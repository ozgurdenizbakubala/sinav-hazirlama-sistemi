# -*- coding: utf-8 -*-
"""
Platform bağımsız kısayol oluşturucu.
Windows: .lnk (COM veya PowerShell)
Linux:   .desktop dosyası
"""
import os, sys, subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PY  = os.path.join(BASE_DIR, "main.py")
ICO_PATH = os.path.join(BASE_DIR, "logo.ico")
PNG_PATH = os.path.join(BASE_DIR, "logo.png")

# ── Windows ───────────────────────────────────────────────────────────────────
def kisayol_windows():
    DESKTOP  = os.path.join(os.path.expanduser("~"), "Desktop")
    SHORTCUT = os.path.join(DESKTOP, "Sinav Hazirlama.lnk")

    # pythonw.exe (konsolsuz)
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable

    # Yöntem 1: win32com
    try:
        import win32com.client
        shell    = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(SHORTCUT)
        shortcut.TargetPath      = pythonw
        shortcut.Arguments       = f'"{MAIN_PY}"'
        shortcut.WorkingDirectory = BASE_DIR
        if os.path.exists(ICO_PATH):
            shortcut.IconLocation = ICO_PATH
        shortcut.Description = "Sinav Hazirlama Sistemi"
        shortcut.Save()
        if os.path.exists(SHORTCUT):
            return True, SHORTCUT
    except Exception:
        pass

    # Yöntem 2: PowerShell
    icon_line = f'$s.IconLocation = "{ICO_PATH}";' if os.path.exists(ICO_PATH) else ""
    ps = f"""
$ws = New-Object -ComObject WScript.Shell
$s  = $ws.CreateShortcut('{SHORTCUT}')
$s.TargetPath      = '{pythonw}'
$s.Arguments       = '"{MAIN_PY}"'
$s.WorkingDirectory= '{BASE_DIR}'
{icon_line}
$s.Description     = 'Sinav Hazirlama Sistemi'
$s.Save()
"""
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                       capture_output=True)
    if r.returncode == 0 and os.path.exists(SHORTCUT):
        return True, SHORTCUT
    return False, SHORTCUT

# ── Linux ─────────────────────────────────────────────────────────────────────
def kisayol_linux():
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    # Eğer masaüstü Türkçe ise
    if not os.path.exists(desktop_dir):
        desktop_dir = os.path.join(os.path.expanduser("~"), "Masaüstü")
    if not os.path.exists(desktop_dir):
        desktop_dir = os.path.expanduser("~")

    desktop_file = os.path.join(desktop_dir, "sinav-hazirlama.desktop")
    python_exe   = sys.executable

    icon = PNG_PATH if os.path.exists(PNG_PATH) else ""

    content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Sınav Hazırlama Sistemi
Comment=Öğretmenler için sınav hazırlama uygulaması
Exec={python_exe} {MAIN_PY}
Icon={icon}
Path={BASE_DIR}
Terminal=false
Categories=Education;
"""
    try:
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.write(content)
        # Çalıştırılabilir yap
        os.chmod(desktop_file, 0o755)
        # ~/.local/share/applications/ a da kopyala (uygulama menüsü için)
        apps_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
        os.makedirs(apps_dir, exist_ok=True)
        import shutil
        shutil.copy2(desktop_file, os.path.join(apps_dir, "sinav-hazirlama.desktop"))
        return True, desktop_file
    except Exception as e:
        return False, str(e)

# ── Ana ───────────────────────────────────────────────────────────────────────
def main():
    print("Kısayol oluşturuluyor...")
    print(f"  Platform: {sys.platform}")
    print()

    if sys.platform == "win32":
        ok, path = kisayol_windows()
    else:
        ok, path = kisayol_linux()

    if ok:
        print("=" * 50)
        print("BAŞARILI!")
        print(f"Kısayol oluşturuldu: {path}")
        if sys.platform != "win32":
            print("Masaüstü ve uygulama menüsüne eklendi.")
        print("=" * 50)
    else:
        print("=" * 50)
        print("BAŞARISIZ. Manuel oluşturma:")
        if sys.platform == "win32":
            print(f"  Hedef: pythonw.exe")
            print(f"  Bağımsız değişken: \"{MAIN_PY}\"")
        else:
            print(f"  python3 {MAIN_PY}")
        print("=" * 50)

if __name__ == "__main__":
    main()
    input("\nDevam etmek için Enter'a basın...")
