# ============================================================
# gui.py  — Ultra Premium Black Edition
# Aesthetic: Luxury Minimal — pure black, warm whites,
#            gold accents, Apple/Vercel inspired
# Made by Vansh
# ============================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from PIL import Image, ImageTk

from attendance_manager      import AttendanceManager
from student_registration    import StudentRegistration
from face_recognition_engine import FaceRecognitionEngine
from statistics              import AttendanceStatistics

# ── Pure Black Luxury Palette ───────────────────────────────
BG_TRUE_BLACK = "#000000"   # Pure black
BG_900        = "#0a0a0a"   # Near black
BG_800        = "#111111"   # Elevated surface
BG_700        = "#1a1a1a"   # Card
BG_600        = "#222222"   # Hover state
BG_500        = "#2a2a2a"   # Border light

GOLD          = "#c9a84c"   # Warm gold accent
GOLD_LIGHT    = "#e8c87a"   # Light gold
GOLD_DIM      = "#7a6230"   # Muted gold

WHITE         = "#ffffff"   # Pure white
GRAY_100      = "#f5f5f5"   # Near white
GRAY_300      = "#d4d4d4"   # Light text
GRAY_500      = "#737373"   # Muted text
GRAY_700      = "#404040"   # Very muted
GRAY_800      = "#2d2d2d"   # Border

GREEN_SOFT    = "#4ade80"   # Soft green
RED_SOFT      = "#f87171"   # Soft red
AMBER         = "#fbbf24"   # Amber

# ── Typography ──────────────────────────────────────────────
F_HERO    = ("Georgia", 24, "bold")
F_TITLE   = ("Georgia", 15, "bold")
F_SUB     = ("Georgia", 11)
F_BODY    = ("Helvetica Neue", 11)
F_SMALL   = ("Helvetica Neue", 9)
F_MONO    = ("Courier New", 9)
F_NUM     = ("Georgia", 38, "bold")
F_LABEL   = ("Helvetica Neue", 8, "bold")
F_BTN     = ("Helvetica Neue", 10, "bold")


# ── Thin separator ───────────────────────────────────────────
def thin_line(parent, color=GRAY_800, height=1, padx=0):
    tk.Frame(parent, bg=color, height=height).pack(
        fill="x", padx=padx)


# ── Premium button ───────────────────────────────────────────
def premium_btn(parent, text, command,
                bg=BG_700, fg=GRAY_300,
                hover_bg=BG_600, hover_fg=WHITE,
                pady=12, font=F_BTN, width=None):
    btn = tk.Button(
        parent, text=text, command=command,
        font=font, bg=bg, fg=fg,
        activebackground=hover_bg,
        activeforeground=hover_fg,
        relief="flat", cursor="hand2",
        padx=20, pady=pady, bd=0,
        width=width
    )
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg, fg=hover_fg))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg, fg=fg))
    return btn


# ── Gold accent button ───────────────────────────────────────
def gold_btn(parent, text, command, pady=12, font=F_BTN):
    return premium_btn(parent, text, command,
                       bg=GOLD, fg=BG_TRUE_BLACK,
                       hover_bg=GOLD_LIGHT, hover_fg=BG_TRUE_BLACK,
                       pady=pady, font=font)


# ============================================================
# MainDashboard
# ============================================================

