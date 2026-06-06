import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageTk as _ITk

_WIN = sys.platform == "win32"

# ── Data constants ─────────────────────────────────────────────────────────────
COLUMNS    = ("freq", "amplitude", "phase")
COL_LABELS = ("Frequenz (Hz)", "Amplitude (dB)", "Phase (°)")
FREQ_UNITS = {"Hz": 1e0, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}
AMP_UNITS  = {"dB": None, "V": 1e0, "mV": 1e-3, "µV": 1e-6, "kV": 1e3}

# ── Color palette ──────────────────────────────────────────────────────────────
P = {
    "header":     "#1b2d4f",   # navy sidebar/header
    "header2":    "#243860",   # slightly lighter navy
    "sidebar":    "#1b2d4f",   # left panel background
    "bg":         "#f0f4f8",   # main content background
    "card":       "#ffffff",   # white cards
    "border":     "#dde3ee",   # subtle border
    "accent":     "#3b82f6",   # primary blue
    "accent_dk":  "#2563eb",   # darker blue (hover)
    "accent_lt":  "#dbeafe",   # light blue
    "text":       "#0f172a",   # primary text
    "text_inv":   "#e8f0fe",   # text on dark bg
    "muted":      "#94a3b8",   # muted text on dark
    "danger":     "#f43f5e",   # delete / danger
    "danger_dk":  "#e11d48",
    "success":    "#10b981",
    "warning":    "#f59e0b",
    "row_a":      "#f8fafc",
    "row_b":      "#ffffff",
    "input_bg":   "#f1f5f9",
    "sep":        "#2e4470",   # separator on dark bg
}

_SANS  = "Segoe UI"   if _WIN else "Sans"
_MONO  = "Courier New" if _WIN else "Monospace"
FONT      = (_SANS, 9)
FONT_B    = (_SANS, 9,  "bold")
FONT_LG   = (_SANS, 11, "bold")
FONT_SM   = (_SANS, 8)
FONT_XS   = (_SANS, 7, "bold")
FONT_MONO = (_MONO, 9)

# ── Button icons (generated via Pillow — no font/emoji dependency) ─────────────
_ICON_REFS: dict = {}  # keeps ImageTk.PhotoImage alive (GC would blank the button)

