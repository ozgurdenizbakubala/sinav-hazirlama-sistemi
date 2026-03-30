# -*- coding: utf-8 -*-
"""
PDF font yönetimi — Türkçe karakter desteği.
DejaVuSans fontunu uygulama klasöründen yükler.
"""
import os, sys
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_registered = False

def _get_base():
    if getattr(sys, 'frozen', False):
        # PyInstaller: fontlar exe'nin yanında (_MEIPASS veya exe klasörü)
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass and os.path.exists(os.path.join(meipass, 'DejaVuSans.ttf')):
            return meipass
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def register_fonts():
    global _registered
    if _registered:
        return True

    base = _get_base()
    normal_path = os.path.join(base, "DejaVuSans.ttf")
    bold_path   = os.path.join(base, "DejaVuSans-Bold.ttf")

    fallbacks_normal = [
        normal_path,
        # Windows
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        # macOS
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    fallbacks_bold = [
        bold_path,
        # Windows
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
        # macOS
        "/Library/Fonts/Arial Bold.ttf",
    ]

    def try_register(name, paths):
        for p in paths:
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont(name, p))
                    return True
                except Exception:
                    continue
        return False

    ok_n = try_register("DejaVu",      fallbacks_normal)
    ok_b = try_register("DejaVu-Bold", fallbacks_bold)

    if not ok_b:
        # Bold yoksa normal fontu bold olarak da kaydet
        try_register("DejaVu-Bold", fallbacks_normal)

    _registered = ok_n
    return ok_n

def F(bold=False):
    """Font adı döndür — DejaVu yoksa Helvetica'ya düş."""
    if _registered:
        return "DejaVu-Bold" if bold else "DejaVu"
    return "Helvetica-Bold" if bold else "Helvetica"
