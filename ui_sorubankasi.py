# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import io
from PIL import Image, ImageTk

import db
from theme import T, make_btn, make_entry
from image_proc import resize_bytes, to_tk

# ── Custom Checkbox (tema uyumlu) ─────────────────────────────────────────────
class CustomCheckbox(tk.Frame):
    """Koyu/açık temada tik işareti her zaman görünen custom checkbox."""
    def __init__(self, parent, text="", variable=None, command=None, **kw):
        t = T()
        super().__init__(parent, bg=kw.pop("bg", t["panel"]))
        self.var = variable or tk.BooleanVar(value=True)
        self.command = command
        self._build(text)

    def _build(self, text):
        t = T()
        self.box = tk.Canvas(self, width=18, height=18,
                              bg=self["bg"], highlightthickness=0, cursor="hand2")
        self.box.pack(side="left", padx=(0,6))
        self.lbl = tk.Label(self, text=text,
                             font=("Segoe UI",10),
                             bg=self["bg"], fg=t["text"], cursor="hand2")
        self.lbl.pack(side="left")
        self._draw()
        self.box.bind("<Button-1>", self._toggle)
        self.lbl.bind("<Button-1>", self._toggle)
        self.var.trace_add("write", lambda *a: self._draw())

    def _draw(self):
        t = T()
        self.box.delete("all")
        checked = self.var.get()
        # Kutu
        fill = t["btn_primary"] if checked else t["entry_bg"]
        self.box.create_rectangle(2, 2, 16, 16,
            fill=fill, outline=t["border"] if not checked else t["btn_primary"],
            width=1.5)
        # Tik işareti — her zaman beyaz, dolayısıyla her temada görünür
        if checked:
            self.box.create_line(4, 9, 7, 13, fill="white", width=2.5)
            self.box.create_line(7, 13, 14, 5, fill="white", width=2.5)

    def _toggle(self, e=None):
        self.var.set(not self.var.get())
        if self.command: self.command()

    def get(self):
        return self.var.get()


