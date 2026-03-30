# -*- coding: utf-8 -*-
"""
Sınav Hazırlama Sistemi v4.2
Ana başlatıcı dosya.
"""
import sys, os

# PyInstaller ile paketlenince _MEIPASS içindeki dosyalara bak
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    # sys.path'e exe klasörünü de ekle (db.py, theme.py vb. için)
    EXE_DIR  = os.path.dirname(sys.executable)
    if EXE_DIR not in sys.path:
        sys.path.insert(0, EXE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import tkinter as tk
from tkinter import ttk

import db, theme
from theme import T, apply_ttk_style, make_btn, load_theme, save_theme
from auth import LoginWindow
from db import get_ayar, init_db

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sınav Hazırlama Sistemi")
        self.geometry("1400x860")
        self.minsize(1100, 680)

        # İkon ayarla
        self._set_icon()
        init_db()
        self._apply()
        self._build()

    def _set_icon(self):
        import os, sys
        if getattr(sys, 'frozen', False):
            base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            base = os.path.dirname(os.path.abspath(__file__))

        ico = os.path.join(base, "logo.ico")
        png = os.path.join(base, "logo.png")
        try:
            from PIL import ImageTk, Image
            if sys.platform == "win32" and os.path.exists(ico):
                self.iconbitmap(ico)
            elif os.path.exists(png):
                img = Image.open(png).resize((32, 32), Image.LANCZOS)
                self._icon_img = ImageTk.PhotoImage(img)
                self.iconphoto(True, self._icon_img)
        except Exception:
            pass

    def _apply(self):
        t = T(); self.configure(bg=t["bg"]); apply_ttk_style()

    def _build(self):
        t = T()
        hdr = tk.Frame(self, bg=t["header"], height=56)
        hdr.pack(fill="x"); hdr.pack_propagate(False)

        tk.Label(hdr, text="📚  Sınav Hazırlama Sistemi",
                 font=("Segoe UI",16,"bold"),
                 bg=t["header"], fg=t["header_fg"]).pack(side="left", padx=20, pady=12)

        ad = get_ayar("ogretmen_ad") or ""
        if ad:
            tk.Label(hdr, text=f"👤  {ad}",
                     font=("Segoe UI",10),
                     bg=t["header"], fg=t["subtext"]).pack(side="right", padx=20)

        tema_icon = "☀️" if theme.current_theme == "dark" else "🌙"
        tema_text = f"{tema_icon}  {'Açık Tema' if theme.current_theme == 'dark' else 'Koyu Tema'}"
        self.tema_btn = tk.Button(hdr, text=tema_text,
                                   font=("Segoe UI",9),
                                   bg=t["header"], fg=t["header_fg"],
                                   relief="flat", cursor="hand2", bd=0,
                                   activebackground=t["panel"],
                                   activeforeground=t["header_fg"],
                                   command=self._tema)
        self.tema_btn.pack(side="right", padx=14)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=10)

        from ui_sorubankasi import DatabaseTab
        from ui_sinav import SinavTab

        self.tab_db    = DatabaseTab(self.nb, self)
        self.tab_sinav = SinavTab(self.nb, self)
        self.tab_hakkinda = HakkindaTab(self.nb)

        self.nb.add(self.tab_db,       text="   🗂️  Soru Bankası   ")
        self.nb.add(self.tab_sinav,    text="   📝  Sınav Hazırla   ")
        self.nb.add(self.tab_hakkinda, text="   ℹ️  Hakkında   ")
        self.nb.bind("<<NotebookTabChanged>>",
                     lambda e: self.tab_sinav.refresh_konular())

    def _tema(self):
        theme.toggle()
        save_theme()  # Temayı kaydet
        for w in self.winfo_children(): w.destroy()
        self._apply(); self._build()
        self.tab_db.load_siniflar()


def main():
    init_db()
    load_theme()  # Kaydedilmiş temayı yükle
    login = LoginWindow()

    # Giriş ekranına da ikon ekle
    ico = os.path.join(BASE_DIR, "logo.ico")
    png = os.path.join(BASE_DIR, "logo.png")
    try:
        if os.path.exists(ico):
            login.iconbitmap(ico)
        elif os.path.exists(png):
            from PIL import ImageTk, Image
            img = Image.open(png).resize((32,32), Image.LANCZOS)
            login._icon = ImageTk.PhotoImage(img)
            login.iconphoto(True, login._icon)
    except Exception:
        pass

    login.mainloop()
    if not login.result:
        return

    app = MainApp()
    app.mainloop()




