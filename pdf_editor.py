# -*- coding: utf-8 -*-
"""
PDF Düzenleme Editörü — Türkçe karakter destekli.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import io, os, datetime
from PIL import Image, ImageTk

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Image as RLImage, Table, TableStyle)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    RL_OK = True
except ImportError:
    RL_OK = False

from theme import T, make_btn
from pdf_fonts import register_fonts, F

A4_W_MM = 210.0
A4_H_MM = 297.0
PREVIEW_SCALE = 2.2
PDF_SCALE = 2.8346
MARGIN_MM = 15.0
TOP_MM    = 35.0

def mm_to_px(mm): return int(mm * PREVIEW_SCALE)
def mm_to_pt(mm): return mm * PDF_SCALE

PW = mm_to_px(A4_W_MM)
PH = mm_to_px(A4_H_MM)


class QuestionBox:
    MIN_H_MM = 20.0
    def __init__(self, idx, soru, x_mm, y_mm, w_mm, h_mm):
        self.idx=idx; self.soru=soru
        self.x_mm=x_mm; self.y_mm=y_mm; self.w_mm=w_mm; self.h_mm=h_mm
        self.cozum_h_mm=0.0; self.nokta_satirlar=0; self.selected=False
        self.box_id=self.lbl_id=self.img_id=self.han_id=None; self.photo=None

    @property
    def x_px(self): return mm_to_px(self.x_mm)
    @property
    def y_px(self): return mm_to_px(self.y_mm)
    @property
    def w_px(self): return mm_to_px(self.w_mm)
    @property
    def h_px(self): return mm_to_px(self.h_mm)


class PDFLayoutEditor(tk.Toplevel):
    def __init__(self, parent, sorular, baslik, sinif_adi, tarih,
                 cevap_var, cozum_var, on_done=None):
        super().__init__(parent)
        self.title("PDF Düzenleme Editörü")
        self.sorular=sorular; self.baslik=baslik
        self.sinif_adi=sinif_adi; self.tarih=tarih
        self.cevap_var=cevap_var; self.cozum_var=cozum_var; self.on_done=on_done
        t=T(); self.configure(bg=t["bg"])
        self.boxes=[]; self.sel_box=None
        self.drag_off=(0,0); self.drag_mode=None
        self._photos=[]
        self._build(); self._init_layout()
        self.geometry("1200x820")
        try: self.state("zoomed")
        except: pass

    def _build(self):
        t=T()
        tb=tk.Frame(self,bg=t["header"],pady=8); tb.pack(fill="x")
        tk.Label(tb,text="📐  PDF Düzenleme Editörü",
                 font=("Segoe UI",14,"bold"),
                 bg=t["header"],fg=t["header_fg"]).pack(side="left",padx=16)
        make_btn(tb,"📄  PDF Oluştur","btn_success",self._olustur).pack(side="right",padx=6,pady=4,ipady=6,ipadx=10)
        make_btn(tb,"👁  Önizleme","btn_primary",self._onizle).pack(side="right",padx=2,pady=4,ipady=6,ipadx=10)
        make_btn(tb,"🔄  Sıfırla","btn_secondary",self._init_layout).pack(side="right",padx=2,pady=4,ipady=6,ipadx=10)

        main=tk.Frame(self,bg=t["bg"]); main.pack(fill="both",expand=True)
        self._build_left(main)
        self._build_right(main)

    def _build_left(self,parent):
        t=T()
        left=tk.Frame(parent,bg=t["panel"],width=280,
                      highlightthickness=1,highlightbackground=t["border"])
        left.pack(side="left",fill="y",padx=(10,5),pady=10)
        left.pack_propagate(False)

        tk.Label(left,text="⚙️  Soru Ayarları",font=("Segoe UI",12,"bold"),
                 bg=t["panel"],fg=t["text"]).pack(pady=(16,2),padx=14,anchor="w")
        tk.Label(left,text="Bir soru kutusuna tıklayarak seçin.",
                 font=("Segoe UI",8),bg=t["panel"],fg=t["subtext"]).pack(padx=14,anchor="w",pady=(0,10))
        tk.Frame(left,bg=t["separator"],height=1).pack(fill="x",padx=14)

        self.sel_lbl=tk.Label(left,text="Seçili soru yok",
                              font=("Segoe UI",10,"bold"),
                              bg=t["panel"],fg=t["subtext"],wraplength=240)
        self.sel_lbl.pack(pady=(12,8),padx=14,anchor="w")

        tk.Label(left,text="📏  Çözüm Alanı Yüksekliği (mm):",
                 font=("Segoe UI",9,"bold"),bg=t["panel"],fg=t["text"]).pack(anchor="w",padx=14)
        self.cozum_h_var=tk.IntVar(value=0)
        sf=tk.Frame(left,bg=t["panel"]); sf.pack(fill="x",padx=14,pady=(4,12))
        tk.Scale(sf,from_=0,to=150,orient="horizontal",variable=self.cozum_h_var,
                 bg=t["panel"],fg=t["text"],troughcolor=t["border"],
                 highlightthickness=0,bd=0,font=("Segoe UI",8),
                 command=self._on_cozum_h).pack(fill="x")
        tk.Label(sf,textvariable=self.cozum_h_var,
                 font=("Segoe UI",9),bg=t["panel"],fg=t["subtext"]).pack(anchor="e")

        tk.Label(left,text="✏️  Noktalı Satır Sayısı:",
                 font=("Segoe UI",9,"bold"),bg=t["panel"],fg=t["text"]).pack(anchor="w",padx=14)
        self.nokta_var=tk.IntVar(value=0)
        nf=tk.Frame(left,bg=t["panel"]); nf.pack(fill="x",padx=14,pady=(4,12))
        tk.Scale(nf,from_=0,to=30,orient="horizontal",variable=self.nokta_var,
                 bg=t["panel"],fg=t["text"],troughcolor=t["border"],
                 highlightthickness=0,bd=0,font=("Segoe UI",8),
                 command=self._on_nokta).pack(fill="x")
        tk.Label(nf,textvariable=self.nokta_var,
                 font=("Segoe UI",9),bg=t["panel"],fg=t["subtext"]).pack(anchor="e")

        tk.Frame(left,bg=t["separator"],height=1).pack(fill="x",padx=14,pady=8)
        tk.Label(left,text="📋  Soru Listesi",
                 font=("Segoe UI",10,"bold"),bg=t["panel"],fg=t["text"]).pack(anchor="w",padx=14,pady=(4,6))
        lf=tk.Frame(left,bg=t["panel"]); lf.pack(fill="both",expand=True,padx=14,pady=(0,14))
        vsb=ttk.Scrollbar(lf)
        self.soru_list=tk.Listbox(lf,font=("Segoe UI",9),
                                   bg=t["listbox_bg"],fg=t["listbox_fg"],
                                   selectbackground=t["listbox_sel"],
                                   selectforeground="white",
                                   relief="flat",activestyle="none",
                                   yscrollcommand=vsb.set)
        vsb.config(command=self.soru_list.yview)
        vsb.pack(side="right",fill="y"); self.soru_list.pack(side="left",fill="both",expand=True)
        self.soru_list.bind("<<ListboxSelect>>",self._on_list_sel)

    def _build_right(self,parent):
        t=T()
        right=tk.Frame(parent,bg=t["bg"]); right.pack(side="left",fill="both",expand=True,padx=(5,10),pady=10)
        cf=tk.Frame(right,bg=t["canvas_bg"],
                    highlightthickness=1,highlightbackground=t["border"])
        cf.pack(fill="both",expand=True)
        hsb=ttk.Scrollbar(cf,orient="horizontal")
        vsb=ttk.Scrollbar(cf,orient="vertical")
        self.canvas=tk.Canvas(cf,bg="#C8CDD6",
                              scrollregion=(0,0,PW+60,PH+60),
                              xscrollcommand=hsb.set,yscrollcommand=vsb.set,
                              highlightthickness=0)
        hsb.config(command=self.canvas.xview)
        vsb.config(command=self.canvas.yview)
        vsb.pack(side="right",fill="y"); hsb.pack(side="bottom",fill="x")
        self.canvas.pack(fill="both",expand=True)
        self.canvas.bind("<ButtonPress-1>",   self._press)
        self.canvas.bind("<B1-Motion>",       self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.canvas.bind("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

    def _init_layout(self):
        self.canvas.delete("all"); self.boxes.clear()
        self._photos.clear(); self.sel_box=None
        self.soru_list.delete(0,"end")
        self.canvas.create_rectangle(36,36,36+PW,36+PH,fill="#00000020",outline="")
        self.canvas.create_rectangle(32,32,32+PW,32+PH,fill="white",outline="#AAAAAA",width=1)
        self._draw_header()
        cols=2 if len(self.sorular)>1 else 1
        gutter_mm=5.0
        col_w_mm=(A4_W_MM-2*MARGIN_MM-(cols-1)*gutter_mm)/cols
        def_h_mm=65.0
        for i,soru in enumerate(self.sorular):
            c_idx=i%cols; r_idx=i//cols
            x_mm=MARGIN_MM+c_idx*(col_w_mm+gutter_mm)
            y_mm=TOP_MM+r_idx*(def_h_mm+4)
            box=QuestionBox(i,soru,x_mm,y_mm,col_w_mm,def_h_mm)
            self.boxes.append(box); self._draw_box(box)
            self.soru_list.insert("end",f"  Soru {i+1}")

    def _draw_header(self):
        self.canvas.delete("header_items")
        cx=32+PW//2
        self.canvas.create_text(cx,32+mm_to_px(8),
            text=self.baslik or "SINAV",
            font=("Segoe UI",14,"bold"),fill="#1E293B",anchor="center",tag="header_items")
        info=[]
        if self.sinif_adi: info.append(f"Sınıf: {self.sinif_adi}")
        if self.tarih:     info.append(f"Tarih: {self.tarih}")
        if info:
            self.canvas.create_text(cx,32+mm_to_px(16),
                text="  |  ".join(info),
                font=("Segoe UI",9),fill="#64748B",anchor="center",tag="header_items")
        lx=32+mm_to_px(MARGIN_MM); rx=32+PW-mm_to_px(MARGIN_MM); ly=32+mm_to_px(26)
        self.canvas.create_line(lx,ly,rx,ly,fill="#CBD5E1",width=1,tag="header_items")
        self.canvas.create_text(lx,ly-6,
            text="Ad Soyad: ________________________",
            font=("Segoe UI",8),fill="#374151",anchor="w",tag="header_items")
        self.canvas.create_text(lx+mm_to_px(90),ly-6,
            text="No: __________   Puan: __________",
            font=("Segoe UI",8),fill="#374151",anchor="w",tag="header_items")

    def _draw_box(self,b):
        self._remove_box_items(b)
        ox,oy=32,32
        x1=ox+b.x_px; y1=oy+b.y_px; x2=x1+b.w_px; y2=y1+b.h_px
        col="#3B82F6" if b.selected else "#E2E8F0"
        fill="#EFF6FF" if b.selected else "#FFFFFF"
        b.box_id=self.canvas.create_rectangle(x1,y1,x2,y2,
            fill=fill,outline=col,width=2 if b.selected else 1)
        b.lbl_id=self.canvas.create_text(x1+6,y1+10,anchor="nw",
            text=f"Soru {b.idx+1}",font=("Segoe UI",9,"bold"),fill="#1E293B")
        try:
            ph=_to_tk_preview(b.soru[1],b.w_px-12,b.h_px-26)
            if ph:
                self._photos.append(ph); b.photo=ph
                b.img_id=self.canvas.create_image(
                    x1+b.w_px//2,y1+18+(b.h_px-26)//2,image=ph,anchor="center")
        except: pass
        if b.cozum_h_mm>0:
            cz_px=mm_to_px(b.cozum_h_mm); cy1=y2; cy2=cy1+cz_px
            self.canvas.create_rectangle(x1,cy1,x2,cy2,
                fill="#F8FAFC",outline="#94A3B8",width=1,dash=(4,3))
            self.canvas.create_text(x1+6,cy1+8,anchor="nw",
                text="[ Çözüm Alanı ]",
                font=("Segoe UI",8,"italic"),fill="#94A3B8")
            if b.nokta_satirlar>0:
                spacing=cz_px/(b.nokta_satirlar+1)
                for i in range(1,b.nokta_satirlar+1):
                    ly=cy1+int(i*spacing); nx=x1+8
                    while nx<x2-8:
                        self.canvas.create_text(nx,ly,text=".",
                            font=("Segoe UI",8),fill="#CBD5E1",anchor="center"); nx+=8
        hx=x1+b.w_px//2; hy=y1+b.h_px
        b.han_id=self.canvas.create_rectangle(hx-10,hy-5,hx+10,hy+5,
            fill="#3B82F6",outline="#1D4ED8",width=1,cursor="sb_v_double_arrow")
        self.canvas.create_text(hx,hy,text="↕",
            font=("Segoe UI",7,"bold"),fill="white",anchor="center")

    def _remove_box_items(self,b):
        for attr in ("box_id","lbl_id","img_id","han_id"):
            iid=getattr(b,attr,None)
            if iid: self.canvas.delete(iid); setattr(b,attr,None)

    def _press(self,e):
        cx=self.canvas.canvasx(e.x); cy=self.canvas.canvasy(e.y)
        clicked=None
        for b in self.boxes:
            ox,oy=32,32; bx1,by1=ox+b.x_px,oy+b.y_px; bx2=bx1+b.w_px
            total_h=mm_to_px(b.h_mm+b.cozum_h_mm)
            if bx1<=cx<=bx2 and by1<=cy<=by1+total_h: clicked=b; break
        self._deselect_all()
        if not clicked: return
        self.sel_box=clicked; clicked.selected=True
        self._update_left(clicked)
        hx=32+clicked.x_px+clicked.w_px//2; hy=32+clicked.y_px+clicked.h_px
        if abs(cx-hx)<=12 and abs(cy-hy)<=8:
            self.drag_mode="resize"; self.drag_off=(cx,cy-clicked.h_px)
        else:
            self.drag_mode="move"; self.drag_off=(cx-(32+clicked.x_px),cy-(32+clicked.y_px))
        self._draw_box(clicked)

    def _drag(self,e):
        if not self.sel_box: return
        cx=self.canvas.canvasx(e.x); cy=self.canvas.canvasy(e.y); b=self.sel_box
        if self.drag_mode=="resize":
            b.h_mm=max(QuestionBox.MIN_H_MM,(cy-self.drag_off[1])/PREVIEW_SCALE)
        elif self.drag_mode=="move":
            b.x_mm=max(0,min((cx-self.drag_off[0]-32)/PREVIEW_SCALE,A4_W_MM-b.w_mm))
            b.y_mm=max(TOP_MM,min((cy-self.drag_off[1]-32)/PREVIEW_SCALE,A4_H_MM-b.h_mm-b.cozum_h_mm))
        self._draw_box(b)

    def _release(self,e): self.drag_mode=None

    def _deselect_all(self):
        for b in self.boxes:
            if b.selected: b.selected=False; self._draw_box(b)
        self.sel_box=None
        self.sel_lbl.config(text="Seçili soru yok",fg=T()["subtext"])

    def _on_list_sel(self,e):
        sel=self.soru_list.curselection()
        if not sel: return
        self._deselect_all(); b=self.boxes[sel[0]]
        b.selected=True; self.sel_box=b; self._update_left(b); self._draw_box(b)
        self.canvas.yview_moveto((32+b.y_px-40)/(PH+64))

    def _update_left(self,b):
        t=T(); self.sel_lbl.config(text=f"Soru {b.idx+1} seçili",fg=t["highlight"])
        self.cozum_h_var.set(int(b.cozum_h_mm)); self.nokta_var.set(b.nokta_satirlar)

    def _on_cozum_h(self,val):
        if not self.sel_box: return
        self.sel_box.cozum_h_mm=float(val); self._draw_box(self.sel_box)

    def _on_nokta(self,val):
        if not self.sel_box: return
        self.sel_box.nokta_satirlar=int(val); self._draw_box(self.sel_box)

    def _onizle(self):
        win=tk.Toplevel(self); win.title("Önizleme")
        t=T(); win.configure(bg=t["bg"]); win.geometry("700x860")
        tk.Label(win,text="PDF önizleme (yaklaşık görünüm)",
                 font=("Segoe UI",9),bg=t["bg"],fg=t["subtext"]).pack(pady=6)
        cf=tk.Frame(win,bg=t["canvas_bg"]); cf.pack(fill="both",expand=True,padx=10,pady=(0,10))
        vsb=ttk.Scrollbar(cf)
        c=tk.Canvas(cf,bg="#C8CDD6",highlightthickness=0,
                    scrollregion=(0,0,PW+60,PH+60),yscrollcommand=vsb.set)
        vsb.config(command=c.yview); vsb.pack(side="right",fill="y"); c.pack(fill="both",expand=True)
        c.create_rectangle(36,36,36+PW,36+PH,fill="#00000020",outline="")
        c.create_rectangle(32,32,32+PW,32+PH,fill="white",outline="#AAAAAA",width=1)
        cx2=32+PW//2
        c.create_text(cx2,32+mm_to_px(8),text=self.baslik or "SINAV",
                      font=("Segoe UI",14,"bold"),fill="#1E293B",anchor="center")
        photos_p=[]
        for b in self.boxes:
            x1=32+b.x_px; y1=32+b.y_px; x2=x1+b.w_px; y2=y1+b.h_px
            c.create_rectangle(x1,y1,x2,y2,fill="white",outline="#E2E8F0",width=1)
            c.create_text(x1+5,y1+8,anchor="nw",text=f"Soru {b.idx+1}",
                          font=("Segoe UI",8,"bold"),fill="#1E293B")
            try:
                ph=_to_tk_preview(b.soru[1],b.w_px-10,b.h_px-22)
                if ph: photos_p.append(ph); c.create_image(x1+b.w_px//2,y1+16+(b.h_px-22)//2,image=ph,anchor="center")
            except: pass
            if b.cozum_h_mm>0:
                cz=mm_to_px(b.cozum_h_mm)
                c.create_rectangle(x1,y2,x2,y2+cz,fill="#F8FAFC",outline="#CBD5E1",width=1,dash=(3,2))
                c.create_text(x1+5,y2+6,anchor="nw",text="[ Çözüm ]",
                              font=("Segoe UI",7,"italic"),fill="#94A3B8")
        win._ph=photos_p

    def _olustur(self):
        if not RL_OK: messagebox.showerror("Hata","reportlab yüklü değil!"); return
        path=filedialog.asksaveasfilename(defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")],
            initialfile=f"sinav_{datetime.date.today().strftime('%Y%m%d')}.pdf",
            title="Sınav PDF Kaydet")
        if not path: return
        register_fonts()
        self._gen_pdf(path)
        if (self.cevap_var.get() if hasattr(self.cevap_var,'get') else self.cevap_var):
            cp=filedialog.asksaveasfilename(defaultextension=".pdf",
                filetypes=[("PDF","*.pdf")],
                initialfile=f"cevap_{datetime.date.today().strftime('%Y%m%d')}.pdf",
                title="Cevap Anahtarı Kaydet")
            if cp:
                from pdf_utils import gen_cevap_pdf
                sl=[b.soru for b in sorted(self.boxes,key=lambda x:x.idx)]
                gen_cevap_pdf(cp,sl,self.baslik,self.sinif_adi,self.tarih,
                              self.cozum_var.get() if hasattr(self.cozum_var,'get') else self.cozum_var)
        messagebox.showinfo("✅","PDF oluşturuldu!\n"+os.path.basename(path))
        if self.on_done: self.on_done()
        self.destroy()

    def _gen_pdf(self,path):
        pdf_w,pdf_h=A4; sx=pdf_w/PW; sy=pdf_h/PH
        c=rl_canvas.Canvas(path,pagesize=A4)
        # Başlık
        c.setFont(F(bold=True),16); c.setFillColor(colors.HexColor("#1E293B"))
        c.drawCentredString(pdf_w/2,pdf_h-mm_to_pt(12),self.baslik or "SINAV")
        c.setFont(F(),9); c.setFillColor(colors.HexColor("#64748B"))
        info=[]
        if self.sinif_adi: info.append(f"Sınıf: {self.sinif_adi}")
        if self.tarih: info.append(f"Tarih: {self.tarih}")
        if info: c.drawCentredString(pdf_w/2,pdf_h-mm_to_pt(20),"  |  ".join(info))
        c.setStrokeColor(colors.HexColor("#CBD5E1")); c.setLineWidth(0.5)
        c.line(mm_to_pt(MARGIN_MM),pdf_h-mm_to_pt(28),pdf_w-mm_to_pt(MARGIN_MM),pdf_h-mm_to_pt(28))
        c.setFont(F(),9); c.setFillColor(colors.HexColor("#374151"))
        c.drawString(mm_to_pt(MARGIN_MM),pdf_h-mm_to_pt(26),"Ad Soyad: _______________________________")
        c.drawString(mm_to_pt(MARGIN_MM+90),pdf_h-mm_to_pt(26),"No: _____________   Puan: _____________")
        # Soru kutuları
        for b in self.boxes:
            bx=mm_to_pt(b.x_mm); bh=mm_to_pt(b.h_mm)
            by=pdf_h-mm_to_pt(b.y_mm)-bh; bw=mm_to_pt(b.w_mm)
            c.setStrokeColor(colors.HexColor("#E2E8F0"))
            c.setFillColor(colors.white); c.setLineWidth(0.5)
            c.rect(bx,by,bw,bh,stroke=1,fill=1)
            c.setFont(F(bold=True),9); c.setFillColor(colors.HexColor("#1E293B"))
            c.drawString(bx+4,by+bh-14,f"Soru {b.idx+1}")
            try:
                blob=b.soru[1]; pil=Image.open(io.BytesIO(blob)).convert("RGB")
                max_iw=bw-8; max_ih=bh-20
                pil.thumbnail((int(max_iw*2),int(max_ih*2)),Image.LANCZOS)
                iw=min(max_iw,pil.width/2); ih=iw*pil.height/pil.width
                if ih>max_ih: ih=max_ih; iw=ih*pil.width/pil.height
                buf=io.BytesIO(); pil.save(buf,"PNG"); buf.seek(0)
                ir=ImageReader(buf)
                c.drawImage(ir,bx+(bw-iw)/2,by+(bh-ih)/2-4,iw,ih,
                            preserveAspectRatio=True,mask="auto")
            except: pass
            if b.cozum_h_mm>0:
                czh=mm_to_pt(b.cozum_h_mm); czy=by-czh
                c.setStrokeColor(colors.HexColor("#94A3B8"))
                c.setFillColor(colors.HexColor("#F8FAFC"))
                c.setLineWidth(0.4); c.setDash(4,3)
                c.rect(bx,czy,bw,czh,stroke=1,fill=1); c.setDash()
                c.setFont(F(),8); c.setFillColor(colors.HexColor("#94A3B8"))
                c.drawString(bx+4,czy+czh-12,"Çözüm Alanı")
                if b.nokta_satirlar>0:
                    spacing=czh/(b.nokta_satirlar+1)
                    c.setFont(F(),7); c.setFillColor(colors.HexColor("#CBD5E1"))
                    for i in range(1,b.nokta_satirlar+1):
                        ly_pt=czy+i*spacing; nx=bx+4
                        while nx<bx+bw-4: c.drawString(nx,ly_pt,"."); nx+=5.5
        c.save()


def _to_tk_preview(data,mw,mh):
    try:
        img=Image.open(io.BytesIO(data)); img.thumbnail((max(1,mw),max(1,mh)),Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except: return None