# ── Ekran Görüntüsü / Dosya Seçme Penceresi ──────────────────────────────────
class ImageSelectWindow(tk.Toplevel):
    """
    Ekran görüntüsü veya dosyadan soru seçme.
    Manuel kırpma (dikdörtgen çizme) desteklenir.
    """
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Görsel Seç ve Kırp")
        self.callback    = callback
        self.img_bytes   = None
        self.pil_orig    = None
        self.tk_photo    = None
        self.drag_start  = None
        self.manual_rect = None
        self.scale_x = self.scale_y = 1.0
        t = T(); self.configure(bg=t["bg"]); self.geometry("980x700")
        self._build()

    def _build(self):
        t = T()
        # Toolbar
        tb = tk.Frame(self, bg=t["header"]); tb.pack(fill="x")
        tk.Label(tb, text="✂️  Görsel Seç ve Kırp",
                 font=("Segoe UI",13,"bold"),
                 bg=t["header"], fg=t["header_fg"]).pack(side="left", padx=16, pady=10)
        make_btn(tb,"📁  Dosyadan Aç","btn_primary",self._ac_dosya).pack(
            side="right", padx=6, pady=8, ipady=5, ipadx=10)
        make_btn(tb,"📋  Panodan Yapıştır","btn_warning",self._panodan).pack(
            side="right", padx=2, pady=8, ipady=5, ipadx=10)

        # Bilgi çubuğu
        info = tk.Frame(self, bg=t["panel2"]); info.pack(fill="x")
        tk.Label(info,
                 text="💡  Görsel açtıktan sonra kırpmak istediğiniz alanı sol tıklayıp sürükleyerek seçin. "
                      "Tüm görseli kullanmak için direkt 'Kullan' butonuna basın.",
                 font=("Segoe UI",8), bg=t["panel2"], fg=t["subtext"],
                 wraplength=900, justify="left").pack(anchor="w", padx=14, pady=6)

        # Canvas
        cf = tk.Frame(self, bg=t["canvas_bg"],
                      highlightthickness=1, highlightbackground=t["border"])
        cf.pack(fill="both", expand=True, padx=10, pady=(0,0))
        self.canvas = tk.Canvas(cf, bg="#C8CDD6", cursor="crosshair", highlightthickness=0)
        hsb = ttk.Scrollbar(cf, orient="horizontal", command=self.canvas.xview)
        vsb = ttk.Scrollbar(cf, orient="vertical",   command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y"); hsb.pack(side="bottom", fill="x")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>",   self._press)
        self.canvas.bind("<B1-Motion>",       self._drag_sel)
        self.canvas.bind("<ButtonRelease-1>", self._release)

        # Alt butonlar
        bot = tk.Frame(self, bg=t["bg"]); bot.pack(fill="x", padx=10, pady=8)
        make_btn(bot,"✅  Seçimi Kullan","btn_success",self._kullan).pack(
            side="right", ipady=7, ipadx=14)
        make_btn(bot,"🔄  Seçimi Temizle","btn_secondary",self._temizle_sec).pack(
            side="right", padx=6, ipady=7, ipadx=10)
        self.durum_lbl = tk.Label(bot, text="Henüz görsel açılmadı.",
                                   font=("Segoe UI",9), bg=t["bg"], fg=t["subtext"])
        self.durum_lbl.pack(side="left", padx=8)

    # ── Görsel Açma ──────────────────────────────────────────────────────────
    def _ac_dosya(self):
        path = filedialog.askopenfilename(
            title="Görsel Seç",
            filetypes=[
                ("Görsel","*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("Tümü","*.*")
            ])
        if not path: return
        with open(path,"rb") as f: data = f.read()
        self._yukle(data)

    def _panodan(self):
        """Panodan görsel yapıştır (ekran görüntüsü için)."""
        try:
            # Windows / PIL pano desteği
            from PIL import ImageGrab
            img = ImageGrab.grabclipboard()
            if img is None:
                messagebox.showinfo("Bilgi",
                    "Panoda görsel bulunamadı.\n"
                    "Ekran görüntüsü alıp (PrintScreen veya Snipping Tool) "
                    "ardından Panodan Yapıştır'a basın.")
                return
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            self._yukle(buf.getvalue())
        except Exception as ex:
            messagebox.showerror("Hata", f"Pano okunamadı:\n{ex}")

    def _yukle(self, data: bytes):
        self.img_bytes = data
        self.pil_orig  = Image.open(io.BytesIO(data)).convert("RGB")
        self._goster()
        self.durum_lbl.config(
            text=f"✅  Görsel yüklendi: {self.pil_orig.width}×{self.pil_orig.height} px  "
                 f"— İstediğiniz alanı seçin veya direkt 'Kullan'a basın.")

    def _goster(self):
        if not self.pil_orig: return
        disp = self.pil_orig.copy()
        disp.thumbnail((920, 580), Image.LANCZOS)
        self.scale_x = self.pil_orig.width  / disp.width
        self.scale_y = self.pil_orig.height / disp.height
        self.tk_photo = ImageTk.PhotoImage(disp)
        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0,0,disp.width,disp.height))
        self.canvas.create_image(0,0,anchor="nw",image=self.tk_photo,tag="img")
        self.manual_rect = None

    # ── Manuel Seçim ─────────────────────────────────────────────────────────
    def _press(self, e):
        self.drag_start = (self.canvas.canvasx(e.x), self.canvas.canvasy(e.y))
        self.canvas.delete("sel")

    def _drag_sel(self, e):
        if not self.drag_start: return
        cx, cy = self.canvas.canvasx(e.x), self.canvas.canvasy(e.y)
        self.canvas.delete("sel")
        self.canvas.create_rectangle(
            self.drag_start[0], self.drag_start[1], cx, cy,
            outline="#3B82F6", width=2, dash=(4,2), tag="sel")
        # Boyut göster
        w_px = int(abs(cx - self.drag_start[0]) * self.scale_x)
        h_px = int(abs(cy - self.drag_start[1]) * self.scale_y)
        self.canvas.create_text(
            cx+4, cy+4, anchor="nw",
            text=f"{w_px}×{h_px}",
            font=("Segoe UI",8,"bold"), fill="#3B82F6", tag="sel")

    def _release(self, e):
        if not self.drag_start: return
        cx, cy = self.canvas.canvasx(e.x), self.canvas.canvasy(e.y)
        x0, y0 = self.drag_start
        if abs(cx-x0) < 8 or abs(cy-y0) < 8:
            # Çok küçük seçim — yoksay
            self.drag_start = None; return
        rx = int(min(x0,cx) * self.scale_x)
        ry = int(min(y0,cy) * self.scale_y)
        rw = int(abs(cx-x0) * self.scale_x)
        rh = int(abs(cy-y0) * self.scale_y)
        self.manual_rect = (rx, ry, rw, rh)
        self.drag_start  = None
        self.durum_lbl.config(
            text=f"✅  Seçim: {rw}×{rh} px — 'Seçimi Kullan' butonuna basın.")

    def _temizle_sec(self):
        self.manual_rect = None
        self.drag_start  = None
        self.canvas.delete("sel")
        if self.pil_orig:
            self.durum_lbl.config(text="Seçim temizlendi. Tekrar seçebilirsiniz.")

    # ── Kullan ───────────────────────────────────────────────────────────────
    def _kullan(self):
        if not self.pil_orig:
            messagebox.showwarning("Uyarı","Önce bir görsel açın!"); return
        if self.manual_rect:
            x, y, w, h = self.manual_rect
            cropped = self.pil_orig.crop((x, y, x+w, y+h))
        else:
            cropped = self.pil_orig
        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        self.callback(buf.getvalue())
        self.destroy()


