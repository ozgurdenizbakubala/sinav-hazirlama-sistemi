# -*- coding: utf-8 -*-
from tkinter import ttk

THEMES = {
    "light": {
        "bg":           "#F5F7FA",
        "panel":        "#FFFFFF",
        "panel2":       "#F0F4F8",
        "header":       "#1E293B",
        "header_fg":    "#F1F5F9",
        "text":         "#1E293B",
        "subtext":      "#64748B",
        "border":       "#E2E8F0",
        "entry_bg":     "#FFFFFF",
        "entry_fg":     "#1E293B",
        "entry_border": "#CBD5E1",
        "listbox_bg":   "#F8FAFC",
        "listbox_sel":  "#3B82F6",
        "listbox_fg":   "#1E293B",
        "card_bg":      "#FFFFFF",
        "card_hover":   "#F0F9FF",
        "canvas_bg":    "#F1F5F9",
        "btn_primary":  "#3B82F6",
        "btn_success":  "#10B981",
        "btn_danger":   "#EF4444",
        "btn_warning":  "#F59E0B",
        "btn_purple":   "#8B5CF6",
        "btn_orange":   "#F97316",
        "btn_dark":     "#1E293B",
        "btn_secondary":"#64748B",
        "highlight":    "#3B82F6",
        "accent":       "#06B6D4",
        "tab_bg":       "#E2E8F0",
        "tab_sel":      "#1E293B",
        "tab_fg":       "#64748B",
        "tab_sel_fg":   "#FFFFFF",
        "tag_blue":     "#DBEAFE",
        "tag_blue_fg":  "#1D4ED8",
        "tag_green":    "#D1FAE5",
        "tag_green_fg": "#065F46",
        "tag_red":      "#FEE2E2",
        "tag_red_fg":   "#991B1B",
        "separator":    "#E2E8F0",
        "shadow":       "#00000015",
    },
    "dark": {
        "bg":           "#0F172A",
        "panel":        "#1E293B",
        "panel2":       "#162032",
        "header":       "#0F172A",
        "header_fg":    "#F1F5F9",
        "text":         "#F1F5F9",
        "subtext":      "#94A3B8",
        "border":       "#334155",
        "entry_bg":     "#1E293B",
        "entry_fg":     "#F1F5F9",
        "entry_border": "#475569",
        "listbox_bg":   "#162032",
        "listbox_sel":  "#3B82F6",
        "listbox_fg":   "#F1F5F9",
        "card_bg":      "#1E293B",
        "card_hover":   "#243347",
        "canvas_bg":    "#0F172A",
        "btn_primary":  "#3B82F6",
        "btn_success":  "#10B981",
        "btn_danger":   "#EF4444",
        "btn_warning":  "#F59E0B",
        "btn_purple":   "#8B5CF6",
        "btn_orange":   "#F97316",
        "btn_dark":     "#334155",
        "btn_secondary":"#475569",
        "highlight":    "#3B82F6",
        "accent":       "#06B6D4",
        "tab_bg":       "#1E293B",
        "tab_sel":      "#3B82F6",
        "tab_fg":       "#94A3B8",
        "tab_sel_fg":   "#FFFFFF",
        "tag_blue":     "#1E3A5F",
        "tag_blue_fg":  "#93C5FD",
        "tag_green":    "#064E3B",
        "tag_green_fg": "#6EE7B7",
        "tag_red":      "#4C1D1D",
        "tag_red_fg":   "#FCA5A5",
        "separator":    "#334155",
        "shadow":       "#00000040",
    }
}

current_theme = "light"

def T():
    return THEMES[current_theme]

def toggle():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"

def save_theme():
    """Temayı veritabanına kaydet."""
    try:
        from db import set_ayar
        set_ayar("tema", current_theme)
    except Exception:
        pass

def load_theme():
    """Veritabanından temayı yükle."""
    global current_theme
    try:
        from db import get_ayar
        saved = get_ayar("tema")
        if saved in THEMES:
            current_theme = saved
    except Exception:
        pass

def apply_ttk_style():
    t = T()
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TNotebook",
        background=t["bg"], borderwidth=0, tabmargins=[0,0,0,0])
    style.configure("TNotebook.Tab",
        font=("Segoe UI", 10, "bold"),
        padding=[20, 10],
        background=t["tab_bg"],
        foreground=t["tab_fg"],
        borderwidth=0)
    style.map("TNotebook.Tab",
        background=[("selected", t["tab_sel"]), ("active", t["highlight"])],
        foreground=[("selected", t["tab_sel_fg"]), ("active", "#FFFFFF")])

    style.configure("TScrollbar",
        background=t["panel"], troughcolor=t["bg"],
        borderwidth=0, arrowcolor=t["subtext"], width=8)
    style.map("TScrollbar",
        background=[("active", t["highlight"])])

    style.configure("TSeparator", background=t["separator"])

def make_btn(parent, text, color_key, command, width=None, small=False):
    t = T()
    font_size = 9 if small else 10
    kw = dict(
        text=text,
        font=("Segoe UI", font_size, "bold"),
        bg=t[color_key],
        fg="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=command,
        padx=12 if not small else 8,
        pady=6 if not small else 4,
        bd=0,
        activebackground=t[color_key],
        activeforeground="#FFFFFF",
    )
    if width:
        kw["width"] = width
    import tkinter as tk
    btn = tk.Button(parent, **kw)
    # hover efekti
    import colorsys
    try:
        hex_color = t[color_key].lstrip("#")
        r,g,b = tuple(int(hex_color[i:i+2],16)/255 for i in (0,2,4))
        h,s,v = colorsys.rgb_to_hsv(r,g,b)
        hover_v = max(0, v - 0.1)
        hr,hg,hb = colorsys.hsv_to_rgb(h,s,hover_v)
        hover_color = "#{:02x}{:02x}{:02x}".format(int(hr*255),int(hg*255),int(hb*255))
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=t[color_key]))
    except:
        pass
    return btn

def make_label(parent, text, size=10, bold=False, color_key="text", **kw):
    import tkinter as tk
    t = T()
    weight = "bold" if bold else "normal"
    return tk.Label(parent, text=text,
                    font=("Segoe UI", size, weight),
                    bg=kw.pop("bg", t["panel"]),
                    fg=t[color_key], **kw)

def make_entry(parent, textvariable=None, show=None, width=None):
    import tkinter as tk
    t = T()
    kw = dict(
        font=("Segoe UI", 11),
        relief="solid", bd=1,
        bg=t["entry_bg"], fg=t["entry_fg"],
        insertbackground=t["text"],
        highlightthickness=1,
        highlightcolor=t["highlight"],
        highlightbackground=t["entry_border"],
    )
    if textvariable: kw["textvariable"] = textvariable
    if show:         kw["show"] = show
    if width:        kw["width"] = width
    return tk.Entry(parent, **kw)