# ── Hakkında Sekmesi ──────────────────────────────────────────────────────────
class HakkindaTab(tk.Frame):
    def __init__(self, parent):
        t = T()
        super().__init__(parent, bg=t["bg"])
        self._build()

    def _build(self):
        import sys as _sys
        t = T()

        # Üst başlık
        top = tk.Frame(self, bg=t["header"])
        top.pack(fill="x")
        try:
            from PIL import Image as _Img, ImageTk as _ITk
            _base = getattr(_sys, "_MEIPASS",
                    os.path.dirname(os.path.abspath(__file__)))                     if getattr(_sys, "frozen", False)                     else os.path.dirname(os.path.abspath(__file__))
            _p = os.path.join(_base, "logo.png")
            if os.path.exists(_p):
                _ph = _ITk.PhotoImage(_Img.open(_p).resize((72,72), _Img.LANCZOS))
                self._logo = _ph
                tk.Label(top, image=_ph, bg=t["header"]).pack(pady=(18,4))
        except Exception:
            tk.Label(top, text="📚", font=("Segoe UI",38),
                     bg=t["header"], fg=t["accent"]).pack(pady=(18,4))

        tk.Label(top, text="Sınav Hazırlama Sistemi",
                 font=("Segoe UI",18,"bold"),
                 bg=t["header"], fg=t["header_fg"]).pack()
        tk.Label(top, text="Versiyon 4.0",
                 font=("Segoe UI",9),
                 bg=t["header"], fg=t["subtext"]).pack(pady=(2,16))

        # Scrollable içerik
        cf = tk.Frame(self, bg=t["bg"])
        cf.pack(fill="both", expand=True)
        vsb = ttk.Scrollbar(cf)
        canvas = tk.Canvas(cf, bg=t["bg"], highlightthickness=0,
                           yscrollcommand=vsb.set)
        vsb.config(command=canvas.yview)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        body = tk.Frame(canvas, bg=t["bg"])
        win  = canvas.create_window((0,0), window=body, anchor="nw")
        body.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        def bolum(ikon, baslik):
            f = tk.Frame(body, bg=t["bg"])
            f.pack(fill="x", padx=50, pady=(18,4))
            tk.Label(f, text=f"{ikon}  {baslik}",
                     font=("Segoe UI",12,"bold"),
                     bg=t["bg"], fg=t["text"]).pack(anchor="w")
            tk.Frame(body, bg=t["border"], height=1).pack(
                fill="x", padx=50, pady=(0,6))

        def kart(ikon, baslik, aciklama, renk="btn_primary"):
            f = tk.Frame(body, bg=t["panel"],
                         highlightthickness=1,
                         highlightbackground=t["border"])
            f.pack(fill="x", padx=50, pady=3)
            tk.Label(f, text=f"{ikon}  {baslik}",
                     font=("Segoe UI",10,"bold"),
                     bg=t["panel"], fg=t[renk]).pack(anchor="w", padx=14, pady=(8,2))
            tk.Label(f, text=aciklama,
                     font=("Segoe UI",9),
                     bg=t["panel"], fg=t["subtext"],
                     wraplength=700, justify="left").pack(
                         anchor="w", padx=14, pady=(0,8))

        # ── Özellikler ──
        bolum("✨", "Özellikler")
        for ikon, acik in [
            ("📷", "Ekran görüntüsü veya dosyadan soru ekleme (pano desteği dahil)"),
            ("🗂️", "Sınıf ve konu bazlı soru bankası yönetimi"),
            ("📝", "Sürükle-bırak PDF sınav düzenleyici"),
            ("📐", "Her soru için özelleştirilebilir çözüm alanı ve noktalı satırlar"),
            ("📋", "Otomatik cevap anahtarı ve çözüm PDF'i"),
            ("🌙", "Koyu / Açık tema (tercih kaydedilir)"),
            ("🔐", "Şifreli giriş + 32 adet kurtarma kodu"),
            ("🔡", "Türkçe karakter destekli PDF (DejaVu font)"),
            ("🎲", "Sınıf ve konu bazlı rastgele soru seçimi"),
            ("🐧", "Windows ve Linux desteği"),
        ]:
            kart(ikon, acik, "")

        # ── Teknolojiler ──
        bolum("🛠️", "Kullanılan Teknolojiler")
        for tech, amac in [
            ("Python 3.10+", "Ana programlama dili"),
            ("Tkinter",      "Masaüstü arayüzü"),
            ("SQLite3",      "Yerel veritabanı"),
            ("Pillow",       "Görsel işleme"),
            ("ReportLab",    "PDF oluşturma"),
            ("OpenCV",       "Görsel bölge tespiti"),
            ("DejaVu Sans",  "Türkçe destekli font"),
        ]:
            kart("⚙️", tech, amac)

        # ── AI ──
        bolum("🤖", "Yapay Zeka")
        kart("🧠", "Claude Opus 4.6 (Anthropic)",
             "Bu proje Anthropic'in Claude Opus 4.6 yapay zeka modeli yardımıyla geliştirilmiştir.",
             "btn_purple")

        # ── Lisans ──
        bolum("⚖️", "Lisans — CC BY-NC 4.0")
        kart("✅", "İzin Verilenler",
             "Kullanabilir, değiştirebilir, paylaşabilirsiniz.", "btn_success")
        kart("❌", "Yasak — Ticari Kullanım",
             "Bu yazılım ticari amaçla KULLANILAMAZ. Satış, ücretli dağıtım veya ticari ürüne entegrasyon yasaktır.",
             "btn_danger")

        # ── İletişim ──
        bolum("📬", "İletişim")
        kart("📧", "E-posta", "denizbakubala@gmail.com")
        kart("🐙", "GitHub",
             "github.com — Kaynak koda katkıda bulunmak için GitHub üzerinden Pull Request açabilirsiniz.")

        tk.Frame(body, height=30, bg=t["bg"]).pack()  # alt boşluk

if __name__ == "__main__":
    main()
