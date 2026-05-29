# =============================================
#  chat_widgets.py — UI Components for the Chat
# =============================================
#  Contains all tkinter widget construction:
#    - ChatHeader, ChatArea, InputBar, DebugPanel
#    - Message bubble rendering
#    - Scroll / placeholder event handlers

import tkinter as tk
from tkinter import scrolledtext

from .theme import (
    BG_DARK, BG_HEADER, BG_INPUT_FIELD,
    BG_SENT, BG_RECEIVED, FG_PRIMARY, FG_SECONDARY, FG_INPUT,
    ACCENT_GREEN, BG_DEBUG_PANEL, FG_DEBUG, BG_DATE_SEP, FG_CHECK,
    BG_DEBUG_CONSOLE,
)


class ChatHeader:
    """Top header bar with avatar, chat name, and action buttons."""

    def __init__(self, parent, on_toggle_debugger):
        self.frame = tk.Frame(parent, bg=BG_HEADER, height=56)
        self.frame.pack(fill=tk.X)
        self.frame.pack_propagate(False)

        # Avatar circle
        avatar = tk.Canvas(self.frame, width=40, height=40,
                           bg=BG_HEADER, highlightthickness=0)
        avatar.pack(side=tk.LEFT, padx=(12, 8), pady=8)
        avatar.create_oval(2, 2, 38, 38, fill=ACCENT_GREEN, outline="")
        avatar.create_text(20, 20, text="👤", font=("Segoe UI Emoji", 14))

        # Chat name and status
        name_frame = tk.Frame(self.frame, bg=BG_HEADER)
        name_frame.pack(side=tk.LEFT, fill=tk.Y, pady=8)
        tk.Label(name_frame, text="Secure Chat Room",
                 font=("Segoe UI", 11, "bold"),
                 fg=FG_PRIMARY, bg=BG_HEADER).pack(anchor="w")
        tk.Label(name_frame, text="end-to-end encrypted",
                 font=("Segoe UI", 9),
                 fg=FG_SECONDARY, bg=BG_HEADER).pack(anchor="w")

        # Right-side buttons
        btns = tk.Frame(self.frame, bg=BG_HEADER)
        btns.pack(side=tk.RIGHT, padx=8)

        self.debug_toggle_btn = tk.Button(
            btns, text="🔒 Debugger",
            font=("Segoe UI", 9), fg=ACCENT_GREEN, bg=BG_HEADER,
            activebackground=BG_HEADER, activeforeground=FG_PRIMARY,
            bd=0, cursor="hand2", command=on_toggle_debugger,
        )
        self.debug_toggle_btn.pack(side=tk.RIGHT, padx=4)

        tk.Label(btns, text="🔍", font=("Segoe UI Emoji", 16),
                 fg=FG_SECONDARY, bg=BG_HEADER,
                 cursor="hand2").pack(side=tk.RIGHT, padx=8)
        tk.Label(btns, text="⋮", font=("Segoe UI", 18),
                 fg=FG_SECONDARY, bg=BG_HEADER,
                 cursor="hand2").pack(side=tk.RIGHT, padx=4)

    # ---- helpers used by the app to update the toggle label ----
    def set_debugger_on(self):
        self.debug_toggle_btn.config(text="🔒 Debugger", fg=ACCENT_GREEN)

    def set_debugger_off(self):
        self.debug_toggle_btn.config(text="🔓 Debugger", fg=FG_SECONDARY)