class MainDashboard:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AttendAI")
        self.root.geometry("960x640")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_TRUE_BLACK)

        self.att_manager  = AttendanceManager()
        self.stu_reg      = StudentRegistration()
        self.stats_engine = AttendanceStatistics(
            self.att_manager, self.stu_reg)
        self.engine       = FaceRecognitionEngine(self.att_manager)

        self.status_var    = tk.StringVar(value="Ready.")
        self.webcam_thread = None

        self._build_ui()
        self.refresh_stats()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ────────────────────────────────────────────────────────
    def _build_ui(self):
        # Left sidebar  220px
        self.sidebar = tk.Frame(
            self.root, bg=BG_900, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Right content  740px
        self.content = tk.Frame(
            self.root, bg=BG_TRUE_BLACK)
        self.content.pack(side="left", fill="both", expand=True)

        # 1px border between sidebar and content
        tk.Frame(self.root, bg=GRAY_800, width=1).place(
            x=220, y=0, height=640)

        self._build_sidebar()
        self._build_content()

    # ── SIDEBAR ─────────────────────────────────────────────
    def _build_sidebar(self):
        s = self.sidebar

        # Gold top line
        tk.Frame(s, bg=GOLD, height=2).pack(fill="x")

        # Brand
        brand = tk.Frame(s, bg=BG_900)
        brand.pack(fill="x", padx=24, pady=(28, 24))

        tk.Label(brand, text="AttendAI",
                 font=("Georgia", 20, "bold"),
                 bg=BG_900, fg=WHITE).pack(anchor="w")

        tk.Label(brand, text="Attendance Management",
                 font=("Helvetica Neue", 8),
                 bg=BG_900, fg=GRAY_500).pack(anchor="w", pady=(2, 0))

        thin_line(s, GRAY_800)

        # Nav section label
        tk.Label(s, text="MENU",
                 font=("Helvetica Neue", 7, "bold"),
                 bg=BG_900, fg=GRAY_700
                 ).pack(anchor="w", padx=24, pady=(20, 8))

        # Nav items
        nav = [
            ("Start Attendance",  "▶",  self._start_attendance),
            ("Register Student",  "+",  self._open_registration),
            ("View Attendance",   "≡",  self._open_viewer),
            ("Statistics",        "◈",  self._open_statistics),
            ("Refresh",           "↺",  self.refresh_stats),
        ]
        for label, icon, cmd in nav:
            self._nav_item(s, icon, label, cmd)

        # Spacer — pushes footer down
        spacer = tk.Frame(s, bg=BG_900)
        spacer.pack(fill="both", expand=True)

        # Footer
        thin_line(s, GRAY_800)

        # Exit button
        premium_btn(s, "Exit", self._on_close,
                    bg=BG_900, fg=GRAY_500,
                    hover_bg=BG_800, hover_fg=RED_SOFT,
                    pady=14, font=("Helvetica Neue", 9)
                    ).pack(fill="x")

        thin_line(s, GRAY_800)

        # Made by
        tk.Label(s, text="Made by Vansh",
                 font=("Georgia", 8, "italic"),
                 bg=BG_900, fg=GOLD_DIM
                 ).pack(pady=10)

    def _nav_item(self, parent, icon, label, command):
        row = tk.Frame(parent, bg=BG_900, cursor="hand2")
        row.pack(fill="x")

        left_bar = tk.Frame(row, bg=BG_900, width=3)
        left_bar.pack(side="left", fill="y")

        icon_lbl = tk.Label(row, text=icon,
                            font=("Helvetica Neue", 11),
                            bg=BG_900, fg=GRAY_500,
                            width=3, cursor="hand2")
        icon_lbl.pack(side="left", pady=13)

        text_lbl = tk.Label(row, text=label,
                            font=("Helvetica Neue", 10),
                            bg=BG_900, fg=GRAY_500,
                            anchor="w", cursor="hand2")
        text_lbl.pack(side="left", fill="x", expand=True)

        def on_enter(e):
            row.configure(bg=BG_800)
            left_bar.configure(bg=GOLD)
            icon_lbl.configure(bg=BG_800, fg=GOLD)
            text_lbl.configure(bg=BG_800, fg=WHITE)

        def on_leave(e):
            row.configure(bg=BG_900)
            left_bar.configure(bg=BG_900)
            icon_lbl.configure(bg=BG_900, fg=GRAY_500)
            text_lbl.configure(bg=BG_900, fg=GRAY_500)

        def on_click(e):
            command()

        for w in (row, left_bar, icon_lbl, text_lbl):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        thin_line(parent, BG_800)

    # ── CONTENT ─────────────────────────────────────────────
    def _build_content(self):
        c = self.content

        # Top header bar
        self._build_header(c)

        # Stat cards row
        self._build_cards(c)

        # Divider with label
        div = tk.Frame(c, bg=BG_TRUE_BLACK)
        div.pack(fill="x", padx=32, pady=(20, 10))
        tk.Label(div, text="RECENT ATTENDANCE",
                 font=("Helvetica Neue", 7, "bold"),
                 bg=BG_TRUE_BLACK, fg=GRAY_700
                 ).pack(anchor="w")
        thin_line(div, GRAY_800)

        # Activity table
        self._build_activity(c)

        # Status bar
        self._build_statusbar(c)

    def _build_header(self, parent):
        h = tk.Frame(parent, bg=BG_TRUE_BLACK, height=68)
        h.pack(fill="x")
        h.pack_propagate(False)

        # Left: page title
        tk.Label(h, text="Dashboard",
                 font=F_HERO,
                 bg=BG_TRUE_BLACK, fg=WHITE
                 ).pack(side="left", padx=32, pady=16)

        # Right: date + live dot
        right = tk.Frame(h, bg=BG_TRUE_BLACK)
        right.pack(side="right", padx=28, pady=16)

        from datetime import datetime
        tk.Label(right,
                 text=datetime.now().strftime("%d %B %Y"),
                 font=F_MONO, bg=BG_TRUE_BLACK,
                 fg=GRAY_500).pack(anchor="e")

        self.live_dot = tk.Label(right, text="● LIVE",
                                 font=("Courier New", 8),
                                 bg=BG_TRUE_BLACK, fg=GREEN_SOFT)
        self.live_dot.pack(anchor="e", pady=(3, 0))
        self._blink()

        thin_line(parent, GRAY_800)

    def _blink(self):
        fg = self.live_dot.cget("fg")
        self.live_dot.configure(
            fg=GREEN_SOFT if fg == BG_TRUE_BLACK else BG_TRUE_BLACK)
        self.root.after(900, self._blink)

    def _build_cards(self, parent):
        frame = tk.Frame(parent, bg=BG_TRUE_BLACK)
        frame.pack(fill="x", padx=28, pady=(24, 4))

        self.var_total   = tk.StringVar(value="—")
        self.var_present = tk.StringVar(value="—")
        self.var_absent  = tk.StringVar(value="—")
        self.var_pct     = tk.StringVar(value="—")

        cards = [
            ("Total Students",  self.var_total,   WHITE,      ""),
            ("Present Today",   self.var_present,  GREEN_SOFT, ""),
            ("Absent Today",    self.var_absent,   RED_SOFT,   ""),
            ("Attendance Rate", self.var_pct,      GOLD,       ""),
        ]
        for label, var, color, _ in cards:
            self._stat_card(frame, label, var, color)

    def _stat_card(self, parent, label, var, color):
        # Outer border frame — 1px gold on top
        card = tk.Frame(parent, bg=BG_800)
        card.pack(side="left", fill="both",
                  expand=True, padx=5, pady=0)

        # Top colored line
        tk.Frame(card, bg=color, height=1).pack(fill="x")

        inner = tk.Frame(card, bg=BG_800, padx=18, pady=18)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, textvariable=var,
                 font=F_NUM, bg=BG_800,
                 fg=color).pack(anchor="w")

        tk.Label(inner, text=label,
                 font=("Helvetica Neue", 9),
                 bg=BG_800, fg=GRAY_500).pack(anchor="w", pady=(4, 0))

    def _build_activity(self, parent):
        outer = tk.Frame(parent, bg=BG_TRUE_BLACK)
        outer.pack(fill="both", expand=True, padx=28)

        # Column headers
        hdr = tk.Frame(outer, bg=BG_800)
        hdr.pack(fill="x")

        for col, w, anchor in [
            ("STUDENT NAME", 35, "w"),
            ("DATE",         16, "center"),
            ("TIME",         14, "center"),
        ]:
            tk.Label(hdr, text=col,
                     font=("Courier New", 8, "bold"),
                     bg=BG_800, fg=GRAY_700,
                     width=w, anchor=anchor,
                     padx=16, pady=8
                     ).pack(side="left")

        # Rows frame
        self.rows_frame = tk.Frame(outer, bg=BG_TRUE_BLACK)
        self.rows_frame.pack(fill="both", expand=True)
        self._refresh_rows()

    def _refresh_rows(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()

        df = self.att_manager.get_all_records()

        if df.empty:
            tk.Label(self.rows_frame,
                     text="\n  No records yet.\n  Register a student and start attendance.",
                     font=("Helvetica Neue", 10),
                     bg=BG_TRUE_BLACK, fg=GRAY_700,
                     justify="left"
                     ).pack(anchor="w", padx=16, pady=24)
            return

        recent = df.tail(7).iloc[::-1]
        for i, (_, row) in enumerate(recent.iterrows()):
            bg = BG_TRUE_BLACK if i % 2 == 0 else BG_900
            r  = tk.Frame(self.rows_frame, bg=bg)
            r.pack(fill="x")

            # Gold dot indicator
            tk.Label(r, text="◆",
                     font=("Helvetica Neue", 6),
                     bg=bg, fg=GOLD_DIM,
                     padx=8).pack(side="left", pady=12)

            tk.Label(r, text=row["Name"],
                     font=("Helvetica Neue", 10),
                     bg=bg, fg=GRAY_300,
                     width=32, anchor="w"
                     ).pack(side="left", pady=12)

            tk.Label(r, text=row["Date"],
                     font=("Courier New", 9),
                     bg=bg, fg=GRAY_500,
                     width=16, anchor="center"
                     ).pack(side="left")

            tk.Label(r, text=row["Time"],
                     font=("Courier New", 9),
                     bg=bg, fg=GOLD_DIM,
                     width=14, anchor="center"
                     ).pack(side="left")

            thin_line(r, BG_600)

    def _build_statusbar(self, parent):
        bar = tk.Frame(parent, bg=BG_900, height=30)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        thin_line(bar, GRAY_800)

        tk.Label(bar, text="◆",
                 font=("Helvetica Neue", 7),
                 bg=BG_900, fg=GOLD_DIM
                 ).pack(side="left", padx=(14, 4), pady=8)

        tk.Label(bar, textvariable=self.status_var,
                 font=("Courier New", 8),
                 bg=BG_900, fg=GRAY_500,
                 anchor="w").pack(side="left")

        tk.Label(bar, text="Made by Vansh  ",
                 font=("Georgia", 8, "italic"),
                 bg=BG_900, fg=GOLD_DIM
                 ).pack(side="right")

    # ── Stats ────────────────────────────────────────────────
    def refresh_stats(self):
        try:
            data  = self.stats_engine.get_dashboard_data()
            today = data["today"]
            self.var_total.set(str(today["total_registered"]))
            self.var_present.set(str(today["present_today"]))
            self.var_absent.set(str(today["absent_today"]))
            self.var_pct.set(f"{today['attendance_pct']}%")
            self._refresh_rows()
            self.status_var.set(
                f"Updated — {today['present_today']} present, "
                f"{today['absent_today']} absent today.")
        except Exception as e:
            self.status_var.set(f"Error: {e}")

    # ── Actions ──────────────────────────────────────────────
    def _start_attendance(self):
        if self.webcam_thread and self.webcam_thread.is_alive():
            messagebox.showwarning("Running",
                "Attendance is already running!\nClose the webcam window first.")
            return
        if not self.stu_reg.get_all_students():
            messagebox.showwarning("No Students",
                "No students registered.\nPlease register first.")
            return
        self.engine.refresh_known_faces()

        def run():
            self.status_var.set("Webcam active — recognising faces...")
            self.engine.start(
                camera_index=0,
                status_callback=lambda m: self.status_var.set(m))
            self.refresh_stats()
            self.status_var.set("Webcam stopped.")

        self.webcam_thread = threading.Thread(target=run, daemon=True)
        self.webcam_thread.start()
        self.status_var.set("Starting webcam... press Q to stop.")

    def _open_registration(self):
        StudentRegistrar(self.root, self.stu_reg,
                         self.engine, self.refresh_stats)

    def _open_viewer(self):
        AttendanceViewer(self.root, self.att_manager)

    def _open_statistics(self):
        StatisticsViewer(self.root, self.stats_engine)

    def _on_close(self):
        self.engine.stop()
        self.root.destroy()


# ============================================================
# StudentRegistrar
# ============================================================

class StudentRegistrar(tk.Toplevel):

    def __init__(self, parent, stu_reg, engine, refresh_callback):
        super().__init__(parent)
        self.stu_reg          = stu_reg
        self.engine           = engine
        self.refresh_callback = refresh_callback
        self.selected_image   = None

        self.title("Register Student")
        self.geometry("460x540")
        self.resizable(False, False)
        self.configure(bg=BG_TRUE_BLACK)
        self.withdraw()
        self.grab_set()
        self._build_ui()
        self.deiconify()

    def _build_ui(self):
        tk.Frame(self, bg=GOLD, height=1).pack(fill="x")

        # Header
        h = tk.Frame(self, bg=BG_900)
        h.pack(fill="x")
        tk.Label(h, text="Register Student",
                 font=F_HERO, bg=BG_900,
                 fg=WHITE).pack(anchor="w", padx=28, pady=(22, 2))
        tk.Label(h, text="Add a new student to the system",
                 font=("Helvetica Neue", 9),
                 bg=BG_900, fg=GRAY_500
                 ).pack(anchor="w", padx=28, pady=(0, 18))
        thin_line(self, GRAY_800)

        form = tk.Frame(self, bg=BG_TRUE_BLACK)
        form.pack(fill="both", expand=True, padx=28, pady=20)

        # Name field
        tk.Label(form, text="FULL NAME",
                 font=("Courier New", 8, "bold"),
                 bg=BG_TRUE_BLACK, fg=GRAY_700
                 ).pack(anchor="w", pady=(0, 6))

        entry_wrap = tk.Frame(form, bg=GRAY_800, padx=1, pady=1)
        entry_wrap.pack(fill="x", pady=(0, 22))
        entry_bg = tk.Frame(entry_wrap, bg=BG_800)
        entry_bg.pack(fill="x")

        self.name_var = tk.StringVar()
        name_entry = tk.Entry(
            entry_bg, textvariable=self.name_var,
            font=("Helvetica Neue", 12),
            bg=BG_800, fg=WHITE,
            insertbackground=GOLD,
            relief="flat")
        name_entry.pack(fill="x", padx=14, pady=12)
        name_entry.focus_set()

        # Focus border effect
        def on_focus_in(e):
            entry_wrap.configure(bg=GOLD)
        def on_focus_out(e):
            entry_wrap.configure(bg=GRAY_800)
        name_entry.bind("<FocusIn>",  on_focus_in)
        name_entry.bind("<FocusOut>", on_focus_out)

        # Photo section
        tk.Label(form, text="PHOTO",
                 font=("Courier New", 8, "bold"),
                 bg=BG_TRUE_BLACK, fg=GRAY_700
                 ).pack(anchor="w", pady=(0, 6))

        preview_wrap = tk.Frame(form, bg=GRAY_800, padx=1, pady=1)
        preview_wrap.pack(fill="x", pady=(0, 18))

        self.preview_label = tk.Label(
            preview_wrap,
            text="No photo selected",
            font=("Helvetica Neue", 10),
            bg=BG_800, fg=GRAY_700,
            height=7, justify="center")
        self.preview_label.pack(fill="x")

        # Buttons
        btn_row = tk.Frame(form, bg=BG_TRUE_BLACK)
        btn_row.pack(fill="x", pady=(0, 14))

        premium_btn(btn_row, "Browse Photo",
                    self._browse,
                    bg=BG_700, fg=GRAY_300,
                    hover_bg=BG_600, hover_fg=WHITE,
                    pady=11
                    ).pack(side="left", fill="x",
                           expand=True, padx=(0, 6))

        gold_btn(btn_row, "Register",
                 lambda: self._do_register(),
                 pady=11
                 ).pack(side="left", fill="x",
                        expand=True, padx=(6, 0))

        self.msg_var = tk.StringVar(value="")
        tk.Label(form, textvariable=self.msg_var,
                 font=("Courier New", 9),
                 bg=BG_TRUE_BLACK, fg=GREEN_SOFT,
                 wraplength=400).pack(pady=4)

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"),
                       ("All", "*.*")])
        if not path:
            return
        self.selected_image = path
        try:
            img = Image.open(path)
            img.thumbnail((340, 160))
            self.preview_photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(
                image=self.preview_photo, text="")
        except Exception as e:
            self.msg_var.set(f"Preview error: {e}")

    def _do_register(self):
        name = self.name_var.get().strip()
        if not name:
            self.msg_var.set("Enter a student name.")
            return
        if not self.selected_image:
            self.msg_var.set("Select a photo first.")
            return
        self.msg_var.set("Registering...")
        self.update()
        success, message = self.stu_reg.register_student(
            name, self.selected_image)
        if success:
            self.msg_var.set(f"✓  {name} registered successfully.")
            self.engine.refresh_known_faces()
            self.refresh_callback()
            self.after(1800, self.destroy)
        else:
            self.msg_var.set(f"✗  {message}")


