# -*- coding: utf-8 -*-
"""
Görsel işleme modülü — Ekran görüntüsü odaklı, hafif versiyon.
EasyOCR kaldırıldı. Sadece Pillow kullanılır (OpenCV isteğe bağlı).
"""
import io
from PIL import Image, ImageTk

def resize_bytes(data: bytes, mw=800, mh=600) -> bytes:
    img = Image.open(io.BytesIO(data))
    img.thumbnail((mw, mh), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format=img.format or "PNG")
    return buf.getvalue()

def to_tk(data: bytes, mw=320, mh=240) -> ImageTk.PhotoImage:
    img = Image.open(io.BytesIO(data))
    img.thumbnail((mw, mh), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def to_tk_preview(data: bytes, mw: int, mh: int):
    try:
        img = Image.open(io.BytesIO(data))
        img.thumbnail((max(1,mw), max(1,mh)), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None