def _icon(name: str, size: int = 14) -> "_ITk.PhotoImage":
    key = (name, size)
    if key in _ICON_REFS:
        return _ICON_REFS[key]
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    c   = (255, 255, 255, 210)
    s, h = size, size - 1
    cx = s // 2
    if name == "chart":
        d.line([0, h, s - 1, h], fill=c)
        for i, bh in enumerate([s * 10 // 14, s * 13 // 14, s * 8 // 14]):
            x = 1 + i * (s // 3)
            d.rectangle([x, h - bh, x + s // 4, h - 1], fill=c)
    elif name == "save":
        d.rectangle([cx - 1, 1, cx + 1, s * 5 // 10], fill=c)
        for j in range(s * 5 // 10 + 1, s - 2):
            sp = j - s * 5 // 10
            d.line([cx - sp, j, cx + sp, j], fill=c)
        d.line([1, h, s - 2, h], fill=c, width=2)
    elif name == "import":
        # folder outline
        d.rectangle([0, s * 3 // 10, s - 1, h], outline=c)
        d.rectangle([0, s * 1 // 10, s * 2 // 5, s * 3 // 10], fill=c)
        # arrow pointing down (data coming in)
        d.rectangle([cx - 1, s * 4 // 10, cx + 1, s * 7 // 10], fill=c)
        for j in range(s * 7 // 10 + 1, h - 1):
            sp = j - s * 7 // 10
            d.line([cx - sp, j, cx + sp, j], fill=c)
    elif name == "export":
        # folder outline
        d.rectangle([0, s * 3 // 10, s - 1, h], outline=c)
        d.rectangle([0, s * 1 // 10, s * 2 // 5, s * 3 // 10], fill=c)
        # arrow pointing up (data going out)
        top = s * 2 // 10
        d.rectangle([cx - 1, s * 5 // 10, cx + 1, h - 2], fill=c)
        for j in range(top, s * 5 // 10):
            sp = s * 5 // 10 - j
            d.line([cx - sp, j, cx + sp, j], fill=c)
    elif name == "trash":
        d.rectangle([s // 4, s // 4 + 1, s * 3 // 4, h - 1], outline=c)
        d.line([s // 5, s // 4, s * 4 // 5, s // 4], fill=c, width=1)
        d.rectangle([s * 3 // 8, 1, s * 5 // 8, s // 4], outline=c)
        for x in [s * 2 // 5, cx, s * 3 // 5]:
            d.line([x, s // 3 + 1, x, h - 2], fill=c)
    photo = _ITk.PhotoImage(img)
    _ICON_REFS[key] = photo
    return photo


CSV_HELP = """\
Die App erkennt CSV-Dateien automatisch (Trennzeichen, Dezimalzeichen).

══════════════════════════════════════════════════════
FORMAT 1 — Deutsch  (Semikolon, Komma als Dezimal)
══════════════════════════════════════════════════════
Frequenz (Hz);Amplitude (dB);Phase (°)
100;-3,01;-45,0
1000;-6,02;-63,4

══════════════════════════════════════════════════════
FORMAT 2 — Englisch  (Komma, Punkt als Dezimal)
══════════════════════════════════════════════════════
Frequency (Hz),Amplitude (dB),Phase (deg)
100,-3.01,-45.0
1000,-6.02,-63.4

══════════════════════════════════════════════════════
FORMAT 3 — Ohne Kopfzeile
══════════════════════════════════════════════════════
100;-3,01;-45,0
1000;-6,02;-63,4
  Spaltenreihenfolge: 1. Frequenz  2. Amplitude  3. Phase

══════════════════════════════════════════════════════
FORMAT 4 — Mit Projektkommentar (wird beim Export erzeugt)
══════════════════════════════════════════════════════
# Projekt: Tiefpassfilter 1. Ordnung
Frequenz (Hz);Amplitude (dB);Phase (°)
100;-0,04;-0,57

  Zeilen mit # werden ignoriert.
  Projektname wird automatisch übernommen.

══════════════════════════════════════════════════════
SPALTEN-ERKENNUNG  (Schlüsselwörter)
══════════════════════════════════════════════════════
  Frequenz  →  freq, hz, f(
  Amplitude →  amp, db, gain, mag, betr
  Phase     →  phase, pha, grad, deg, winkel

══════════════════════════════════════════════════════
EINHEITEN
══════════════════════════════════════════════════════
  • Frequenz in Hz  (z.B. 1000 für 1 kHz)
  • Amplitude in dB
  • Phase in Grad (°)

  Spannungswerte (V/mV/µV/kV) können in der App
  eingegeben werden → Umrechnung: dB = 20·log₁₀(U)
  In CSV-Dateien werden immer dB gespeichert.
"""


# ── Helpers ────────────────────────────────────────────────────────────────────
def v_to_db(volts: float) -> float:
    if volts <= 0:
        raise ValueError("Spannung muss > 0 V sein.")
    return 20.0 * np.log10(volts)


def _btn(parent, text, cmd, bg, fg="#ffffff", width=None, icon=None, **kw):
    """Flat colored tk.Button with hover effect."""
    props = dict(bg=bg, fg=fg, activebackground=_shade(bg, -20),
                 activeforeground=fg, relief="flat", bd=0,
                 cursor="hand2", font=FONT_B, padx=10, pady=5)
    if width:
        props["width"] = width
    if icon is not None:
        props["image"]    = icon
        props["compound"] = tk.LEFT
        props["padx"]     = 8
    props.update(kw)
    b = tk.Button(parent, text=text, command=cmd, **props)
    b.bind("<Enter>", lambda _: b.config(bg=_shade(bg, -20)))
    b.bind("<Leave>", lambda _: b.config(bg=bg))
    return b


def _shade(hex_color: str, delta: int) -> str:
    """Lighten (delta>0) or darken (delta<0) a hex color."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = max(0, min(255, r + delta))
    g = max(0, min(255, g + delta))
    b = max(0, min(255, b + delta))
    return f"#{r:02x}{g:02x}{b:02x}"


def _section_label(parent, text: str) -> tk.Label:
    """Small uppercase section header for the dark sidebar."""
    return tk.Label(parent, text=text.upper(),
                    bg=P["sidebar"], fg=P["muted"],
                    font=FONT_XS, anchor="w",
                    padx=16, pady=0)


def _divider(parent) -> tk.Frame:
    return tk.Frame(parent, bg=P["sep"], height=1)


# ── Inline cell editor ─────────────────────────────────────────────────────────
class EditableCell(tk.Entry):
    def __init__(self, tree, item, col_idx, on_commit=None, on_before_commit=None, **kw):
        super().__init__(tree, **kw)
        self.tree, self.item, self.col_idx = tree, item, col_idx
        self._on_commit = on_commit
        self._on_before_commit = on_before_commit
        val = tree.item(item)["values"][col_idx]
        self.insert(0, str(val))
        self.select_range(0, tk.END)
        self.focus()
        self.bind("<Return>",   self._commit)
        self.bind("<Tab>",      self._commit)
        self.bind("<Escape>",   lambda _: self.destroy())
        self.bind("<FocusOut>", self._commit)

    def _commit(self, _=None):
        try:
            v = float(self.get().replace(",", "."))
        except ValueError:
            self.destroy()
            return
        if self._on_before_commit:
            self._on_before_commit()
        vals = list(self.tree.item(self.item)["values"])
        vals[self.col_idx] = v
        self.tree.item(self.item, values=vals)
        if self._on_commit:
            self._on_commit()
        self.destroy()


# ── Input row widget (entry + custom unit picker) ─────────────────────────────
class UnitEntry(tk.Frame):
    def __init__(self, parent, units: list[str], default_unit: str,
                 entry_width=12, fixed_unit=False, **kw):
        super().__init__(parent, bg=P["header2"],
                         highlightbackground=P["sep"],
                         highlightthickness=1, bd=0, **kw)
        self.unit_var = tk.StringVar(value=default_unit)
        self._units   = units

        self.entry = tk.Entry(
            self, bg=P["header2"], fg=P["text_inv"],
            relief="flat", bd=0, font=FONT, width=entry_width,
            insertbackground=P["text_inv"],
            selectbackground=P["accent"], selectforeground="#ffffff",
        )
        self.entry.pack(side=tk.LEFT, padx=(8, 0), pady=5)

        tk.Frame(self, bg=P["sep"], width=1).pack(
            side=tk.LEFT, fill=tk.Y, pady=5)

        if fixed_unit:
            tk.Label(self, text=default_unit,
                     bg=P["header2"], fg=P["muted"],
                     font=FONT, padx=10).pack(side=tk.LEFT)
        else:
            # ── Custom dropdown: button shows active unit, click → tk.Menu ──
            pick = tk.Frame(self, bg=P["header2"], cursor="hand2")
            pick.pack(side=tk.LEFT, fill=tk.Y)
            pick.bind("<Button-1>", lambda _: self._show_menu())

            self._unit_lbl = tk.Label(
                pick, textvariable=self.unit_var,
                bg=P["header2"], fg=P["text_inv"],
                font=FONT_B, padx=4, pady=0, cursor="hand2",
            )
            self._unit_lbl.pack(side=tk.LEFT, pady=5)
            self._unit_lbl.bind("<Button-1>", lambda _: self._show_menu())

            # "v" in a smaller, muted font works reliably on all platforms
            tk.Label(pick, text="v", bg=P["header2"], fg=P["muted"],
                     font=FONT_XS, padx=0).pack(
                side=tk.LEFT, padx=(0, 6), pady=5)

        self.entry.bind("<FocusIn>",  lambda _: self._highlight(True))
        self.entry.bind("<FocusOut>", lambda _: self._highlight(False))

    def _show_menu(self):
        m = tk.Menu(self, tearoff=0,
                    bg=P["header2"], fg=P["text_inv"],
                    activebackground=P["accent"],
                    activeforeground="#ffffff",
                    relief="flat", bd=1,
                    activeborderwidth=0, font=FONT)
        for u in self._units:
            m.add_command(
                label=f"  {u}  ",
                command=lambda v=u: self.unit_var.set(v),
            )
        lbl = self._unit_lbl
        m.post(lbl.winfo_rootx(),
               lbl.winfo_rooty() + lbl.winfo_height() + 2)

    def _highlight(self, on: bool):
        self.config(highlightbackground=P["accent"] if on else P["sep"])

    def get(self) -> str:        return self.entry.get()
    def unit(self) -> str:       return self.unit_var.get()
    def delete(self, *a):        self.entry.delete(*a)
    def focus(self):             self.entry.focus()
    def bind_entry(self, s, f):  self.entry.bind(s, f)


# ── Main application ───────────────────────────────────────────────────────────
class BodeTool:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bode Diagramm Tool")
        self.root.geometry("1340x800")
        self.root.minsize(980, 660)
        self.root.configure(bg=P["bg"])
        # View-toggle flags — created before menu/plot so both can bind to them
        self.opt_markers = tk.BooleanVar(value=True)
        self.opt_grid    = tk.BooleanVar(value=True)
        self.opt_dots    = tk.BooleanVar(value=True)
        self._dirty = False
        self._undo_stack: list = []
        self._redo_stack: list = []
        self._configure_ttk()
        self._build_menubar()
        self._build_ui()
        self._init_plot()
        self._bind_shortcuts()
        self.project_var.trace_add("write", lambda *_: self._set_dirty())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Menu bar ──────────────────────────────────────────────────────────────
    def _build_menubar(self):
        # All menu callbacks are deferred with after(5) so the menu fully
        # closes before any canvas redraw happens — prevents header flicker.
        def d(fn):
            return lambda: self.root.after(5, fn)

        MK = dict(
            bg=P["sidebar"], fg=P["text_inv"],
            activebackground=P["accent"], activeforeground="#ffffff",
            relief="flat", bd=0, font=FONT, activeborderwidth=0,
        )
        bar = tk.Menu(
            self.root,
            bg=P["header"], fg=P["text_inv"],
            activebackground=P["accent_dk"], activeforeground="#ffffff",
            relief="flat", bd=0, font=FONT,
        )
        self.root.configure(menu=bar)

        # ── Datei ─────────────────────────────────────────────────────
        m_file = tk.Menu(bar, tearoff=0, **MK)
        bar.add_cascade(label="  Datei  ", menu=m_file)

        m_file.add_command(label="  Neu",
                           command=d(self._new_project), accelerator="Strg+N")
        m_file.add_separator()
        m_file.add_command(label="  CSV importieren …",
                           command=d(self._import_csv), accelerator="Strg+O")
        m_file.add_command(label="  CSV exportieren …",
                           command=d(self._export_csv), accelerator="Strg+S")
        m_file.add_separator()

        m_save = tk.Menu(m_file, tearoff=0, **MK)
        m_file.add_cascade(label="  Plot speichern als …", menu=m_save)
        m_save.add_command(label="  PNG-Bild  (.png)",
                           command=d(lambda: self._save_plot("png")))
        m_save.add_command(label="  PDF-Dokument  (.pdf)",
                           command=d(lambda: self._save_plot("pdf")))
        m_save.add_command(label="  SVG-Vektorgrafik  (.svg)",
                           command=d(lambda: self._save_plot("svg")))

        m_file.add_separator()
        m_file.add_command(label="  Beenden",
                           command=self.root.quit, accelerator="Alt+F4")

        # ── Bearbeiten ─────────────────────────────────────────────────
        m_edit = tk.Menu(bar, tearoff=0, **MK)
        self._m_edit = m_edit
        bar.add_cascade(label="  Bearbeiten  ", menu=m_edit)

        m_edit.add_command(label="  Rückgängig",
                           command=d(self._undo), accelerator="Strg+Z",
                           state="disabled")
        m_edit.add_command(label="  Wiederherstellen",
                           command=d(self._redo), accelerator="Strg+Y",
                           state="disabled")
        m_edit.add_separator()
        m_edit.add_command(label="  Zeile löschen",
                           command=d(self._delete_selected), accelerator="Entf")
        m_edit.add_command(label="  Alle Zeilen löschen",
                           command=d(self._clear_all))
        m_edit.add_separator()
        m_edit.add_command(label="  Alle auswählen",
                           command=d(self._select_all), accelerator="Strg+A")
        m_edit.add_separator()
        m_edit.add_command(label="  Nach Frequenz sortieren",
                           command=d(lambda: self._sort("freq")))
        m_edit.add_command(label="  Nach Amplitude sortieren",
                           command=d(lambda: self._sort("amplitude")))
        m_edit.add_command(label="  Nach Phase sortieren",
                           command=d(lambda: self._sort("phase")))

        # ── Ansicht ────────────────────────────────────────────────────
        m_view = tk.Menu(bar, tearoff=0, **MK)
        bar.add_cascade(label="  Ansicht  ", menu=m_view)

        m_view.add_command(label="  Bode Diagramm erstellen",
                           command=d(self._plot_bode), accelerator="F5")
        m_view.add_separator()
        m_view.add_checkbutton(
            label="  −3 dB / −45° Markierungen",
            variable=self.opt_markers, command=d(self._plot_bode),
            selectcolor=P["accent"])
        m_view.add_checkbutton(
            label="  Gitterlinien",
            variable=self.opt_grid, command=d(self._toggle_grid),
            selectcolor=P["accent"])
        m_view.add_checkbutton(
            label="  Datenpunkte markieren",
            variable=self.opt_dots, command=d(self._plot_bode),
            selectcolor=P["accent"])

        # ── Hilfe ──────────────────────────────────────────────────────
        m_help = tk.Menu(bar, tearoff=0, **MK)
        bar.add_cascade(label="  Hilfe  ", menu=m_help)

        m_help.add_command(label="  CSV-Format Anleitung",
                           command=d(self._show_csv_help), accelerator="F1")
        m_help.add_separator()
        m_help.add_command(label="  Über Bode Diagramm Tool …",
                           command=d(self._show_about))

    # ── Unsaved-changes guard ──────────────────────────────────────────────────
    def _set_dirty(self):
        self._dirty = True

    def _data_changed(self):
        """Called after every data mutation; marks dirty and auto-refreshes the plot."""
        self._set_dirty()
        if self.tree.get_children():
            self._plot_bode(silent=True)
        else:
            self._init_plot()
            self.canvas.draw_idle()

    # ── Undo / Redo ───────────────────────────────────────────────────────────
    _MAX_UNDO = 50

    def _snapshot(self):
        return tuple(
            tuple(self.tree.item(i)["values"])
            for i in self.tree.get_children()
        )

    def _save_undo_state(self):
        state = self._snapshot()
        if self._undo_stack and self._undo_stack[-1] == state:
            return
        self._undo_stack.append(state)
        if len(self._undo_stack) > self._MAX_UNDO:
            del self._undo_stack[0]
        self._redo_stack.clear()
        self._update_undo_menu()

    def _undo(self):
        if not self._undo_stack:
            return
        self._redo_stack.append(self._snapshot())
        self._restore_state(self._undo_stack.pop())
        self._update_undo_menu()

    def _redo(self):
        if not self._redo_stack:
            return
        self._undo_stack.append(self._snapshot())
        self._restore_state(self._redo_stack.pop())
        self._update_undo_menu()

    def _restore_state(self, state):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, row in enumerate(state):
            self.tree.insert("", tk.END, values=row,
                             tags=("odd" if idx % 2 else "even",))
        self._set_dirty()
        self._update_status()
        if state:
            self._plot_bode(silent=True)
        else:
            self._init_plot()
            self.canvas.draw_idle()

    def _update_undo_menu(self):
        self._m_edit.entryconfig(
            "  Rückgängig",
            state="normal" if self._undo_stack else "disabled")
        self._m_edit.entryconfig(
            "  Wiederherstellen",
            state="normal" if self._redo_stack else "disabled")

    def _on_close(self):
        if self._dirty and self.tree.get_children():
            if not self._dlg(
                "Beenden",
                "Es gibt ungespeicherte Daten.\n"
                "Vor dem Beenden als CSV speichern?",
                "confirm",
            ):
                self.root.destroy()
            else:
                self._export_csv()
        else:
            self.root.destroy()

    # ── Keyboard shortcuts ─────────────────────────────────────────────────────
    def _bind_shortcuts(self):
        for seq, fn in [
            ("<Control-n>",       self._new_project),
            ("<Control-N>",       self._new_project),
            ("<Control-o>",       self._import_csv),
            ("<Control-O>",       self._import_csv),
            ("<Control-s>",       self._export_csv),
            ("<Control-S>",       self._export_csv),
            ("<Control-a>",       self._select_all),
            ("<Control-A>",       self._select_all),
            ("<Control-z>",       self._undo),
            ("<Control-Z>",       self._undo),
            ("<Control-y>",       self._redo),
            ("<Control-Y>",       self._redo),
            ("<Control-Shift-Z>", self._redo),
            ("<F5>",              self._plot_bode),
            ("<F1>",              self._show_csv_help),
        ]:
            self.root.bind_all(seq, lambda _, f=fn: f())

    # ── TTK styles ─────────────────────────────────────────────────────────────
    def _configure_ttk(self):
        s = ttk.Style()
        for theme in ("clam", "alt", "default"):
            if theme in s.theme_names():
                s.theme_use(theme)
                break

        # Treeview
        s.configure("Bode.Treeview",
                    background=P["row_b"],
                    fieldbackground=P["row_b"],
                    foreground=P["text"],
                    rowheight=26,
                    font=FONT,
                    borderwidth=0,
                    relief="flat")
        s.configure("Bode.Treeview.Heading",
                    background=P["bg"],
                    foreground=P["text"],
                    font=FONT_B,
                    relief="flat",
                    borderwidth=0,
                    padding=(4, 6))
        s.map("Bode.Treeview",
              background=[("selected", P["accent_lt"])],
              foreground=[("selected", P["accent_dk"])])
        s.map("Bode.Treeview.Heading",
              background=[("active", P["border"])])

        # Combobox inside UnitEntry
        s.configure("TCombobox", relief="flat", borderwidth=0,
                    selectbackground=P["accent_lt"],
                    selectforeground=P["accent_dk"])

        # Scrollbar
        s.configure("Vertical.TScrollbar",
                    troughcolor=P["bg"],
                    background=P["border"],
                    relief="flat", borderwidth=0)

    # ── UI scaffold ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header bar ──────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=P["header"], height=56)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="📈", bg=P["header"],
                 font=(_SANS, 20)).pack(side=tk.LEFT, padx=(16, 6))
        tk.Label(hdr, text="Bode Diagramm Tool",
                 bg=P["header"], fg=P["text_inv"],
                 font=(_SANS, 14, "bold")).pack(side=tk.LEFT, padx=(0, 28))

        tk.Label(hdr, text="Projektname:",
                 bg=P["header"], fg=P["muted"],
                 font=FONT_B).pack(side=tk.LEFT, padx=(0, 6))

        self.project_var = tk.StringVar()
        proj_e = tk.Entry(hdr, textvariable=self.project_var,
                          bg=P["header2"], fg=P["text_inv"],
                          insertbackground=P["text_inv"],
                          relief="flat", bd=0, font=(_SANS, 11),
                          width=32)
        proj_e.pack(side=tk.LEFT, ipady=6, padx=(0, 4))
        proj_e.bind("<KeyRelease>", lambda _: self._sync_title())

        # ── Two-column layout ────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=P["bg"])
        body.pack(fill=tk.BOTH, expand=True)

        # Left sidebar (dark navy)
        self.sidebar = tk.Frame(body, bg=P["sidebar"], width=320)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Thin border line between sidebar and content
        tk.Frame(body, bg=P["border"], width=1).pack(side=tk.LEFT, fill=tk.Y)

        # Right content area
        right = tk.Frame(body, bg=P["bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_sidebar(self.sidebar)
        self._build_plot_area(right)

        # ── Status bar ───────────────────────────────────────────────────────
        sb = tk.Frame(self.root, bg=P["header"], height=26)
        sb.pack(fill=tk.X, side=tk.BOTTOM)
        sb.pack_propagate(False)
        self.status_var = tk.StringVar(value="Keine Daten")
        tk.Label(sb, textvariable=self.status_var,
                 bg=P["header"], fg=P["muted"],
                 font=FONT_SM, anchor="w").pack(side=tk.LEFT, padx=14)

    def _sync_title(self):
        name = self.project_var.get().strip()
        self.root.title(f"Bode Diagramm Tool — {name}" if name
                        else "Bode Diagramm Tool")
        self._refresh_suptitle()

    def _update_status(self):
        n = len(self.tree.get_children())
        self.status_var.set(
            f"  {n} Datenpunkt{'e' if n != 1 else ''}  •  "
            "Doppelklick zum Bearbeiten  •  Entf zum Löschen"
        )

    # ── Sidebar ─────────────────────────────────────────────────────────────
    def _build_sidebar(self, parent):
        # Pack BOTTOM items first (first packed = very bottom).
        # This lets the treeview (packed TOP + expand) fill the remaining middle.

        # ── CTA buttons — anchored to bottom ──────────────────────────
        cta = tk.Frame(parent, bg=P["sidebar"], padx=12, pady=10)
        cta.pack(side=tk.BOTTOM, fill=tk.X)
        _btn(cta, "Plot speichern",
             self._save_plot, P["accent"],
             icon=_icon("save")).pack(fill=tk.X, ipady=6)

        # ── Section: Datei ─────────────────────────────────────────────
        _divider(parent).pack(side=tk.BOTTOM, fill=tk.X)
        fa = tk.Frame(parent, bg=P["sidebar"], padx=12)
        fa.pack(side=tk.BOTTOM, fill=tk.X)
        fa.columnconfigure(0, weight=1)
        fa.columnconfigure(1, weight=1)
        for i, (lbl, cmd, ico) in enumerate([
            ("CSV importieren", self._import_csv,   "import"),
            ("CSV exportieren", self._export_csv,   "export"),
            ("?  CSV-Format",   self._show_csv_help, None),
        ]):
            r, c = divmod(i, 2)
            _btn(fa, lbl, cmd, "#2e4470", P["text_inv"],
                 icon=_icon(ico) if ico else None).grid(
                row=r, column=c, sticky="ew",
                padx=(0, 4) if c == 0 else (4, 0), pady=(0, 5))
        _section_label(parent, "Datei").pack(
            side=tk.BOTTOM, fill=tk.X, pady=(8, 4))

        # ── Section: Tabelle ───────────────────────────────────────────
        _divider(parent).pack(side=tk.BOTTOM, fill=tk.X)
        ra = tk.Frame(parent, bg=P["sidebar"], padx=12)
        ra.pack(side=tk.BOTTOM, fill=tk.X)
        ra.columnconfigure(0, weight=1)
        ra.columnconfigure(1, weight=1)
        _btn(ra, "Zeile löschen", self._delete_selected,
             "#2e4470", P["text_inv"], icon=_icon("trash")).grid(
            row=0, column=0, sticky="ew", padx=(0, 4))
        _btn(ra, "✕  Alle löschen", self._clear_all,
             "#2e4470", P["text_inv"]).grid(
            row=0, column=1, sticky="ew", padx=(4, 0))
        _btn(ra, "↻  Aktualisieren", self._plot_bode,
             "#2e4470", P["text_inv"]).grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        _section_label(parent, "Tabelle").pack(
            side=tk.BOTTOM, fill=tk.X, pady=(8, 4))

        # ── Section: Zeile einfügen ────────────────────────────────────
        _divider(parent).pack(side=tk.BOTTOM, fill=tk.X)
        ef = tk.Frame(parent, bg=P["sidebar"], padx=12)
        ef.pack(side=tk.BOTTOM, fill=tk.X)
        ef.columnconfigure(1, weight=1)

        self.ue_freq  = self._input_row(ef, "Frequenz",
                                         list(FREQ_UNITS), "Hz",  row=0)
        self.ue_amp   = self._input_row(ef, "Amplitude",
                                         list(AMP_UNITS),  "dB",  row=1)
        self.ue_phase = self._input_row(ef, "Phase",
                                         ["°"],             "°",   row=2,
                                         fixed_unit=True)
        for ue in (self.ue_freq, self.ue_amp, self.ue_phase):
            ue.bind_entry("<Return>", self._on_entry_return)
        _btn(ef, "+ Hinzufügen", self._add_row,
             P["accent"]).grid(row=3, column=0, columnspan=2,
                               sticky="ew", pady=(8, 0))

        _section_label(parent, "Zeile einfügen").pack(
            side=tk.BOTTOM, fill=tk.X, pady=(8, 4))
        _divider(parent).pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))

        # ── Section: Messdaten (TOP) — treeview fills the middle ───────
        _section_label(parent, "Messdaten").pack(fill=tk.X, pady=(14, 4))

        tree_wrap = tk.Frame(parent, bg=P["sidebar"], padx=12)
        tree_wrap.pack(fill=tk.BOTH, expand=True)

        tree_card = tk.Frame(tree_wrap, bg=P["row_b"],
                             highlightbackground=P["border"],
                             highlightthickness=1)
        tree_card.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_card, style="Bode.Treeview",
                                  columns=COLUMNS, show="headings",
                                  selectmode="extended")
        widths = (88, 95, 80)
        for col, lbl, w in zip(COLUMNS, COL_LABELS, widths):
            self.tree.heading(col, text=lbl,
                              command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, anchor="center", stretch=True)
        self.tree.tag_configure("odd",  background=P["row_a"])
        self.tree.tag_configure("even", background=P["row_b"])

        vsb = ttk.Scrollbar(tree_card, orient=tk.VERTICAL,
                             command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Delete>",   lambda _: self._delete_selected())

    def _input_row(self, parent, label: str, units: list, default: str,
                   row: int, fixed_unit=False) -> UnitEntry:
        tk.Label(parent, text=label, bg=P["sidebar"], fg=P["text_inv"],
                 font=FONT, anchor="w").grid(
            row=row, column=0, sticky="w", pady=(0, 6))

        ue = UnitEntry(parent, units, default,
                       entry_width=11, fixed_unit=fixed_unit)
        ue.grid(row=row, column=1, sticky="ew", padx=(6, 0), pady=(0, 6))
        parent.columnconfigure(1, weight=1)
        return ue

    # ── Plot area ────────────────────────────────────────────────────────────
    def _build_plot_area(self, parent):
        self.fig = Figure(figsize=(9, 6.5), dpi=100)
        self.fig.patch.set_facecolor(P["bg"])
        self.ax_mag   = self.fig.add_subplot(2, 1, 1)
        self.ax_phase = self.fig.add_subplot(2, 1, 2)
        self.fig.subplots_adjust(
            hspace=0.42, top=0.90, bottom=0.09, left=0.09, right=0.97)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True,
                                          padx=0, pady=0)

        tb_frame = tk.Frame(parent, bg=P["bg"])
        tb_frame.pack(fill=tk.X)
        toolbar = NavigationToolbar2Tk(self.canvas, tb_frame)
        toolbar.update()
        # Apply theme colors to toolbar and all its children
        self._style_widget(toolbar, P["bg"], P["text"])

    @staticmethod
    def _style_widget(widget, bg: str, fg: str):
        """Recursively apply bg/fg to a widget tree (best-effort)."""
        try:
            widget.configure(bg=bg)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            try:
                child.configure(
                    bg=bg, fg=fg,
                    activebackground=_shade(bg, -15),
                    activeforeground=fg,
                    relief="flat", bd=0,
                    highlightthickness=0,
                )
            except tk.TclError:
                pass
            BodeTool._style_widget(child, bg, fg)

    def _init_plot(self):
        for ax, title, ylabel in (
            (self.ax_mag,   "Amplitudengang", "Amplitude (dB)"),
            (self.ax_phase, "Phasengang",     "Phase (°)"),
        ):
            ax.clear()
            ax.set_facecolor("#fafcff")
            ax.set_xscale("log")
            ax.set_title(title, fontsize=10, fontweight="bold",
                         color=P["text"], pad=8)
            ax.set_ylabel(ylabel, fontsize=9, color=P["text"])
            ax.tick_params(colors=P["text"], labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(P["border"])
            ax.grid(True, which="major", color=P["border"],
                    linestyle="-", linewidth=0.8)
            ax.grid(True, which="minor", color=P["border"],
                    linestyle=":", linewidth=0.5, alpha=0.6)
        self.ax_phase.set_xlabel("Frequenz (Hz)", fontsize=9, color=P["text"])
        self._refresh_suptitle()

    def _refresh_suptitle(self):
        name = self.project_var.get().strip()
        title = f"Bode Diagramm  —  {name}" if name else "Bode Diagramm"
        self.fig.suptitle(title, fontsize=13, fontweight="bold",
                          color=P["text"], y=0.97)
        self.canvas.draw_idle()

    # ── Styled dialog (replaces messagebox) ──────────────────────────────────
    def _dlg(self, title: str, msg: str, kind: str = "info") -> bool:
        """Modal dialog matching the app theme.
        kind: 'info' | 'error' | 'warn' | 'confirm'
        Returns True when user clicks OK / Ja."""
        accent = {"info":  P["accent"], "error": P["danger"],
                  "warn":  P["warning"], "confirm": P["warning"]}.get(kind, P["accent"])
        icon   = {"info": "i", "error": "✕", "warn": "!", "confirm": "?"}.get(kind, "i")

        result = [False]
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=P["bg"])
        win.resizable(False, False)
        win.grab_set()
        win.focus_set()

        # Coloured accent bar at top
        tk.Frame(win, bg=accent, height=5).pack(fill=tk.X)

        # Body
        body = tk.Frame(win, bg=P["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=(18, 10))

        # Icon pill + title
        top = tk.Frame(body, bg=P["bg"])
        top.pack(fill=tk.X, pady=(0, 10))
        tk.Label(top, text=icon, bg=accent, fg="#ffffff",
                 font=FONT_B, padx=7, pady=2).pack(side=tk.LEFT)
        tk.Label(top, text=f"  {title}", bg=P["bg"], fg=P["text"],
                 font=FONT_B).pack(side=tk.LEFT)

        # Message text
        tk.Label(body, text=msg, bg=P["bg"], fg=P["text"],
                 font=FONT, wraplength=320, justify="left").pack(anchor="w")

        # Buttons
        br = tk.Frame(win, bg=P["bg"])
        br.pack(fill=tk.X, padx=24, pady=(8, 20))
        if kind == "confirm":
            def _yes():
                result[0] = True
                win.destroy()
            _btn(br, "Ja",   _yes,        P["accent"], padx=14).pack(side=tk.RIGHT, padx=(6, 0), ipady=4)
            _btn(br, "Nein", win.destroy, "#2e4470", P["text_inv"], padx=14).pack(side=tk.RIGHT, ipady=4)
        else:
            _btn(br, "OK", win.destroy, P["accent"], padx=14).pack(side=tk.RIGHT, ipady=4)

        # Centre on parent
        win.update_idletasks()
        pw, ph = self.root.winfo_width(), self.root.winfo_height()
        px, py = self.root.winfo_x(),     self.root.winfo_y()
        ww, wh = win.winfo_reqwidth(),    win.winfo_reqheight()
        win.geometry(f"+{px + (pw - ww)//2}+{py + (ph - wh)//2}")

        win.wait_window()
        return result[0]

    # ── Table helpers ────────────────────────────────────────────────────────
    def _retag(self):
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, tags=("odd" if i % 2 else "even",))

    def _on_entry_return(self, event):
        ues = [self.ue_freq, self.ue_amp, self.ue_phase]
        widgets = [ue.entry for ue in ues]
        idx = widgets.index(event.widget)
        if idx < len(ues) - 1:
            ues[idx + 1].focus()
        else:
            self._add_row()

    def _parse_freq(self, raw: str) -> float:
        val = float(raw.strip().replace(",", "."))
        val *= FREQ_UNITS[self.ue_freq.unit()]
        if val <= 0:
            raise ValueError("Frequenz muss > 0 sein.")
        return val

    def _parse_amp(self, raw: str) -> float:
        val  = float(raw.strip().replace(",", "."))
        unit = self.ue_amp.unit()
        if unit == "dB":
            return val
        return v_to_db(val * AMP_UNITS[unit])

    def _add_row(self):
        try:
            freq  = self._parse_freq(self.ue_freq.get())
            amp   = self._parse_amp(self.ue_amp.get())
            phase = float(self.ue_phase.get().strip().replace(",", "."))
        except ValueError as exc:
            self._dlg("Eingabefehler",
                      str(exc) or "Bitte gültige Zahlen eingeben.", "error")
            return
        self._save_undo_state()
        n = len(self.tree.get_children())
        tag = "odd" if n % 2 else "even"
        self.tree.insert("", tk.END,
                         values=(round(freq, 6), round(amp, 4), round(phase, 4)),
                         tags=(tag,))
        for ue in (self.ue_freq, self.ue_amp, self.ue_phase):
            ue.delete(0, tk.END)
        self.ue_freq.focus()
        self._data_changed()
        self._update_status()

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            self._dlg("Hinweis", "Keine Zeile ausgewählt.", "info")
            return
        self._save_undo_state()
        for item in sel:
            self.tree.delete(item)
        self._retag()
        self._data_changed()
        self._update_status()

    def _clear_all(self):
        if self.tree.get_children() and \
                self._dlg("Bestätigen", "Alle Zeilen löschen?", "confirm"):
            self._save_undo_state()
            for item in self.tree.get_children():
                self.tree.delete(item)
            self._data_changed()
            self._update_status()

    def _on_double_click(self, event):
        row = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row or not col:
            return
        col_idx = int(col.lstrip("#")) - 1
        x, y, w, h = self.tree.bbox(row, col)
        EditableCell(self.tree, row, col_idx,
                     on_before_commit=self._save_undo_state,
                     on_commit=self._data_changed,
                     font=FONT, bg=P["accent_lt"],
                     fg=P["text"]).place(x=x, y=y, width=w, height=h)

    def _sort(self, col):
        self._save_undo_state()
        col_idx = COLUMNS.index(col)
        data = [(float(self.tree.item(k)["values"][col_idx]), k)
                for k in self.tree.get_children()]
        data.sort()
        for i, (_, k) in enumerate(data):
            self.tree.move(k, "", i)
        self._retag()

    def _get_sorted_data(self):
        rows = []
        for item in self.tree.get_children():
            v = self.tree.item(item)["values"]
            rows.append((float(v[0]), float(v[1]), float(v[2])))
        return sorted(rows, key=lambda r: r[0])

    # ── CSV ──────────────────────────────────────────────────────────────────
    def _sniff(self, path):
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            sample = f.read(4096)
        delim   = ";" if sample.count(";") >= sample.count(",") else ","
        decimal = "," if delim == ";" else "."
        return delim, decimal

    def _import_csv(self):
        path = filedialog.askopenfilename(
            title="CSV Datei öffnen",
            filetypes=[("CSV Dateien", "*.csv"), ("Alle Dateien", "*.*")])
        if not path:
            return
        self._save_undo_state()
        delim, decimal = self._sniff(path)

        def parse(s):
            return float(s.strip().replace(decimal, "."))

        count = errors = 0
        try:
            with open(path, encoding="utf-8-sig",
                      errors="replace", newline="") as f:
                reader = csv.reader(f, delimiter=delim)
                freq_idx = amp_idx = phase_idx = None
                header_done = False

                for raw in reader:
                    if not any(c.strip() for c in raw):
                        continue
                    first = raw[0].strip()
                    if first.startswith("#"):
                        if "projekt" in first.lower() and ":" in first:
                            self.project_var.set(
                                first.split(":", 1)[1].strip())
                            self._sync_title()
                        continue

                    if not header_done:
                        header_done = True
                        hl = [c.lower().strip() for c in raw]
                        for i, h in enumerate(hl):
                            if any(k in h for k in ("freq","hz","f(")):
                                freq_idx = i
                            elif any(k in h for k in ("amp","db","gain",
                                                       "mag","betr")):
                                amp_idx = i
                            elif any(k in h for k in ("phase","pha","grad",
                                                       "deg","winkel")):
                                phase_idx = i
                        if None in (freq_idx, amp_idx, phase_idx):
                            freq_idx, amp_idx, phase_idx = 0, 1, 2
                            try:
                                n = len(self.tree.get_children())
                                self.tree.insert(
                                    "", tk.END,
                                    values=(parse(raw[0]),
                                            parse(raw[1]),
                                            parse(raw[2])),
                                    tags=("odd" if n % 2 else "even",))
                                count += 1
                            except (ValueError, IndexError):
                                pass
                        continue

                    try:
                        n = len(self.tree.get_children())
                        self.tree.insert(
                            "", tk.END,
                            values=(parse(raw[freq_idx]),
                                    parse(raw[amp_idx]),
                                    parse(raw[phase_idx])),
                            tags=("odd" if n % 2 else "even",))
                        count += 1
                    except (ValueError, IndexError):
                        errors += 1

        except Exception as exc:
            self._dlg("Importfehler", str(exc), "error")
            return

        self._update_status()
        self._data_changed()
        msg = f"{count} Zeilen importiert."
        if errors:
            msg += f"\n{errors} Zeile(n) übersprungen."
        self._dlg("Import", msg, "info")

    def _export_csv(self):
        data = self._get_sorted_data()
        if not data:
            self._dlg("Hinweis", "Keine Daten vorhanden.", "info")
            return
        path = filedialog.asksaveasfilename(
            title="CSV speichern", defaultextension=".csv",
            filetypes=[("CSV Dateien", "*.csv"), ("Alle Dateien", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=";")
                proj = self.project_var.get().strip()
                if proj:
                    w.writerow([f"# Projekt: {proj}"])
                w.writerow(COL_LABELS)
                w.writerows(data)
            self._dirty = False
            self._dlg("Export", f"Gespeichert:\n{path}", "info")
        except Exception as exc:
            self._dlg("Exportfehler", str(exc), "error")

    def _show_csv_help(self):
        win = tk.Toplevel(self.root)
        win.title("CSV-Format Anleitung")
        win.geometry("600x580")
        win.configure(bg=P["sidebar"])
        win.resizable(True, True)

        # Header bar
        hdr = tk.Frame(win, bg=P["header"], height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="CSV-Format Anleitung",
                 bg=P["header"], fg=P["text_inv"],
                 font=FONT_LG).pack(side=tk.LEFT, padx=18, pady=14)
        _divider(win).pack(fill=tk.X)

        # Text area
        card = tk.Frame(win, bg=P["sidebar"], padx=14, pady=10)
        card.pack(fill=tk.BOTH, expand=True)

        txt = tk.Text(card, wrap=tk.WORD, font=FONT_MONO,
                      bg=P["header2"], fg=P["text_inv"],
                      insertbackground=P["text_inv"],
                      padx=14, pady=12, relief="flat",
                      selectbackground=P["accent"],
                      selectforeground="#ffffff",
                      borderwidth=0)
        sb = ttk.Scrollbar(card, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        txt.insert("1.0", CSV_HELP)
        txt.config(state=tk.DISABLED)

        _divider(win).pack(fill=tk.X)
        foot = tk.Frame(win, bg=P["sidebar"])
        foot.pack(fill=tk.X, padx=18, pady=(10, 14))
        _btn(foot, "Schließen", win.destroy,
             P["accent"], padx=14).pack(side=tk.RIGHT, ipady=5)

    # ── Plotting ─────────────────────────────────────────────────────────────
    def _plot_bode(self, silent=False):
        data = self._get_sorted_data()
        if not data:
            if not silent:
                self._dlg("Warnung", "Keine Daten vorhanden.", "warn")
            return

        freqs  = np.array([d[0] for d in data])
        amps   = np.array([d[1] for d in data])
        phases = np.array([d[2] for d in data])

        self._init_plot()

        use_dots = self.opt_dots.get() and len(data) <= 80
        marker = "o" if use_dots else ""
        kw = dict(linewidth=2.2, marker=marker, markersize=5,
                  markerfacecolor="white", markeredgewidth=1.5,
                  solid_capstyle="round")

        self.ax_mag.semilogx(freqs, amps,   color=P["accent"],
                             label="Amplitude (dB)", **kw)
        self.ax_mag.set_ylabel("Amplitude (dB)", fontsize=9)
        self.ax_mag.legend(fontsize=8, framealpha=0.9)

        self.ax_phase.semilogx(freqs, phases, color="#e85d04",
                               label="Phase (°)", **kw)
        self.ax_phase.set_ylabel("Phase (°)", fontsize=9)
        self.ax_phase.set_xlabel("Frequenz (Hz)", fontsize=9)
        self.ax_phase.legend(fontsize=8, framealpha=0.9)

        if self.opt_markers.get():
            self._add_marker(self.ax_mag,   freqs, amps,   -3,  P["warning"], "−3 dB")
            self._add_marker(self.ax_phase, freqs, phases, -45, P["success"], "−45°")

        self.canvas.draw_idle()

    def _add_marker(self, ax, x, y, target, color, label):
        ax.axhline(target, color=color, linestyle="--",
                   linewidth=1.2, alpha=0.85, label=label)
        for i in range(len(y) - 1):
            y0, y1 = y[i], y[i + 1]
            if min(y0, y1) <= target <= max(y0, y1):
                t = (target - y0) / (y1 - y0)
                xc = np.exp(np.log(x[i]) + t * (np.log(x[i+1]) - np.log(x[i])))
                ax.axvline(xc, color=color, linestyle=":",
                           linewidth=1.0, alpha=0.75)
                ax.annotate(f" {xc:.3g} Hz",
                            xy=(xc, target),
                            xytext=(4, 5), textcoords="offset points",
                            fontsize=7.5, color=color, fontweight="bold")
                break
        ax.legend(fontsize=8, framealpha=0.9)

    def _save_plot(self, fmt: str | None = None):
        fmt_map = {
            "png": ("PNG-Bild",        "*.png"),
            "pdf": ("PDF-Dokument",    "*.pdf"),
            "svg": ("SVG-Vektorgrafik","*.svg"),
        }
        if fmt and fmt in fmt_map:
            lbl, ext = fmt_map[fmt]
            path = filedialog.asksaveasfilename(
                title=f"Plot als {fmt.upper()} speichern",
                defaultextension=f".{fmt}",
                filetypes=[(lbl, ext), ("Alle Dateien", "*.*")])
        else:
            path = filedialog.asksaveasfilename(
                title="Diagramm speichern", defaultextension=".png",
                filetypes=[("PNG-Bild", "*.png"),
                            ("PDF-Dokument", "*.pdf"),
                            ("SVG-Vektorgrafik", "*.svg")])
        if not path:
            return
        try:
            self.fig.savefig(path, dpi=200, bbox_inches="tight",
                             facecolor=P["bg"])
            self._dlg("Gespeichert", f"Diagramm gespeichert:\n{path}", "info")
        except Exception as exc:
            self._dlg("Fehler", str(exc), "error")


    # ── Extra actions (menu targets) ──────────────────────────────────────────
    def _new_project(self):
        if self.tree.get_children():
            if not self._dlg("Neu",
                    "Alle Daten verwerfen und neu beginnen?", "confirm"):
                return
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.project_var.set("")
        self._sync_title()
        self._init_plot()
        self._update_status()
        self._dirty = False

    def _select_all(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def _toggle_grid(self):
        on = self.opt_grid.get()
        for ax in (self.ax_mag, self.ax_phase):
            ax.grid(on, which="major", color=P["border"],
                    linestyle="-", linewidth=0.8)
            ax.grid(on, which="minor", color=P["border"],
                    linestyle=":", linewidth=0.5, alpha=0.6)
        self.canvas.draw_idle()

    def _open_url(self, url: str):
        import webbrowser
        webbrowser.open(url)

    def _show_about(self):
        win = tk.Toplevel(self.root)
        win.title("Über Bode Diagramm Tool")
        win.geometry("380x290")
        win.configure(bg=P["sidebar"])
        win.resizable(False, False)

        # Full-width dark header
        hdr = tk.Frame(win, bg=P["header"], height=72)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📈  Bode Diagramm Tool",
                 bg=P["header"], fg=P["text_inv"],
                 font=FONT_LG).pack(expand=True)
        _divider(win).pack(fill=tk.X)

        # Body
        body = tk.Frame(win, bg=P["sidebar"])
        body.pack(fill=tk.BOTH, expand=True, padx=22, pady=(16, 0))

        for text, col, fnt, bot_pad in [
            ("Visualisierung von Frequenzgängen",          P["text_inv"], FONT,    2),
            ("aus gemessenen Übertragungsverhalten.",       P["text_inv"], FONT,    12),
            ("Eingabe:  Frequenz  ·  Amplitude  ·  Phase",  P["muted"],   FONT_SM, 3),
            ("Export:   CSV  ·  PNG  ·  PDF  ·  SVG",       P["muted"],   FONT_SM, 12),
        ]:
            tk.Label(body, text=text, bg=P["sidebar"], fg=col,
                     font=fnt, anchor="w").pack(anchor="w", pady=(0, bot_pad))

        gh_url = "github.com/FelixLenz-Code/bode-diagramm-tool"
        gh_lbl = tk.Label(body, text=f">> {gh_url}",
                          bg=P["sidebar"], fg=P["accent"],
                          font=FONT_SM, anchor="w", cursor="hand2")
        gh_lbl.pack(anchor="w")
        gh_lbl.bind("<Button-1>", lambda _: self._open_url(
            "https://github.com/FelixLenz-Code/bode-diagramm-tool"))

        _divider(win).pack(fill=tk.X)
        foot = tk.Frame(win, bg=P["sidebar"])
        foot.pack(fill=tk.X, padx=22, pady=(10, 16))
        _btn(foot, "Schließen", win.destroy,
             P["accent"], padx=14).pack(side=tk.RIGHT, ipady=5)

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    _app_icon = Path(__file__).parent / "icons" / "icon.png"
    if _app_icon.exists():
        _img = tk.PhotoImage(file=str(_app_icon))
        root.iconphoto(True, _img)
    BodeTool(root)
    root.mainloop()