# ── Soru Bankası Sekmesi ──────────────────────────────────────────────────────
class DatabaseTab(tk.Frame):
    def __init__(self, parent, app):
        t = T(); super().__init__(parent, bg=t["bg"])
        self.app = app
        self.sel_img   = None
        self.sel_cevap = None
        self.sel_cozum = None
        self.selected_soru_id = None
        self.soru_cards = []
        self._build()
        self.load_siniflar()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build(self):
        t = T()
        pane = tk.PanedWindow(self, orient="horizontal",
                               bg=t["bg"], sashwidth=4,
                               sashrelief="flat", sashpad=2)
        pane.pack(fill="both", expand=True, padx=8, pady=8)

        left = tk.Frame(pane, bg=t["panel"],
                        highlightthickness=1, highlightbackground=t["border"])
        pane.add(left, minsize=200)
        self._build_left(left)

        mid = tk.Frame(pane, bg=t["panel"],
                       highlightthickness=1, highlightbackground=t["border"])
        pane.add(mid, minsize=280)
        self._build_mid(mid)

        right = tk.Frame(pane, bg=t["panel"],
                         highlightthickness=1, highlightbackground=t["border"])
        pane.add(right, minsize=300)
        self._build_right(right)

    def _build_left(self, parent):
        t = T()
        # Sınıflar
        tk.Label(parent, text="🏫  Sınıflar",
                 font=("Segoe UI",11,"bold"),
                 bg=t["panel"], fg=t["text"]).pack(pady=(14,6), padx=14, anchor="w")
        af = tk.Frame(parent, bg=t["panel"]); af.pack(fill="x", padx=10, pady=(0,6))
        self.sinif_ent = make_entry(af)
        self.sinif_ent.pack(side="left", fill="x", expand=True, ipady=5, padx=(0,4))
        self.sinif_ent.bind("<Return>", lambda e: self._sinif_ekle())
        make_btn(af,"+ Ekle","btn_success",self._sinif_ekle,small=True).pack(side="left",ipady=5,ipadx=6)
        lf = tk.Frame(parent, bg=t["panel"]); lf.pack(fill="x", padx=10)
        sb = ttk.Scrollbar(lf)
        self.sinif_lb = tk.Listbox(lf, font=("Segoe UI",10),
                                    selectbackground=t["listbox_sel"],
                                    selectforeground="white",
                                    relief="flat", bg=t["listbox_bg"], fg=t["listbox_fg"],
                                    activestyle="none", yscrollcommand=sb.set, height=6)
        sb.config(command=self.sinif_lb.yview)
        sb.pack(side="right",fill="y"); self.sinif_lb.pack(side="left",fill="x",expand=True)
        self.sinif_lb.bind("<<ListboxSelect>>", self._on_sinif_sec)
        make_btn(parent,"🗑️  Sınıfı Sil","btn_danger",self._sinif_sil,small=True).pack(
            pady=(4,12), padx=10, fill="x", ipady=4)

        tk.Frame(parent, bg=t["separator"], height=1).pack(fill="x", padx=10)

        # Konular
        tk.Label(parent, text="📁  Konular",
                 font=("Segoe UI",11,"bold"),
                 bg=t["panel"], fg=t["text"]).pack(pady=(12,6), padx=14, anchor="w")
        af2 = tk.Frame(parent, bg=t["panel"]); af2.pack(fill="x", padx=10, pady=(0,6))
        self.konu_ent = make_entry(af2)
        self.konu_ent.pack(side="left", fill="x", expand=True, ipady=5, padx=(0,4))
        self.konu_ent.bind("<Return>", lambda e: self._konu_ekle())
        make_btn(af2,"+ Ekle","btn_success",self._konu_ekle,small=True).pack(side="left",ipady=5,ipadx=6)
        lf2 = tk.Frame(parent, bg=t["panel"]); lf2.pack(fill="both", expand=True, padx=10)
        sb2 = ttk.Scrollbar(lf2)
        self.konu_lb = tk.Listbox(lf2, font=("Segoe UI",10),
                                   selectbackground=t["listbox_sel"],
                                   selectforeground="white",
                                   relief="flat", bg=t["listbox_bg"], fg=t["listbox_fg"],
                                   activestyle="none", yscrollcommand=sb2.set)
        sb2.config(command=self.konu_lb.yview)
        sb2.pack(side="right",fill="y"); self.konu_lb.pack(side="left",fill="both",expand=True)
        self.konu_lb.bind("<<ListboxSelect>>", self._on_konu_sec)
        make_btn(parent,"🗑️  Konuyu Sil","btn_danger",self._konu_sil,small=True).pack(
            pady=(4,12), padx=10, fill="x", ipady=4)

    def _build_mid(self, parent):
        t = T()
        tk.Label(parent, text="➕  Soru Ekle / Güncelle",
                 font=("Segoe UI",12,"bold"),
                 bg=t["panel"], fg=t["text"]).pack(pady=(14,4), padx=14, anchor="w")

        # Scrollable form
        cf = tk.Frame(parent, bg=t["panel"]); cf.pack(fill="both", expand=True)
        vsb = ttk.Scrollbar(cf)
        canvas = tk.Canvas(cf, bg=t["panel"], highlightthickness=0, yscrollcommand=vsb.set)
        vsb.config(command=canvas.yview)
        vsb.pack(side="right",fill="y"); canvas.pack(side="left",fill="both",expand=True)
        form = tk.Frame(canvas, bg=t["panel"])
        win = canvas.create_window((0,0), window=form, anchor="nw")
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        def section(text):
            tk.Frame(form, bg=t["separator"], height=1).pack(fill="x", padx=12, pady=8)
            tk.Label(form, text=text, font=("Segoe UI",9,"bold"),
                     bg=t["panel"], fg=t["subtext"]).pack(anchor="w", padx=12)

        # Soru görseli
        section("📷  SORU GÖRSELİ")
        self.prev_s = tk.Label(form, bg=t["canvas_bg"], text="Görsel seçilmedi",
                                width=30, height=7, relief="flat",
                                font=("Segoe UI",8), fg=t["subtext"],
                                highlightthickness=1, highlightbackground=t["border"])
        self.prev_s.pack(padx=12, pady=(4,6))
        br = tk.Frame(form, bg=t["panel"]); br.pack(fill="x", padx=12, pady=(0,4))
        make_btn(br,"📁 Dosyadan","btn_primary",self._gorsel_sec,small=True).pack(
            side="left",fill="x",expand=True,ipady=5,padx=(0,3))
        make_btn(br,"📋 Pano/Kırp","btn_warning",self._gorsel_kirp,small=True).pack(
            side="left",fill="x",expand=True,ipady=5)

        # Cevap metni
        section("✏️  CEVAP (METİN)")
        self.cevap_ent = make_entry(form, width=28)
        self.cevap_ent.pack(padx=12, pady=(4,4), fill="x", ipady=6)

        # Cevap görseli
        section("🖼️  CEVAP GÖRSELİ (opsiyonel)")
        self.prev_c = tk.Label(form, bg=t["canvas_bg"], text="Seçilmedi",
                                width=30, height=4, relief="flat",
                                font=("Segoe UI",8), fg=t["subtext"],
                                highlightthickness=1, highlightbackground=t["border"])
        self.prev_c.pack(padx=12, pady=(4,4))
        make_btn(form,"📁  Cevap Görseli Seç","btn_purple",
                 lambda: self._gen_sec(self.prev_c,"sel_cevap"),small=True).pack(
                     padx=12,fill="x",ipady=4)

        # Çözüm görseli
        section("📋  ÇÖZÜM GÖRSELİ (opsiyonel)")
        self.prev_z = tk.Label(form, bg=t["canvas_bg"], text="Seçilmedi",
                                width=30, height=4, relief="flat",
                                font=("Segoe UI",8), fg=t["subtext"],
                                highlightthickness=1, highlightbackground=t["border"])
        self.prev_z.pack(padx=12, pady=(4,4))
        make_btn(form,"📁  Çözüm Görseli Seç","btn_orange",
                 lambda: self._gen_sec(self.prev_z,"sel_cozum"),small=True).pack(
                     padx=12,fill="x",ipady=4)

        tk.Frame(form, bg=t["separator"], height=1).pack(fill="x", padx=12, pady=10)
        make_btn(form,"💾  Soruyu Kaydet","btn_success",self.soru_kaydet).pack(
            padx=12,fill="x",ipady=8,pady=(0,6))
        make_btn(form,"✏️  Seçileni Güncelle","btn_warning",self.soru_guncelle).pack(
            padx=12,fill="x",ipady=8,pady=(0,14))

    def _build_right(self, parent):
        t = T()
        hdr = tk.Frame(parent, bg=t["panel"]); hdr.pack(fill="x", padx=12, pady=(12,6))
        tk.Label(hdr, text="📋  Sorular",
                 font=("Segoe UI",12,"bold"),
                 bg=t["panel"], fg=t["text"]).pack(side="left")
        self.ss_lbl = tk.Label(hdr, text="", font=("Segoe UI",9),
                                bg=t["panel"], fg=t["subtext"])
        self.ss_lbl.pack(side="left", padx=8)
        make_btn(hdr,"🗑️  Sil","btn_danger",self.soru_sil,small=True).pack(
            side="right",ipady=4,ipadx=6)

        cf = tk.Frame(parent, bg=t["canvas_bg"])
        cf.pack(fill="both", expand=True, padx=8, pady=(0,10))
        self.cards_canvas = tk.Canvas(cf, bg=t["canvas_bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(cf, orient="vertical", command=self.cards_canvas.yview)
        self.cards_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y"); self.cards_canvas.pack(side="left",fill="both",expand=True)
        self.cards_frame = tk.Frame(self.cards_canvas, bg=t["canvas_bg"])
        self.cards_win = self.cards_canvas.create_window((0,0), window=self.cards_frame, anchor="nw")
        self.cards_frame.bind("<Configure>",
            lambda e: self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all")))
        self.cards_canvas.bind("<Configure>",
            lambda e: self.cards_canvas.itemconfig(self.cards_win, width=e.width))
        self.cards_canvas.bind_all("<MouseWheel>",
            lambda e: self.cards_canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

    # ── Sınıf İşlemleri ───────────────────────────────────────────────────────
    def load_siniflar(self):
        self.sinif_lb.delete(0,"end"); self._sinif_ids=[]
        for sid, ad in db.get_siniflar():
            self.sinif_lb.insert("end", f"  {ad}"); self._sinif_ids.append(sid)
        self._load_konular_all()

    def _sinif_ekle(self):
        ad = self.sinif_ent.get().strip()
        if not ad: messagebox.showwarning("Uyarı","Sınıf adı boş olamaz!"); return
        try: db.sinif_ekle(ad); self.sinif_ent.delete(0,"end"); self.load_siniflar()
        except Exception as ex: messagebox.showerror("Hata",str(ex))

    def _sinif_sil(self):
        sel = self.sinif_lb.curselection()
        if not sel: messagebox.showwarning("Uyarı","Bir sınıf seçin!"); return
        if messagebox.askyesno("Onay","Bu sınıfı sil?"):
            db.sinif_sil(self._sinif_ids[sel[0]]); self.load_siniflar()

    def _on_sinif_sec(self, e=None):
        sel = self.sinif_lb.curselection()
        if sel: self._load_konular(self._sinif_ids[sel[0]])
        else:   self._load_konular_all()

    def _load_konular(self, sinif_id=None):
        self.konu_lb.delete(0,"end"); self._konu_ids=[]
        for kid, ad, _ in db.get_konular(sinif_id):
            self.konu_lb.insert("end", f"  {ad}"); self._konu_ids.append(kid)

    def _load_konular_all(self):
        self.konu_lb.delete(0,"end"); self._konu_ids=[]
        for kid, ad, _ in db.get_konular():
            self.konu_lb.insert("end", f"  {ad}"); self._konu_ids.append(kid)

    def _konu_ekle(self):
        ad = self.konu_ent.get().strip()
        if not ad: messagebox.showwarning("Uyarı","Konu adı boş olamaz!"); return
        sel = self.sinif_lb.curselection()
        sinif_id = self._sinif_ids[sel[0]] if sel else None
        try:
            db.konu_ekle(ad, sinif_id)
            self.konu_ent.delete(0,"end"); self._on_sinif_sec()
        except Exception as ex: messagebox.showerror("Hata",str(ex))

    def _konu_sil(self):
        sel = self.konu_lb.curselection()
        if not sel: messagebox.showwarning("Uyarı","Bir konu seçin!"); return
        if messagebox.askyesno("Onay","Bu konuyu ve tüm sorularını sil?"):
            db.konu_sil(self._konu_ids[sel[0]]); self._on_sinif_sec()

    def _on_konu_sec(self, e=None):
        sel = self.konu_lb.curselection()
        if sel: self.load_sorular(self._konu_ids[sel[0]])

    # ── Görsel Seçme ─────────────────────────────────────────────────────────
    def _gen_sec(self, label, attr):
        path = filedialog.askopenfilename(title="Görsel",
            filetypes=[("Görsel","*.png *.jpg *.jpeg *.bmp *.gif *.webp"),("Tümü","*.*")])
        if not path: return
        with open(path,"rb") as f: data = f.read()
        data = resize_bytes(data); setattr(self, attr, data)
        ph = to_tk(data,200,110); setattr(self,f"_ph_{attr}",ph)
        label.configure(image=ph, text="")

    def _gorsel_sec(self):
        path = filedialog.askopenfilename(title="Soru Görseli",
            filetypes=[("Görsel","*.png *.jpg *.jpeg *.bmp *.gif *.webp"),("Tümü","*.*")])
        if not path: return
        with open(path,"rb") as f: data = f.read()
        self.sel_img = resize_bytes(data)
        self._ph_s = to_tk(self.sel_img,220,130)
        self.prev_s.configure(image=self._ph_s, text="")

    def _gorsel_kirp(self):
        """Ekran görüntüsü / pano / dosyadan kırparak soru ekle."""
        def cb(b):
            self.sel_img = resize_bytes(b)
            self._ph_s = to_tk(self.sel_img,220,130)
            self.prev_s.configure(image=self._ph_s, text="")
        ImageSelectWindow(self, cb)

    # ── Soru CRUD ─────────────────────────────────────────────────────────────
    def soru_kaydet(self):
        sel = self.konu_lb.curselection()
        if not sel: messagebox.showwarning("Uyarı","Önce konu seçin!"); return
        if not self.sel_img: messagebox.showwarning("Uyarı","Soru görseli seçin!"); return
        kid = self._konu_ids[sel[0]]
        cm  = self.cevap_ent.get().strip() or None
        db.soru_ekle(kid, self.sel_img, self.sel_img, cm, self.sel_cevap, self.sel_cozum)
        self._temizle(); self.load_sorular(kid)
        messagebox.showinfo("✅","Soru kaydedildi!")

    def soru_guncelle(self):
        if not self.selected_soru_id:
            messagebox.showwarning("Uyarı","Güncellemek için bir soru kartına tıklayın!"); return
        kid = self._get_current_konu_id()
        rows = db.get_sorular(kid) if kid else []
        row = next((r for r in rows if r[0]==self.selected_soru_id), None)
        if not row: return
        g  = self.sel_img   or row[1]
        gt = self.sel_img   or row[2] or row[1]
        cg = self.sel_cevap or row[4]
        zg = self.sel_cozum or row[5]
        cm = self.cevap_ent.get().strip() or None
        db.soru_guncelle(self.selected_soru_id, g, gt, cm, cg, zg)
        self._temizle(); self.load_sorular(kid)
        messagebox.showinfo("✅",f"Soru #{self.selected_soru_id} güncellendi!")

    def _get_current_konu_id(self):
        sel = self.konu_lb.curselection()
        return self._konu_ids[sel[0]] if sel else None

    def _temizle(self):
        self.sel_img = self.sel_cevap = self.sel_cozum = None
        for lbl, txt in [
            (self.prev_s,"Görsel seçilmedi"),
            (self.prev_c,"Seçilmedi"),
            (self.prev_z,"Seçilmedi")
        ]:
            lbl.configure(image="", text=txt)
        self.cevap_ent.delete(0,"end")

    def load_sorular(self, konu_id):
        for w in self.soru_cards: w.destroy()
        self.soru_cards.clear(); self.selected_soru_id = None
        if konu_id is None: self.ss_lbl.config(text=""); return
        rows = db.get_sorular(konu_id)
        self.ss_lbl.config(text=f"({len(rows)} soru)")
        t = T(); COLS = 3; self._phs = []

        for i, (sid, blob, blob_t, cm, cg, zg) in enumerate(rows):
            r, c = divmod(i, COLS)
            card = tk.Frame(self.cards_frame, bg=t["card_bg"],
                            relief="flat", bd=0,
                            highlightthickness=2,
                            highlightbackground=t["border"])
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            self.cards_frame.columnconfigure(c, weight=1)

            display_blob = blob_t if blob_t else blob
            ph = to_tk(display_blob,190,130); self._phs.append(ph)
            il = tk.Label(card, image=ph, bg=t["card_bg"], cursor="hand2")
            il.pack(padx=8, pady=8)

            badge_f = tk.Frame(card, bg=t["card_bg"]); badge_f.pack(fill="x", padx=8, pady=(0,4))
            tk.Label(badge_f, text=f"Soru #{sid}",
                     font=("Segoe UI",8,"bold"),
                     bg=t["card_bg"], fg=t["subtext"]).pack(side="left")
            for icon, is_green in [("✏️",True),("🖼️",False),("📋",False)]:
                has = (cm and icon=="✏️") or (cg and icon=="🖼️") or (zg and icon=="📋")
                if has:
                    tk.Label(badge_f, text=icon, font=("Segoe UI",9),
                             bg=t["tag_green"] if is_green else t["tag_blue"],
                             fg=t["tag_green_fg"] if is_green else t["tag_blue_fg"],
                             padx=4, pady=1).pack(side="right", padx=2)

            if cm:
                tk.Label(card, text=cm, font=("Segoe UI",8,"bold"),
                         bg=t["card_bg"], fg=t["btn_success"]).pack(pady=(0,4))
            elif not cg:
                tk.Label(card, text="⚠️ Cevap eklenmemiş",
                         font=("Segoe UI",7),
                         bg=t["tag_red"], fg=t["tag_red_fg"],
                         padx=4).pack(pady=(0,4))

            def make_sel(widget, s_id, s_cm, s_cg, s_zg, s_blob, s_blt):
                def fn(e=None):
                    self.selected_soru_id = s_id
                    for w2 in self.soru_cards:
                        w2.config(highlightbackground=T()["border"])
                    widget.config(highlightbackground=T()["highlight"])
                    self.cevap_ent.delete(0,"end")
                    if s_cm: self.cevap_ent.insert(0, s_cm)
                    disp = s_blt if s_blt else s_blob
                    ph2=to_tk(disp,220,130); self._cur_s=ph2
                    self.prev_s.configure(image=ph2, text="")
                    if s_cg:
                        ph3=to_tk(s_cg,200,110); self._cur_c=ph3
                        self.prev_c.configure(image=ph3, text="")
                    else: self.prev_c.configure(image="", text="Seçilmedi")
                    if s_zg:
                        ph4=to_tk(s_zg,200,110); self._cur_z=ph4
                        self.prev_z.configure(image=ph4, text="")
                    else: self.prev_z.configure(image="", text="Seçilmedi")
                return fn

            cb = make_sel(card, sid, cm, cg, zg, blob, blob_t)
            card.bind("<Button-1>",cb); il.bind("<Button-1>",cb)
            self.soru_cards.append(card)

    def soru_sil(self):
        if not self.selected_soru_id:
            messagebox.showwarning("Uyarı","Silmek için bir soru kartına tıklayın!"); return
        if messagebox.askyesno("Onay",f"Soru #{self.selected_soru_id} silinsin mi?"):
            db.soru_sil(self.selected_soru_id)
            kid = self._get_current_konu_id()
            if kid: self.load_sorular(kid)
