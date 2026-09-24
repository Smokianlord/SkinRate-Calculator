"""
Modern dialogs and modal windows for SkinRate Calculator Pro:
Settings, History, Trade Slip Exporter, and About.
"""

from __future__ import annotations
import tkinter as tk
from typing import Callable, Optional, Dict, Any
from skinrate.theme import FONTS, shade
from skinrate.widgets import ModernButton
from skinrate.config import ConfigManager
from skinrate.engine import generate_trade_slip, TAKA


class BaseModal(tk.Toplevel):
    """Base modal window with consistent styling and positioning."""
    def __init__(self, parent, title: str, width: int = 500, height: int = 420, theme: dict = None):
        super().__init__(parent)
        self.theme = theme or {}
        self.title(title)
        self.configure(bg=self.theme.get("bg_app", "#0f131c"))
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        parent.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - width) // 2
        y = py + (ph - height) // 2
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        self.bind("<Escape>", lambda _e: self.destroy())


class SettingsDialog(BaseModal):
    """Settings and preferences dialog."""
    def __init__(self, parent, config: ConfigManager, theme: dict, on_save: Callable[[], None]):
        super().__init__(parent, "Settings & Preferences", width=480, height=400, theme=theme)
        self.config = config
        self.on_save = on_save
        self._build_ui()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0f131c")
        card_bg = self.theme.get("bg_card", "#181e2b")
        text_main = self.theme.get("text_main", "#f8fafc")
        input_bg = self.theme.get("bg_input", "#111622")

        container = tk.Frame(self, bg=bg, padx=22, pady=18)
        container.pack(fill="both", expand=True)

        header = tk.Label(
            container,
            text="⚙️ Preferences & Defaults",
            font=FONTS["title"],
            bg=bg,
            fg=text_main,
            anchor="w",
        )
        header.pack(fill="x", pady=(0, 14))

        card = tk.Frame(container, bg=card_bg, padx=16, pady=14, bd=1, relief="solid")
        card.pack(fill="x")
        card.grid_columnconfigure(1, weight=1)

        # Default Rate (৳/$)
        tk.Label(card, text="Default Rate (৳/$):", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=0, column=0, sticky="w", pady=8)
        self.rate_entry = tk.Entry(card, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid", width=12)
        self.rate_entry.grid(row=0, column=1, sticky="e", pady=8)
        self.rate_entry.insert(0, str(self.config.get("default_rate", 85.0)))

        # Custom Cashout Fee %
        tk.Label(card, text="Custom Cashout Fee (%):", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=1, column=0, sticky="w", pady=8)
        self.fee_entry = tk.Entry(card, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid", width=12)
        self.fee_entry.grid(row=1, column=1, sticky="e", pady=8)
        self.fee_entry.insert(0, str(self.config.get("custom_fee_pct", 1.85)))

        # Comma formatting
        tk.Label(card, text="Format Taka with Commas:", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=2, column=0, sticky="w", pady=8)
        self.comma_var = tk.BooleanVar(value=self.config.get("use_comma_bdt", False))
        tk.Checkbutton(card, variable=self.comma_var, bg=card_bg, activebackground=card_bg, selectcolor=input_bg).grid(row=2, column=1, sticky="e", pady=8)

        # Live calculation
        tk.Label(card, text="Live Instant Calculation:", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=3, column=0, sticky="w", pady=8)
        self.live_calc_var = tk.BooleanVar(value=self.config.get("live_calc", True))
        tk.Checkbutton(card, variable=self.live_calc_var, bg=card_bg, activebackground=card_bg, selectcolor=input_bg).grid(row=3, column=1, sticky="e", pady=8)

        # Action Buttons
        btn_bar = tk.Frame(container, bg=bg)
        btn_bar.pack(fill="x", pady=(18, 0))

        ModernButton(
            btn_bar,
            text="Cancel",
            command=self.destroy,
            width=100,
            height=34,
            bg_color=self.theme.get("btn_neutral_bg", "#222a3a"),
            text_color=self.theme.get("btn_neutral_fg", "#e2e8f0"),
            parent_bg=bg,
        ).pack(side="right", padx=(8, 0))

        ModernButton(
            btn_bar,
            text="Save Settings",
            command=self._save,
            width=130,
            height=34,
            bg_color="#2563eb",
            parent_bg=bg,
        ).pack(side="right")

    def _save(self):
        try:
            r = float(self.rate_entry.get().strip())
            fee_p = float(self.fee_entry.get().strip())
        except ValueError:
            return

        self.config.set("default_rate", r, auto_save=False)
        self.config.set("custom_fee_pct", fee_p, auto_save=False)
        self.config.set("use_comma_bdt", self.comma_var.get(), auto_save=False)
        self.config.set("live_calc", self.live_calc_var.get(), auto_save=True)

        if self.on_save:
            self.on_save()
        self.destroy()


class TradeSlipDialog(BaseModal):
    """Trade slip exporter modal for copying formatted quotes."""
    def __init__(self, parent, quote: Dict[str, Any], config: ConfigManager, theme: dict):
        super().__init__(parent, "📋 Export Trade Slip", width=520, height=440, theme=theme)
        self.quote = quote
        self.config = config
        self.current_style = "box"
        self._build_ui()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0f131c")
        text_main = self.theme.get("text_main", "#f8fafc")
        input_bg = self.theme.get("bg_input", "#111622")

        container = tk.Frame(self, bg=bg, padx=20, pady=16)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="📋 Trade Receipt Slip",
            font=FONTS["title"],
            bg=bg,
            fg=text_main,
        ).pack(anchor="w", pady=(0, 10))

        # Format selector buttons
        format_bar = tk.Frame(container, bg=bg)
        format_bar.pack(fill="x", pady=(0, 10))

        self.btn_box = ModernButton(
            format_bar, text="Box Style", command=lambda: self.switch_style("box"),
            width=90, height=26, bg_color="#2563eb", parent_bg=bg, font=FONTS["small_bold"]
        )
        self.btn_box.pack(side="left", padx=(0, 6))

        self.btn_discord = ModernButton(
            format_bar, text="Discord", command=lambda: self.switch_style("discord"),
            width=90, height=26, bg_color="#222a3a", parent_bg=bg, font=FONTS["small_bold"]
        )
        self.btn_discord.pack(side="left", padx=6)

        self.btn_compact = ModernButton(
            format_bar, text="Compact", command=lambda: self.switch_style("compact"),
            width=90, height=26, bg_color="#222a3a", parent_bg=bg, font=FONTS["small_bold"]
        )
        self.btn_compact.pack(side="left", padx=6)

        # Text display
        self.text_box = tk.Text(
            container,
            font=FONTS["mono"],
            bg=input_bg,
            fg=text_main,
            relief="solid",
            bd=1,
            padx=12,
            pady=10,
        )
        self.text_box.pack(fill="both", expand=True)

        # Bottom action bar
        btn_bar = tk.Frame(container, bg=bg)
        btn_bar.pack(fill="x", pady=(12, 0))

        self.copy_btn = ModernButton(
            btn_bar,
            text="Copy to Clipboard",
            command=self.copy_slip,
            width=160,
            height=34,
            bg_color="#10b981",
            parent_bg=bg,
        )
        self.copy_btn.pack(side="left")

        ModernButton(
            btn_bar,
            text="Close",
            command=self.destroy,
            width=90,
            height=34,
            bg_color=self.theme.get("btn_neutral_bg", "#222a3a"),
            text_color=self.theme.get("btn_neutral_fg", "#e2e8f0"),
            parent_bg=bg,
        ).pack(side="right")

        self.refresh_text()

    def switch_style(self, style: str):
        self.current_style = style
        self.btn_box.update_colors("#2563eb" if style == "box" else "#222a3a", self.theme.get("bg_app", "#0f131c"))
        self.btn_discord.update_colors("#2563eb" if style == "discord" else "#222a3a", self.theme.get("bg_app", "#0f131c"))
        self.btn_compact.update_colors("#2563eb" if style == "compact" else "#222a3a", self.theme.get("bg_app", "#0f131c"))
        self.refresh_text()

    def refresh_text(self):
        use_comma = self.config.get("use_comma_bdt", False)
        symbol = self.config.get("currency_symbol", TAKA)
        slip = generate_trade_slip(self.quote, use_comma=use_comma, symbol=symbol, style=self.current_style)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert("1.0", slip)

    def copy_slip(self):
        content = self.text_box.get("1.0", tk.END).strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update()
            self.copy_btn.set_text("✓ Copied Slip!")
            self.after(1400, lambda: self.copy_btn.set_text("Copy to Clipboard"))


class HistoryDialog(BaseModal):
    """Recent calculation history viewer."""
    def __init__(self, parent, config: ConfigManager, theme: dict, on_restore: Callable[[Dict[str, Any]], None]):
        super().__init__(parent, "📜 Calculation History", width=560, height=440, theme=theme)
        self.config = config
        self.on_restore = on_restore
        self._build_ui()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0f131c")
        text_main = self.theme.get("text_main", "#f8fafc")
        input_bg = self.theme.get("bg_input", "#111622")

        container = tk.Frame(self, bg=bg, padx=20, pady=16)
        container.pack(fill="both", expand=True)

        header_bar = tk.Frame(container, bg=bg)
        header_bar.pack(fill="x", pady=(0, 10))

        tk.Label(
            header_bar,
            text="📜 Recent Calculations",
            font=FONTS["title"],
            bg=bg,
            fg=text_main,
        ).pack(side="left")

        ModernButton(
            header_bar,
            text="Clear All",
            command=self._clear,
            width=80,
            height=26,
            bg_color="#dc2626",
            parent_bg=bg,
            font=FONTS["small_bold"],
        ).pack(side="right")

        # Scrollable list
        list_frame = tk.Frame(container, bg=input_bg, bd=1, relief="solid")
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            list_frame,
            font=FONTS["mono"],
            bg=input_bg,
            fg=text_main,
            selectbackground="#2563eb",
            selectforeground="#ffffff",
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.history_items = self.config.get("history", [])
        self._populate()

        # Bottom buttons
        btn_bar = tk.Frame(container, bg=bg)
        btn_bar.pack(fill="x", pady=(12, 0))

        ModernButton(
            btn_bar,
            text="Restore Selected",
            command=self._restore_selected,
            width=140,
            height=34,
            bg_color="#2563eb",
            parent_bg=bg,
        ).pack(side="left")

        ModernButton(
            btn_bar,
            text="Close",
            command=self.destroy,
            width=90,
            height=34,
            bg_color=self.theme.get("btn_neutral_bg", "#222a3a"),
            text_color=self.theme.get("btn_neutral_fg", "#e2e8f0"),
            parent_bg=bg,
        ).pack(side="right")

    def _populate(self):
        self.listbox.delete(0, tk.END)
        if not self.history_items:
            self.listbox.insert(tk.END, "  No calculations recorded yet.")
            return

        for idx, item in enumerate(self.history_items):
            ts = item.get("timestamp", "")
            amt = item.get("amount_usd", 0.0)
            r = item.get("rate") or "-"
            line = f" [{ts}]  ${amt:<6.2f} | Rate: {r}/$"
            self.listbox.insert(tk.END, line)

    def _restore_selected(self):
        sel = self.listbox.curselection()
        if not sel or not self.history_items:
            return
        idx = sel[0]
        if 0 <= idx < len(self.history_items):
            item = self.history_items[idx]
            if self.on_restore:
                self.on_restore(item)
            self.destroy()

    def _clear(self):
        self.config.clear_history()
        self.history_items = []
        self._populate()


class AboutDialog(BaseModal):
    """About & Help modal with CS2 trade explanation and shortcuts."""
    def __init__(self, parent, theme: dict):
        super().__init__(parent, "About SkinRate Pro", width=500, height=440, theme=theme)
        self._build_ui()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0f131c")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#8593a8")
        card_bg = self.theme.get("bg_card", "#181e2b")

        container = tk.Frame(self, bg=bg, padx=22, pady=18)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="🎮 SkinRate Calculator Pro v3.0",
            font=FONTS["title"],
            bg=bg,
            fg=text_main,
        ).pack(anchor="w")

        tk.Label(
            container,
            text="Fast, accurate CS2 skins and Steam wallet rate calculator.",
            font=FONTS["body"],
            bg=bg,
            fg=text_muted,
        ).pack(anchor="w", pady=(3, 12))

        card = tk.Frame(container, bg=card_bg, padx=14, pady=10, bd=1, relief="solid")
        card.pack(fill="both", expand=True)

        help_text = (
            "🔥 Version 3.0 Highlights:\n"
            " • Unified Skin & Steam wallet transfer rate calculation\n"
            " • Normal standard rate presets (85/$ default)\n"
            " • MFS Cashout: bKash Agent, Priyo, and Nagad\n"
            " • 15% Steam Community Market Tax (+15% / -15%)\n"
            " • Reverse Calculator (BDT Budget -> USD Skins/Wallet)\n"
            " • Rate Cheat Sheet table ($1 to $1,000)\n"
            " • 1-Click Trade Slip for Discord, Facebook, and Messenger\n\n"
            "⌨️ Keyboard Shortcuts:\n"
            " • Enter        : Calculate\n"
            " • Esc          : Clear fields\n"
            " • Ctrl+C       : Copy trade slip\n"
            " • Ctrl+H       : View calculation history\n"
            " • Ctrl+T       : Toggle Dark / Light theme\n"
            " • Ctrl+S       : Preferences & Settings\n"
            " • Ctrl+1..3    : Switch tabs"
        )

        tk.Label(
            card,
            text=help_text,
            font=FONTS["small"],
            bg=card_bg,
            fg=text_main,
            justify="left",
            anchor="w",
        ).pack(fill="both", expand=True)

        btn_bar = tk.Frame(container, bg=bg)
        btn_bar.pack(fill="x", pady=(12, 0))

        ModernButton(
            btn_bar,
            text="Close",
            command=self.destroy,
            width=90,
            height=32,
            bg_color="#2563eb",
            parent_bg=bg,
        ).pack(side="right")