# ============================================================
# AttendanceViewer
# ============================================================

class AttendanceViewer(tk.Toplevel):

    def __init__(self, parent, att_manager):
        super().__init__(parent)
        self.att_manager = att_manager
        self.title("Attendance Records")
        self.geometry("720x560")
        self.resizable(True, True)
        self.configure(bg=BG_TRUE_BLACK)
        self.withdraw()
        self.grab_set()
        self._build_ui()
        self._load_records()
        self.deiconify()

    def _build_ui(self):
        tk.Frame(self, bg=GOLD, height=1).pack(fill="x")

        h = tk.Frame(self, bg=BG_900)
        h.pack(fill="x")
        tk.Label(h, text="Attendance Records",
                 font=F_HERO, bg=BG_900,
                 fg=WHITE).pack(side="left", padx=28, pady=16)
        thin_line(self, GRAY_800)

        # Search
        sf = tk.Frame(self, bg=BG_TRUE_BLACK)
        sf.pack(fill="x", padx=24, pady=14)

        for attr, placeholder, w in [
            ("search_name", "Search by name...", 22),
            ("search_date", "YYYY-MM-DD", 14),
        ]:
            var = tk.StringVar()
            setattr(self, attr, var)
            wrap = tk.Frame(sf, bg=GRAY_800, padx=1, pady=1)
            wrap.pack(side="left", padx=(0, 10))
            tk.Entry(wrap, textvariable=var,
                     font=F_BODY, bg=BG_800, fg=GRAY_300,
                     insertbackground=GOLD,
                     relief="flat", width=w
                     ).pack(padx=10, pady=7)

        premium_btn(sf, "Search", self._search,
                    bg=BG_700, hover_bg=BG_600,
                    fg=GRAY_300, hover_fg=WHITE,
                    pady=8, font=F_BTN
                    ).pack(side="left", padx=(0, 6))

        premium_btn(sf, "Clear", self._clear,
                    bg=BG_TRUE_BLACK, hover_bg=BG_800,
                    fg=GRAY_500, hover_fg=GRAY_300,
                    pady=8, font=F_BTN
                    ).pack(side="left")

        # Table
        tf = tk.Frame(self, bg=GRAY_800, padx=1, pady=1)
        tf.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        inner = tk.Frame(tf, bg=BG_TRUE_BLACK)
        inner.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("B.Treeview",
                         background=BG_TRUE_BLACK,
                         foreground=GRAY_300,
                         rowheight=34,
                         fieldbackground=BG_TRUE_BLACK,
                         borderwidth=0,
                         font=("Helvetica Neue", 10))
        style.configure("B.Treeview.Heading",
                         background=BG_900,
                         foreground=GRAY_700,
                         relief="flat",
                         font=("Courier New", 8, "bold"))
        style.map("B.Treeview",
                  background=[("selected", BG_700)])

        self.tree = ttk.Treeview(
            inner,
            columns=("Name","Date","Time"),
            show="headings",
            style="B.Treeview")
        self.tree.heading("Name", text="STUDENT NAME")
        self.tree.heading("Date", text="DATE")
        self.tree.heading("Time", text="TIME")
        self.tree.column("Name", width=300, anchor="w")
        self.tree.column("Date", width=150, anchor="center")
        self.tree.column("Time", width=150, anchor="center")

        sb = ttk.Scrollbar(inner, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.count_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.count_var,
                 font=("Courier New", 8),
                 bg=BG_TRUE_BLACK, fg=GRAY_700
                 ).pack(pady=(0, 10))

    def _load_records(self, df=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if df is None:
            df = self.att_manager.get_all_records()
        if df.empty:
            self.count_var.set("No records found.")
            return
        for i, (_, row) in enumerate(df.iterrows()):
            self.tree.insert("", "end",
                             values=(row["Name"], row["Date"], row["Time"]),
                             tags=("even" if i%2==0 else "odd",))
        self.tree.tag_configure("even", background=BG_TRUE_BLACK)
        self.tree.tag_configure("odd",  background=BG_900)
        self.count_var.set(f"  {len(df)} records")

    def _search(self):
        name = self.search_name.get().strip()
        date = self.search_date.get().strip()
        df   = self.att_manager.get_all_records()
        if df.empty:
            self._load_records(df)
            return
        if name:
            df = df[df["Name"].str.contains(name, case=False, na=False)]
        if date:
            df = df[df["Date"] == date]
        self._load_records(df)

    def _clear(self):
        self.search_name.set("")
        self.search_date.set("")
        self._load_records()


# ============================================================
# StatisticsViewer
# ============================================================

class StatisticsViewer(tk.Toplevel):

    def __init__(self, parent, stats_engine):
        super().__init__(parent)
        self.stats_engine = stats_engine
        self.title("Statistics")
        self.geometry("720x580")
        self.resizable(True, True)
        self.configure(bg=BG_TRUE_BLACK)
        self.withdraw()
        self.grab_set()
        self._build_ui()
        self.deiconify()

    def _build_ui(self):
        tk.Frame(self, bg=GOLD, height=1).pack(fill="x")

        h = tk.Frame(self, bg=BG_900)
        h.pack(fill="x")
        tk.Label(h, text="Statistics",
                 font=F_HERO, bg=BG_900,
                 fg=WHITE).pack(side="left", padx=28, pady=16)
        thin_line(self, GRAY_800)

        # Summary row
        summary = self.stats_engine.get_today_summary()
        strip   = tk.Frame(self, bg=BG_TRUE_BLACK)
        strip.pack(fill="x", padx=24, pady=20)

        for label, value, color in [
            ("Registered",  summary["total_registered"], WHITE),
            ("Present",     summary["present_today"],    GREEN_SOFT),
            ("Absent",      summary["absent_today"],     RED_SOFT),
            ("Rate",        f"{summary['attendance_pct']}%", GOLD),
        ]:
            f = tk.Frame(strip, bg=BG_800)
            f.pack(side="left", fill="both",
                   expand=True, padx=5)
            tk.Frame(f, bg=color, height=1).pack(fill="x")
            tk.Label(f, text=str(value),
                     font=("Georgia", 24, "bold"),
                     bg=BG_800, fg=color
                     ).pack(pady=(14, 2))
            tk.Label(f, text=label.upper(),
                     font=("Courier New", 7, "bold"),
                     bg=BG_800, fg=GRAY_700
                     ).pack(pady=(0, 14))

        tk.Label(self, text="PER STUDENT",
                 font=("Courier New", 7, "bold"),
                 bg=BG_TRUE_BLACK, fg=GRAY_700
                 ).pack(anchor="w", padx=26, pady=(4, 6))

        tf = tk.Frame(self, bg=GRAY_800, padx=1, pady=1)
        tf.pack(fill="both", expand=True, padx=24, pady=(0, 14))
        inner = tk.Frame(tf, bg=BG_TRUE_BLACK)
        inner.pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure("St.Treeview",
                         background=BG_TRUE_BLACK,
                         foreground=GRAY_300,
                         rowheight=34,
                         fieldbackground=BG_TRUE_BLACK,
                         borderwidth=0,
                         font=("Helvetica Neue", 10))
        style.configure("St.Treeview.Heading",
                         background=BG_900,
                         foreground=GRAY_700,
                         relief="flat",
                         font=("Courier New", 8, "bold"))
        style.map("St.Treeview",
                  background=[("selected", BG_700)])

        cols = ("Name","Present","Total","Pct","Status")
        self.tree = ttk.Treeview(inner, columns=cols,
                                  show="headings", style="St.Treeview")
        for col, hdr, w in zip(
            cols,
            ["NAME","PRESENT","TOTAL","RATE","STATUS"],
            [240, 90, 80, 90, 110]
        ):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w, anchor="center")
        self.tree.column("Name", anchor="w")

        sb = ttk.Scrollbar(inner, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        color_map = {
            "Excellent": GREEN_SOFT,
            "Good":      GOLD,
            "Average":   AMBER,
            "Poor":      "#f97316",
            "Critical":  RED_SOFT,
        }

        for s in self.stats_engine.get_student_statistics():
            self.tree.insert("", "end",
                             values=(s["name"], s["days_present"],
                                     s["total_days"],
                                     f"{s['percentage']}%",
                                     s["status"]),
                             tags=(s["status"],))

        for status, color in color_map.items():
            self.tree.tag_configure(status, foreground=color)