class ChatArea:
    """Scrollable message area with WhatsApp-style bubbles."""

    def __init__(self, parent):
        self._area = tk.Frame(parent, bg=BG_DARK)
        self._area.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self._area, bg=BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(self._area, orient=tk.VERTICAL,
                                 command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.messages_frame = tk.Frame(self.canvas, bg=BG_DARK)
        self._win_id = self.canvas.create_window(
            (0, 0), window=self.messages_frame, anchor="nw"
        )

        self.messages_frame.bind("<Configure>", self._on_frame_cfg)
        self.canvas.bind("<Configure>", self._on_canvas_cfg)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Initial "Today" separator
        self.add_date_separator("Today")

    # ---- public API ----

    def add_date_separator(self, text):
        """Centered date pill (e.g. 'Today', 'Yesterday')."""
        sep = tk.Frame(self.messages_frame, bg=BG_DARK)
        sep.pack(fill=tk.X, pady=8)
        tk.Label(sep, text=text, font=("Segoe UI", 9),
                 fg=FG_SECONDARY, bg=BG_DATE_SEP,
                 padx=12, pady=3).pack()

    def add_bubble(self, message, time_str, is_sent=True):
        """Render a single chat bubble."""
        bubble_bg = BG_SENT if is_sent else BG_RECEIVED
        pad = (80, 12) if is_sent else (12, 80)

        wrapper = tk.Frame(self.messages_frame, bg=BG_DARK)
        wrapper.pack(fill=tk.X, padx=pad, pady=2)

        bubble = tk.Frame(wrapper, bg=bubble_bg, padx=10, pady=6)
        bubble.pack(side=tk.RIGHT if is_sent else tk.LEFT)

        tk.Label(bubble, text=message, font=("Segoe UI", 11),
                 fg=FG_PRIMARY, bg=bubble_bg, wraplength=280,
                 justify=tk.LEFT, anchor="w").pack(anchor="w")

        ts = tk.Frame(bubble, bg=bubble_bg)
        ts.pack(anchor="e")
        tk.Label(ts, text=time_str, font=("Segoe UI", 8),
                 fg=FG_SECONDARY, bg=bubble_bg).pack(side=tk.LEFT, padx=(0, 4))
        if is_sent:
            tk.Label(ts, text="✓✓", font=("Segoe UI", 8),
                     fg=FG_CHECK, bg=bubble_bg).pack(side=tk.LEFT)

        self._scroll_to_bottom()

    # ---- internal helpers ----

    def _scroll_to_bottom(self):
        self.messages_frame.update_idletasks()
        self._update_scroll_region()
        self.canvas.yview_moveto(1.0)

    def _update_scroll_region(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_frame_cfg(self, _event):
        self._update_scroll_region()

    def _on_canvas_cfg(self, event):
        self.canvas.itemconfig(self._win_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class InputBar:
    """Bottom bar with emoji, attachment, text entry, and mic."""

    PLACEHOLDER = "Type a message"

    def __init__(self, parent, on_send):
        self.frame = tk.Frame(parent, bg=BG_HEADER, height=56)
        self.frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.frame.pack_propagate(False)

        # Emoji
        tk.Label(self.frame, text="😊", font=("Segoe UI Emoji", 16),
                 fg=FG_SECONDARY, bg=BG_HEADER,
                 cursor="hand2").pack(side=tk.LEFT, padx=(12, 6), pady=10)

        # Attachment
        tk.Label(self.frame, text="📎", font=("Segoe UI Emoji", 16),
                 fg=FG_SECONDARY, bg=BG_HEADER,
                 cursor="hand2").pack(side=tk.LEFT, padx=(0, 8), pady=10)

        # Text entry
        self.entry = tk.Entry(
            self.frame, font=("Segoe UI", 11),
            bg=BG_INPUT_FIELD, fg=FG_INPUT,
            insertbackground=FG_INPUT, relief=tk.FLAT, bd=0,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                        pady=10, ipady=6)
        self.entry.insert(0, self.PLACEHOLDER)
        self.entry.config(fg=FG_SECONDARY)
        self.entry.bind("<FocusIn>", self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)
        self.entry.bind("<Return>", lambda _: on_send())

        # Mic
        tk.Label(self.frame, text="🎙", font=("Segoe UI Emoji", 16),
                 fg=FG_SECONDARY, bg=BG_HEADER,
                 cursor="hand2").pack(side=tk.RIGHT, padx=(8, 12), pady=10)

    # ---- public API ----

    def get_text(self):
        """Return the current text, or '' if it's just the placeholder."""
        txt = self.entry.get()
        return "" if txt == self.PLACEHOLDER else txt

    def clear(self):
        self.entry.delete(0, tk.END)

    # ---- placeholder behaviour ----

    def _focus_in(self, _event):
        if self.entry.get() == self.PLACEHOLDER:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=FG_INPUT)

    def _focus_out(self, _event):
        if not self.entry.get():
            self.entry.insert(0, self.PLACEHOLDER)
            self.entry.config(fg=FG_SECONDARY)


class DebugPanel:
    """Toggleable crypto-debugger side panel."""

    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=BG_DEBUG_PANEL, width=340)
        self.frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.frame.pack_propagate(False)

        # Header
        hdr = tk.Frame(self.frame, bg=BG_HEADER, height=56)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="🔐", font=("Segoe UI Emoji", 14),
                 bg=BG_HEADER).pack(side=tk.LEFT, padx=(12, 6), pady=8)
        tk.Label(hdr, text="Crypto Debugger",
                 font=("Segoe UI", 11, "bold"),
                 fg=FG_PRIMARY, bg=BG_HEADER).pack(side=tk.LEFT, pady=8)

        tk.Button(
            hdr, text="Clear", font=("Segoe UI", 9),
            fg=ACCENT_GREEN, bg=BG_HEADER,
            activebackground=BG_HEADER, activeforeground=FG_PRIMARY,
            bd=0, cursor="hand2", command=self.clear,
        ).pack(side=tk.RIGHT, padx=12, pady=8)

        # Console
        self.display = scrolledtext.ScrolledText(
            self.frame, wrap=tk.WORD,
            bg=BG_DEBUG_CONSOLE, fg=FG_DEBUG,
            font=("Consolas", 10),
            insertbackground=FG_DEBUG,
            relief=tk.FLAT, bd=0, padx=10, pady=10,
        )
        self.display.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

    # ---- public API ----

    def log(self, step, data=""):
        self.display.config(state="normal")
        self.display.insert(tk.END, f"[*] {step}\n")
        if data:
            self.display.insert(tk.END, f"    -> {data}\n")
        self.display.insert(tk.END, "-" * 40 + "\n")
        self.display.see(tk.END)
        self.display.config(state="disabled")

    def clear(self):
        self.display.config(state="normal")
        self.display.delete("1.0", tk.END)
        self.display.config(state="disabled")

    def show(self):
        self.frame.pack(side=tk.RIGHT, fill=tk.BOTH)

    def hide(self):
        self.frame.pack_forget()

    def is_visible(self):
        return self.frame.winfo_ismapped()
