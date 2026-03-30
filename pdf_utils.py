# -*- coding: utf-8 -*-
"""PDF yardımcı fonksiyonları — cevap anahtarı üretimi. Türkçe karakter destekli."""
import io, datetime
from PIL import Image

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Image as RLImage, Table, TableStyle, PageBreak)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    RL_OK = True
except ImportError:
    RL_OK = False

from pdf_fonts import register_fonts, F

def gen_cevap_pdf(path, sorular, baslik, sinif_adi, tarih, ekle_cozum):
    if not RL_OK: return
    register_fonts()

    def ps(name, **kw):
        kw.setdefault("fontName", F(kw.pop("bold", False)))
        return ParagraphStyle(name, **kw)

    title_s = ps("t", bold=True, fontSize=16, spaceAfter=4,
                 textColor=colors.HexColor("#1E293B"), leading=20)
    sub_s   = ps("s", fontSize=10, textColor=colors.HexColor("#64748B"), leading=14)
    head_s  = ps("h", bold=True, fontSize=13,
                 textColor=colors.HexColor("#1E293B"), spaceBefore=12, spaceAfter=6, leading=18)

    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    story.append(Paragraph(f"CEVAP ANAHTARI — {baslik or 'SINAV'}", title_s))
    info = []
    if sinif_adi: info.append(f"Sınıf: {sinif_adi}")
    if tarih:     info.append(f"Tarih: {tarih}")
    info.append(f"Toplam Soru: {len(sorular)}")
    story.append(Paragraph("  |  ".join(info), sub_s))
    story.append(Spacer(1, 0.5*cm))

    metin   = [(i+1, r[3]) for i,r in enumerate(sorular) if r[3]]
    cevap_g = [(i+1, r[4]) for i,r in enumerate(sorular) if r[4]]
    cozum_g = [(i+1, r[5]) for i,r in enumerate(sorular) if r[5]]

    # ── Metin cevaplar tablosu ──
    if metin:
        story.append(Paragraph("Cevaplar", head_s))
        COLS = 5
        tdata = []; hr = []; cr = []
        for idx, (num, cevap) in enumerate(metin):
            hr.append(Paragraph(f"Soru {num}",
                ps("th", bold=True, fontSize=10, alignment=1,
                   textColor=colors.HexColor("#1E293B"))))
            cr.append(Paragraph(str(cevap),
                ps("td", bold=True, fontSize=12, alignment=1,
                   textColor=colors.HexColor("#059669"))))
            if len(hr) == COLS or idx == len(metin)-1:
                while len(hr) < COLS:
                    hr.append(Paragraph("", ps("e")))
                    cr.append(Paragraph("", ps("e2")))
                tdata.append(hr); tdata.append(cr); hr = []; cr = []
        cw = (A4[0] - 3*cm) / COLS
        tbl = Table(tdata, colWidths=[cw]*COLS)
        tbl.setStyle(TableStyle([
            ("GRID",         (0,0),(-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ("ALIGN",        (0,0),(-1,-1), "CENTER"),
            ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
            ("TOPPADDING",   (0,0),(-1,-1), 7),
            ("BOTTOMPADDING",(0,0),(-1,-1), 7),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),
             [colors.HexColor("#EFF6FF"), colors.HexColor("#F8FAFC")]),
        ]))
        story.append(tbl); story.append(Spacer(1, 0.5*cm))

    # ── Cevap görselleri ──
    if cevap_g:
        story.append(Paragraph("Cevap Görselleri", head_s))
        story.append(Spacer(1, 0.3*cm))
        imw = 8*cm; imh = 6*cm
        pairs = [cevap_g[i:i+2] for i in range(0, len(cevap_g), 2)]
        for pair in pairs:
            cells = []
            for num, blob in pair:
                ci = [Paragraph(f"Soru {num}",
                    ps("cn", bold=True, fontSize=9, alignment=1,
                       textColor=colors.HexColor("#1E293B")))]
                try:
                    pil = Image.open(io.BytesIO(blob))
                    wp,hp = pil.size; ratio = wp/hp if hp else 1
                    rw = min(imw, imh*ratio); rh = rw/ratio
                    if rh > imh: rh=imh; rw=rh*ratio
                    ci.append(RLImage(io.BytesIO(blob), width=rw, height=rh))
                except:
                    ci.append(Paragraph("[Görsel yüklenemedi]", sub_s))
                cells.append(ci)
            if len(cells) == 1: cells.append([Spacer(1,1)])
            cw2 = (A4[0]-3*cm)/2
            t2 = Table([cells], colWidths=[cw2,cw2], hAlign="LEFT")
            t2.setStyle(TableStyle([
                ("VALIGN",       (0,0),(-1,-1),"TOP"),
                ("ALIGN",        (0,0),(-1,-1),"CENTER"),
                ("BOX",          (0,0),(0,0),0.5,colors.HexColor("#E2E8F0")),
                ("BOX",          (1,0),(1,0),0.5,colors.HexColor("#E2E8F0")),
                ("LEFTPADDING",  (0,0),(-1,-1),5),
                ("RIGHTPADDING", (0,0),(-1,-1),5),
                ("TOPPADDING",   (0,0),(-1,-1),6),
                ("BOTTOMPADDING",(0,0),(-1,-1),6),
            ]))
            story.append(t2); story.append(Spacer(1, 0.2*cm))

    # ── Çözüm görselleri ──
    if ekle_cozum and cozum_g:
        story.append(PageBreak())
        story.append(Paragraph("Çözümler", head_s))
        pw2 = A4[0]-3*cm; imh2 = 12*cm
        for num, blob in cozum_g:
            story.append(Paragraph(f"Soru {num} — Çözüm",
                ps("sn", fontSize=10, textColor=colors.HexColor("#F97316"))))
            try:
                pil = Image.open(io.BytesIO(blob))
                wp,hp = pil.size; ratio = wp/hp if hp else 1
                rw = min(pw2, imh2*ratio); rh = rw/ratio
                if rh > imh2: rh=imh2; rw=rh*ratio
                story.append(RLImage(io.BytesIO(blob), width=rw, height=rh))
            except:
                story.append(Paragraph("[Görsel yüklenemedi]", sub_s))
            story.append(Spacer(1, 0.4*cm))

    if not metin and not cevap_g:
        story.append(Paragraph(
            "Seçilen sorulara henüz cevap eklenmemiş.",
            ps("w", fontSize=12, textColor=colors.HexColor("#EF4444"))))

    doc.build(story)
