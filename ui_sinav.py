# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random, datetime

import db
from theme import T, make_btn, make_entry
from pdf_editor import PDFLayoutEditor
from pdf_utils import gen_cevap_pdf
from pdf_fonts import register_fonts, F
from ui_sorubankasi import CustomCheckbox

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Image as RLImage, Table, TableStyle)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from PIL import Image
    import io
    RL_OK = True
except ImportError:
    RL_OK = False

class SinavTab(tk.Frame):
    def __init__(self, parent, app):
        t = T(); super().__init__(parent, bg=t["bg"])
        self.app = app
        self._sinif_vars = {}
        self._konu_vars  = {}
        self._build()

    def _build(self):
        t = T()
        # Sol: Filtreler
        left = tk.Frame(self, bg=t["panel"],
                        highlightthickness=1, highlightbackground=t["border"])
        left.pack(side="left", fill="both", expand=True, padx=(10,5), pady=10)
        self._build_filters(left)

        # Sağ: Ayarlar
        right = tk.Frame(self, bg=t["panel"], width=310,
                         highlightthickness=1, highlightbackground=t["border"])
        right.pack(side="left", fill="y", padx=(5,10), pady=10)
        right.pack_propagate(False)
        self._build_settings(right)

    def _build_filters(self, parent):
        t = T()
        tk.Label(parent, text="📂  Sınıf & Konu Seçimi",
                 font=("Segoe UI",13,"bold"),
                 bg=t["panel"], fg=t["text"]).pack(pady=(14,4), padx=14, anchor="w")
        tk.Label(parent,
                 text="Seçtiğiniz sınıf ve konulardan soru çekilecek. Hiç seçmezseniz tüm soru havuzu kullanılır.",
                 font=("Segoe UI",8), bg=t["panel"], fg=t["subtext"],
                 wraplength=500).pack(padx=14, anchor="w", pady=(0,10))

        # Sınıf checkboxları
        tk.Label(parent, text="🏫  Sınıflar:",
                 font=("Segoe UI",10,"bold"),
                 bg=t["panel"], fg=t["text"]).pack(anchor="w", padx=14, pady=(4,2))

        sinif_scroll_f = tk.Frame(parent, bg=t["panel"])
        sinif_scroll_f.pack(fill="x", padx=14, pady=(0,10))
        self.sinif_check_frame = tk.Frame(sinif_scroll_f, bg=t["panel"])
        self.sinif_check_frame.pack(fill="x")

        tk.Frame(parent, bg=t["separator"], height=1).pack(fill="x", padx=14)

        # Konu checkboxları
        tk.Label(parent, text="📁  Konular:",
                 font=("Segoe UI",10,"bold"),
                 bg=t["panel"], fg=t["text"]).pack(anchor="w", padx=14, pady=(10,2))

        konu_f = tk.Frame(parent, bg=t["panel"])
        konu_f.pack(fill="both", expand=True, padx=14, pady=(0,10))
        vsb = ttk.Scrollbar(konu_f)
        konu_cv = tk.Canvas(konu_f, bg=t["panel"], highlightthickness=0,
                             yscrollcommand=vsb.set)
        vsb.config(command=konu_cv.yview)
        vsb.pack(side="right",fill="y"); konu_cv.pack(side="left",fill="both",expand=True)
        self.konu_check_frame = tk.Frame(konu_cv, bg=t["panel"])
        konu_win = konu_cv.create_window((0,0), window=self.konu_check_frame, anchor="nw")
        self.konu_check_frame.bind("<Configure>",
            lambda e: konu_cv.configure(scrollregion=konu_cv.bbox("all")))
        konu_cv.bind("<Configure>",
            lambda e: konu_cv.itemconfig(konu_win, width=e.width))
        konu_cv.bind("<MouseWheel>",
            lambda e: konu_cv.yview_scroll(int(-1*(e.delta/120)),"units"))
        self.konu_canvas = konu_cv

    def _build_settings(self, parent):
        t = T()
        tk.Label(parent, text="⚙️  Sınav Ayarları",
                 font=("Segoe UI",13,"bold"),
                 bg=t["panel"], fg=t["text"]).pack(pady=(14,12), padx=14, anchor="w")

        # Scrollable settings
        cf = tk.Frame(parent, bg=t["panel"]); cf.pack(fill="both", expand=True)
        vsb = ttk.Scrollbar(cf)
        sc = tk.Canvas(cf, bg=t["panel"], highlightthickness=0, yscrollcommand=vsb.set)
        vsb.config(command=sc.yview); vsb.pack(side="right",fill="y")
        sc.pack(side="left",fill="both",expand=True)
        body = tk.Frame(sc, bg=t["panel"])
        win = sc.create_window((0,0), window=body, anchor="nw")
        body.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
        sc.bind("<Configure>", lambda e: sc.itemconfig(win, width=e.width))

        def lbl(txt):
            tk.Label(body, text=txt, font=("Segoe UI",9,"bold"),
                     bg=t["panel"], fg=t["text"]).pack(anchor="w", padx=14, pady=(8,2))

        def ent(var):
            e = make_entry(body, textvariable=var)
            e.pack(padx=14, pady=(0,4), fill="x", ipady=6)
            return e

        lbl("📝  Sınav Başlığı:")
        self.baslik  = tk.StringVar(value="SINAV"); ent(self.baslik)

        lbl("🏫  Sınıf / Ders:")
        self.sinif_n = tk.StringVar(value=""); ent(self.sinif_n)

        lbl("📅  Tarih:")
        self.tarih   = tk.StringVar(value=datetime.date.today().strftime("%d.%m.%Y")); ent(self.tarih)

        tk.Frame(body, bg=t["separator"], height=1).pack(fill="x", padx=14, pady=8)

        lbl("🔢  Toplam Soru Sayısı:")
        self.soru_n = tk.IntVar(value=10)
        spin_f = tk.Frame(body, bg=t["panel"]); spin_f.pack(fill="x", padx=14, pady=(0,8))
        tk.Spinbox(spin_f, from_=1, to=200, textvariable=self.soru_n,
                   font=("Segoe UI",12), width=8, relief="solid", bd=1,
                   bg=t["entry_bg"], fg=t["entry_fg"],
                   buttonbackground=t["panel"]).pack(side="left")

        # Seçenekler
        self.karistir   = tk.BooleanVar(value=True)
        self.rastgele   = tk.BooleanVar(value=True)
        self.cevap_pdf  = tk.BooleanVar(value=True)
        self.cozum_pdf  = tk.BooleanVar(value=True)

        for var, text in [
            (self.karistir,  "🔀  Soruları karıştır"),
            (self.rastgele,  "🎲  Rastgele soru seç"),
            (self.cevap_pdf, "📋  Ayrı cevap anahtarı PDF oluştur"),
            (self.cozum_pdf, "📐  Çözüm görsellerini ekle"),
        ]:
            cb = CustomCheckbox(body, text=text, variable=var,
                                bg=t["panel"])
            cb.pack(anchor="w", padx=14, pady=4)

        tk.Frame(body, bg=t["separator"], height=1).pack(fill="x", padx=14, pady=10)

        make_btn(body,"📐  PDF Düzenleyici (Sürükle-Bırak)","btn_dark",
                 self.pdf_layout).pack(padx=14,fill="x",ipady=10,pady=(0,6))
        make_btn(body,"⚡  Hızlı PDF (Otomatik Yerleşim)","btn_primary",
                 self.pdf_hizli).pack(padx=14,fill="x",ipady=8,pady=(0,10))

        self.durum = tk.Label(body, text="", font=("Segoe UI",9),
                              bg=t["panel"], fg=t["btn_success"], wraplength=260)
        self.durum.pack(padx=14, pady=(0,10))

    # ── Konu/Sınıf Refresh ────────────────────────────────────────────────────
    def refresh_konular(self):
        t = T()
        # Sınıfları yenile
        for w in self.sinif_check_frame.winfo_children(): w.destroy()
        self._sinif_vars.clear()
        for sid, ad in db.get_siniflar():
            var = tk.BooleanVar(value=False)
            self._sinif_vars[sid] = var
            cb = CustomCheckbox(
                self.sinif_check_frame,
                text=ad, variable=var,
                bg=t["panel"],
                command=self._on_sinif_filter)
            cb.pack(anchor="w", pady=2)

        # Tüm konuları göster
        self._refresh_konu_checks()

    def _on_sinif_filter(self):
        self._refresh_konu_checks()

    def _refresh_konu_checks(self):
        t = T()
        for w in self.konu_check_frame.winfo_children(): w.destroy()
        self._konu_vars.clear()

        secili_siniflar = [sid for sid, var in self._sinif_vars.items() if var.get()]

        if secili_siniflar:
            rows = []
            for sid in secili_siniflar:
                rows.extend(db.get_konular(sid))
        else:
            rows = db.get_konular()

        if not rows:
            tk.Label(self.konu_check_frame, text="Henüz konu eklenmemiş.",
                     font=("Segoe UI",9), bg=t["panel"], fg=t["subtext"]).pack(pady=8)
            return

        with db.get_conn() as c_:
            sinif_map = {sid: ad for sid, ad in c_.execute("SELECT id, ad FROM siniflar").fetchall()}

        for kid, ad, sinif_id in rows:
            var = tk.BooleanVar(value=True)
            self._konu_vars[kid] = var
            fr = tk.Frame(self.konu_check_frame, bg=t["panel"])
            fr.pack(fill="x", pady=2)
            CustomCheckbox(fr, text=ad, variable=var,
                           bg=t["panel"]).pack(side="left")
            if sinif_id and sinif_id in sinif_map:
                tk.Label(fr,
                         text=f" [{sinif_map[sinif_id]}]",
                         font=("Segoe UI",8), bg=t["panel"],
                         fg=t["subtext"]).pack(side="left")
            # Soru sayısı
            with db.get_conn() as c_:
                cnt = c_.execute(
                    "SELECT COUNT(*) FROM sorular WHERE konu_id=?", (kid,)
                ).fetchone()[0]
            tk.Label(fr, text=f"({cnt})", font=("Segoe UI",8),
                     bg=t["panel"], fg=t["subtext"]).pack(side="right", padx=4)

    # ── Soru Toplama ─────────────────────────────────────────────────────────
    def _get_sorular(self):
        secili_konular = [k for k,v in self._konu_vars.items() if v.get()]
        secili_siniflar = [s for s,v in self._sinif_vars.items() if v.get()]

        if secili_konular:
            rows = db.get_sorular_by_sinif_konu(konu_ids=secili_konular)
        elif secili_siniflar:
            all_rows = []
            for sid in secili_siniflar:
                all_rows.extend(db.get_sorular_by_sinif_konu(sinif_id=sid))
            rows = all_rows
        else:
            rows = db.get_sorular_by_sinif_konu()

        if not rows:
            messagebox.showwarning("Uyarı","Seçili konularda soru bulunamadı!"); return None

        n = self.soru_n.get()
        if self.karistir.get(): random.shuffle(rows)
        if self.rastgele.get():
            selected = rows[:n]
        else:
            # Manuel seçim yerine hepsini sun
            selected = rows[:n]

        if len(selected) < n:
            messagebox.showinfo("Bilgi",f"Yalnızca {len(selected)} soru bulundu.")
        return selected

    # ── PDF Oluşturma ─────────────────────────────────────────────────────────
    def pdf_layout(self):
        sorular = self._get_sorular()
        if not sorular: return
        ed = PDFLayoutEditor(
            self, sorular,
            self.baslik.get(), self.sinif_n.get(), self.tarih.get(),
            self.cevap_pdf, self.cozum_pdf
        )
        ed.grab_set()

    def pdf_hizli(self):
        sorular = self._get_sorular()
        if not sorular: return
        if not RL_OK:
            messagebox.showerror("Hata","reportlab yüklü değil!"); return
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")],
            initialfile=f"sinav_{datetime.date.today().strftime('%Y%m%d')}.pdf",
            title="Sınav PDF Kaydet")
        if not path: return
        self._gen_sinav(path, sorular)
        if self.cevap_pdf.get():
            cp = filedialog.asksaveasfilename(
                defaultextension=".pdf", filetypes=[("PDF","*.pdf")],
                initialfile=f"cevap_{datetime.date.today().strftime('%Y%m%d')}.pdf",
                title="Cevap Anahtarı Kaydet")
            if cp:
                gen_cevap_pdf(cp, sorular, self.baslik.get(),
                              self.sinif_n.get(), self.tarih.get(),
                              self.cozum_pdf.get())
        self.durum.config(text="✅ PDF(ler) oluşturuldu!")
        messagebox.showinfo("✅","PDF oluşturuldu!")

    def _gen_sinav(self, path, sorular):
        register_fonts()

        def ps(name, **kw):
            kw.setdefault("fontName", F(kw.pop("bold", False)))
            return ParagraphStyle(name, **kw)

        doc = SimpleDocTemplate(path, pagesize=A4,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        story = []
        story.append(Paragraph(self.baslik.get() or "SINAV",
            ps("t", bold=True, fontSize=18, spaceAfter=4,
               textColor=colors.HexColor("#1E293B"), leading=22)))
        info = []; sv = self.sinif_n.get()
        if sv: info.append(f"Sinif: {sv}")
        info.append(f"Tarih: {self.tarih.get()}")
        info.append(f"Toplam Soru: {len(sorular)}")
        story.append(Paragraph("  |  ".join(info),
            ps("s", fontSize=10, textColor=colors.HexColor("#64748B"), leading=14)))
        story.append(Spacer(1, 0.3*cm))

        tbl = Table([["Ad Soyad: ___________________________",
                       "No: _____________","Puan: ___________"]],
                    colWidths=[9*cm, 5*cm, 4.5*cm])
        tbl.setStyle(TableStyle([
            ("FONTNAME",(0,0),(-1,-1), F()),
            ("FONTSIZE",(0,0),(-1,-1),10),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("LINEBELOW",(0,0),(-1,0),0.5,colors.HexColor("#CBD5E1"))]))
        story.append(tbl); story.append(Spacer(1, 0.4*cm))

        pw = A4[0]-3*cm; cw = (pw-0.5*cm)/2; imw = cw-0.4*cm; imh = 7.5*cm
        n_s = ps("n", fontSize=9, textColor=colors.HexColor("#94A3B8"), alignment=1)
        s_s = ps("s2", fontSize=9, textColor=colors.HexColor("#64748B"))
        pairs = [sorular[i:i+2] for i in range(0,len(sorular),2)]
        for pi, pair in enumerate(pairs):
            cells = []
            for li, (sid,blob,kad,*_) in enumerate(pair):
                qn = pi*2+li+1
                ci = [Paragraph(f"Soru {qn}", n_s)]
                try:
                    pil=Image.open(io.BytesIO(blob)); wp,hp=pil.size; ratio=wp/hp if hp else 1
                    rw=min(imw,imh*ratio); rh=rw/ratio
                    if rh>imh: rh=imh; rw=rh*ratio
                    ci.append(RLImage(io.BytesIO(blob),width=rw,height=rh))
                except: ci.append(Paragraph("[Gorsel yuklenemedi]",s_s))
                cells.append(ci)
            if len(cells)==1: cells.append([Spacer(1,1)])
            t2=Table([cells],colWidths=[cw,cw],hAlign="LEFT")
            t2.setStyle(TableStyle([
                ("VALIGN",(0,0),(-1,-1),"TOP"),("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("BOX",(0,0),(0,0),0.5,colors.HexColor("#E2E8F0")),
                ("BOX",(1,0),(1,0),0.5,colors.HexColor("#E2E8F0")),
                ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
                ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
            story.append(t2); story.append(Spacer(1, 0.25*cm))
        doc.build(story)
