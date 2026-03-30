# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
from theme import T, make_btn, make_entry
from db import (get_ayar, set_ayar, hash_pw, uret_kurtarma_kodlari,
                kurtarma_kodu_gecerli, kurtarma_kodu_kullan)

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sınav Hazırlama Sistemi")
        self.resizable(False, False)
        self.configure(bg=T()["bg"])
        self.result = False
        self._check()

    def _center(self, w=440, h=500):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _clear(self):
        for w in self.winfo_children(): w.destroy()

    def _header(self, title, subtitle=""):
        t = T()
        f = tk.Frame(self, bg=t["header"])
        f.pack(fill="x")
        # Logo görseli varsa göster, yoksa emoji
        logo_shown = False
        try:
            import os, sys
            from PIL import Image as PilImage, ImageTk
            _base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(_base, "logo.png")
            if os.path.exists(logo_path):
                pil_img = PilImage.open(logo_path).resize((56, 56), PilImage.LANCZOS)
                self._logo_ph = ImageTk.PhotoImage(pil_img)
                tk.Label(f, image=self._logo_ph, bg=t["header"]).pack(pady=(16,4))
                logo_shown = True
        except Exception:
            pass
        if not logo_shown:
            tk.Label(f, text="📚", font=("Segoe UI", 28),
                     bg=t["header"], fg=t["accent"]).pack(pady=(20,4))
        tk.Label(f, text=title, font=("Segoe UI", 16, "bold"),
                 bg=t["header"], fg=t["header_fg"]).pack(pady=(0,4))
        if subtitle:
            tk.Label(f, text=subtitle, font=("Segoe UI", 9),
                     bg=t["header"], fg=t["subtext"]).pack(pady=(0,16))
        else:
            tk.Frame(f, height=16, bg=t["header"]).pack()

    def _body(self):
        t = T()
        b = tk.Frame(self, bg=t["bg"], padx=36, pady=24)
        b.pack(fill="both", expand=True)
        return b

    def _check(self):
        if not get_ayar("pw_hash"):
            self._ilk_kurulum()
        else:
            self._giris_ekrani()

    # ── İlk Kurulum ──────────────────────────────────────────────────────────
    def _ilk_kurulum(self):
        self._clear(); self._center(460, 560)
        t = T()
        self._header("Hoş Geldiniz!", "İlk kullanım — hesabınızı oluşturun")
        body = self._body()

        fields = [
            ("👤  Adınız Soyadınız", "ent_ad", None),
            ("🔒  Şifre (en az 4 karakter)", "ent_pw", "*"),
            ("🔒  Şifre Tekrar", "ent_pw2", "*"),
        ]
        for label_text, attr, show in fields:
            tk.Label(body, text=label_text, font=("Segoe UI",10,"bold"),
                     bg=t["bg"], fg=t["text"]).pack(anchor="w", pady=(8,2))
            kw = {}; kw["show"] = show if show else None
            e = make_entry(body)
            if show: e.config(show=show)
            e.pack(fill="x", ipady=7)
            setattr(self, attr, e)

        self.ent_ad.focus()
        self.lbl_err = tk.Label(body, text="", font=("Segoe UI",9),
                                bg=t["bg"], fg=t["btn_danger"])
        self.lbl_err.pack(pady=6)

        make_btn(body, "✅  Hesabı Oluştur", "btn_success",
                 self._kayit).pack(fill="x", ipady=10, pady=(4,0))

    def _kayit(self):
        ad  = self.ent_ad.get().strip()
        pw  = self.ent_pw.get()
        pw2 = self.ent_pw2.get()
        if not ad:       self.lbl_err.config(text="Ad Soyad boş olamaz!"); return
        if len(pw) < 4:  self.lbl_err.config(text="Şifre en az 4 karakter olmalı!"); return
        if pw != pw2:    self.lbl_err.config(text="Şifreler eşleşmiyor!"); return
        set_ayar("ogretmen_ad", ad)
        set_ayar("pw_hash", hash_pw(pw))
        self._kurtarma_goster(uret_kurtarma_kodlari())

    # ── Kurtarma Kodları ─────────────────────────────────────────────────────
    def _kurtarma_goster(self, kodlar):
        self._clear(); self._center(560, 680)
        t = T()
        self._header("🔐  Kurtarma Kodlarınız",
                     "Bu kodları güvenli bir yere kaydedin — her kod bir kez kullanılabilir")
        body = self._body()
        body.config(padx=20)

        grid = tk.Frame(body, bg=t["bg"]); grid.pack(pady=(0,16))
        for i, k in enumerate(kodlar):
            r, c = divmod(i, 4)
            lbl = tk.Label(grid, text=k, font=("Courier New", 10, "bold"),
                           bg=t["panel"], fg=t["accent"],
                           relief="flat", bd=0, padx=10, pady=6,
                           highlightthickness=1,
                           highlightbackground=t["border"])
            lbl.grid(row=r, column=c, padx=3, pady=3)

        def kopyala():
            self.clipboard_clear()
            self.clipboard_append("\n".join(kodlar))
            messagebox.showinfo("Kopyalandı", "32 kod panoya kopyalandı!")

        make_btn(body, "📋  Kodları Panoya Kopyala", "btn_primary",
                 kopyala).pack(fill="x", ipady=8, pady=(0,6))
        make_btn(body, "✅  Anladım, Devam Et", "btn_success",
                 self._basarili).pack(fill="x", ipady=10)

    # ── Normal Giriş ─────────────────────────────────────────────────────────
    def _giris_ekrani(self):
        self._clear(); self._center(420, 460)
        t = T()
        ad = get_ayar("ogretmen_ad") or "Öğretmen"
        self._header(f"Hoş geldiniz!", ad)
        body = self._body()

        tk.Label(body, text="🔒  Şifre", font=("Segoe UI",10,"bold"),
                 bg=t["bg"], fg=t["text"]).pack(anchor="w", pady=(8,2))
        self.ent_pw = make_entry(body, show="*")
        self.ent_pw.config(show="*")
        self.ent_pw.pack(fill="x", ipady=8)
        self.ent_pw.focus()
        self.ent_pw.bind("<Return>", lambda e: self._giris())

        self.lbl_err = tk.Label(body, text="", font=("Segoe UI",9),
                                bg=t["bg"], fg=t["btn_danger"])
        self.lbl_err.pack(pady=8)

        make_btn(body, "🔑  Giriş Yap", "btn_primary",
                 self._giris).pack(fill="x", ipady=10)

        tk.Button(body, text="Şifremi Unuttum →",
                  font=("Segoe UI",9), bg=t["bg"], fg=t["btn_primary"],
                  relief="flat", cursor="hand2", bd=0,
                  activebackground=t["bg"], activeforeground=t["highlight"],
                  command=self._sifre_sifirla).pack(pady=(12,0))

        # Alt orta - DB etiketi
        tk.Frame(body, bg=t["bg"]).pack(expand=True, fill="both")
        tk.Label(body, text="DB",
                 font=("Segoe UI", 9, "bold"),
                 bg=t["bg"], fg=t["subtext"]).pack(pady=(0,4))

    def _giris(self):
        if hash_pw(self.ent_pw.get()) == get_ayar("pw_hash"):
            self._basarili()
        else:
            self.lbl_err.config(text="❌  Yanlış şifre!")
            self.ent_pw.delete(0, "end")

    def _basarili(self):
        self.result = True; self.destroy()

    # ── Şifre Sıfırlama ──────────────────────────────────────────────────────
    def _sifre_sifirla(self):
        self._clear(); self._center(420, 380)
        t = T()
        self._header("🔐  Şifre Sıfırlama", "Kurtarma kodunuzu girin")
        body = self._body()

        tk.Label(body, text="Kurtarma Kodu:", font=("Segoe UI",10,"bold"),
                 bg=t["bg"], fg=t["text"]).pack(anchor="w", pady=(8,2))
        self.ent_kod = make_entry(body)
        self.ent_kod.pack(fill="x", ipady=8)
        self.ent_kod.focus()

        self.lbl_err2 = tk.Label(body, text="", font=("Segoe UI",9),
                                  bg=t["bg"], fg=t["btn_danger"])
        self.lbl_err2.pack(pady=6)

        make_btn(body, "✅  Kodu Doğrula", "btn_primary",
                 self._dogrula).pack(fill="x", ipady=9, pady=(0,8))
        tk.Button(body, text="← Geri Dön",
                  font=("Segoe UI",9), bg=t["bg"], fg=t["btn_primary"],
                  relief="flat", cursor="hand2", bd=0,
                  activebackground=t["bg"],
                  command=self._giris_ekrani).pack()

    def _dogrula(self):
        kod = self.ent_kod.get().strip().upper()
        kid = kurtarma_kodu_gecerli(kod)
        if not kid:
            self.lbl_err2.config(text="❌  Geçersiz veya kullanılmış kod!")
            return
        self._yeni_sifre(kid)

    def _yeni_sifre(self, kid):
        self._clear()
        self._center(420, 440)
        t = T()

        # Header
        hdr = tk.Frame(self, bg=t["header"])
        hdr.pack(fill="x")
        try:
            import os, sys
            from PIL import Image as PilImage, ImageTk
            _base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(_base, "logo.png")
            if os.path.exists(logo_path):
                pil_img = PilImage.open(logo_path).resize((48, 48), PilImage.LANCZOS)
                self._logo_ph2 = ImageTk.PhotoImage(pil_img)
                tk.Label(hdr, image=self._logo_ph2, bg=t["header"]).pack(pady=(12,2))
        except Exception:
            tk.Label(hdr, text="🔐", font=("Segoe UI", 24),
                     bg=t["header"], fg=t["accent"]).pack(pady=(14,2))
        tk.Label(hdr, text="Yeni Şifre Belirle",
                 font=("Segoe UI", 15, "bold"),
                 bg=t["header"], fg=t["header_fg"]).pack(pady=(0,4))
        tk.Label(hdr, text="Yeni şifrenizi girin",
                 font=("Segoe UI", 9),
                 bg=t["header"], fg=t["subtext"]).pack(pady=(0,14))

        # Body
        body = tk.Frame(self, bg=t["bg"], padx=36, pady=20)
        body.pack(fill="both", expand=True)

        # Yeni şifre alanı
        tk.Label(body, text="Yeni Şifre:",
                 font=("Segoe UI", 10, "bold"),
                 bg=t["bg"], fg=t["text"]).pack(anchor="w", pady=(4,2))
        ent1 = tk.Entry(body,
                        font=("Segoe UI", 12),
                        show="*",
                        relief="solid", bd=1,
                        bg=t["entry_bg"], fg=t["entry_fg"],
                        insertbackground=t["text"])
        ent1.pack(fill="x", ipady=9)
        ent1.focus()

        # Tekrar alanı
        tk.Label(body, text="Şifre Tekrar:",
                 font=("Segoe UI", 10, "bold"),
                 bg=t["bg"], fg=t["text"]).pack(anchor="w", pady=(12,2))
        ent2 = tk.Entry(body,
                        font=("Segoe UI", 12),
                        show="*",
                        relief="solid", bd=1,
                        bg=t["entry_bg"], fg=t["entry_fg"],
                        insertbackground=t["text"])
        ent2.pack(fill="x", ipady=9)

        # Hata etiketi
        lbl_hata = tk.Label(body, text="",
                            font=("Segoe UI", 9),
                            bg=t["bg"], fg=t["btn_danger"])
        lbl_hata.pack(pady=(8,4))

        # Kaydet fonksiyonu — yerel değişkenler kullanıyor, self değil
        def kaydet(event=None):
            p1 = ent1.get()
            p2 = ent2.get()
            if len(p1) < 4:
                lbl_hata.config(text="❌  Şifre en az 4 karakter olmalı!")
                ent1.focus()
                return
            if p1 != p2:
                lbl_hata.config(text="❌  Şifreler eşleşmiyor!")
                ent2.delete(0, "end")
                ent2.focus()
                return
            # Kaydet
            set_ayar("pw_hash", hash_pw(p1))
            kurtarma_kodu_kullan(kid)
            messagebox.showinfo("✅  Başarılı",
                                "Şifreniz güncellendi!\nYeni şifrenizle giriş yapabilirsiniz.")
            self._giris_ekrani()

        # Enter bağlamaları
        ent1.bind("<Return>", lambda e: ent2.focus())
        ent2.bind("<Return>", kaydet)

        # Kaydet butonu
        btn = tk.Button(body,
                        text="💾  Şifreyi Kaydet",
                        font=("Segoe UI", 11, "bold"),
                        bg=t["btn_success"], fg="white",
                        relief="flat", cursor="hand2",
                        command=kaydet,
                        activebackground=t["btn_success"],
                        activeforeground="white")
        btn.pack(fill="x", ipady=10, pady=(4,0))

        # Geri dön
        tk.Button(body, text="← Geri Dön",
                  font=("Segoe UI", 9),
                  bg=t["bg"], fg=t["btn_primary"],
                  relief="flat", cursor="hand2", bd=0,
                  activebackground=t["bg"],
                  command=self._giris_ekrani).pack(pady=(10,0))
