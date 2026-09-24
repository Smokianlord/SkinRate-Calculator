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
    def __init__(self, parent, title: str, width: int = 520, height: int = 420, theme: dict = None):
        super().__init__(parent)
        self.theme = theme or {}
        self.title(title)
        self.configure(bg=self.theme.get("bg_app", "#0b0f17"))
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        # Center on parent
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
        super().__init__(parent, "Settings & Preferences", width=520, height=480, theme=theme)
        self.config = config
        self.on_save = on_save
        self._build_ui()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0b0f17")
        card_bg = self.theme.get("bg_card", "#161f30")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#94a3b8")
        input_bg = self.theme.get("bg_input", "#0f1724")
        border = self.theme.get("border", "#243247")
        primary = self.theme.get("primary", "#3b82f6")

        container = tk.Frame(self, bg=bg, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        header = tk.Label(
            container,
            text="⚙️ Preferences & Presets",
            font=FONTS["title"],
            bg=bg,
            fg=text_main,
            anchor="w",
        )
        header.pack(fill="x", pady=(0, 16))

        card = tk.Frame(container, bg=card_bg, padx=16, pady=16, bd=1, relief="solid")
        card.pack(fill="x")
        card.grid_columnconfigure(1, weight=1)

        # Default Item Rate
        tk.Label(card, text="Default Item Rate (৳/$):", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=0, column=0, sticky="w", pady=8)
        self.item_rate_entry = tk.Entry(card, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid", width=12)
        self.item_rate_entry.grid(row=0, column=1, sticky="e", pady=8)
        self.item_rate_entry.insert(0, str(self.config.get("default_item_rate", 120.0)))

        # Default Wallet Rate
        tk.Label(card, text="Default Wallet Rate (৳/$):", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=1, column=0, sticky="w", pady=8)
        self.wallet_rate_entry = tk.Entry(card, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid", width=12)
        self.wallet_rate_entry.grid(row=1, column=1, sticky="e", pady=8)
        self.wallet_rate_entry.insert(0, str(self.config.get("default_wallet_rate", 118.0)))

        # Custom Cashout Fee %
        tk.Label(card, text="Custom Cashout Fee (%):", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=2, column=0, sticky="w", pady=8)
        self.fee_entry = tk.Entry(card, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid", width=12)
        self.fee_entry.grid(row=2, column=1, sticky="e", pady=8)
        self.fee_entry.insert(0, str(self.config.get("custom_fee_pct", 1.85)))

        # Comma formatting
        tk.Label(card, text="Format Taka with Commas:", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=3, column=0, sticky="w", pady=8)
        self.comma_var = tk.BooleanVar(value=self.config.get("use_comma_bdt", False))
        tk.Checkbutton(card, variable=self.comma_var, bg=card_bg, activebackground=card_bg, selectcolor=input_bg).grid(row=3, column=1, sticky="e", pady=8)

        # Live calculation
        tk.Label(card, text="Live Instant Calculation:", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=4, column=0, sticky="w", pady=8)
        self.live_calc_var = tk.BooleanVar(value=self.config.get("live_calc", True))
        tk.Checkbutton(card, variable=self.live_calc_var, bg=card_bg, activebackground=card_bg, selectcolor=input_bg).grid(row=4, column=1, sticky="e", pady=8)

        # Action Buttons
        btn_bar = tk.Frame(container, bg=bg)
        btn_bar.pack(fill="x", pady=(20, 0))

        ModernButton(
            btn_bar,
            text="Cancel",
            command=self.destroy,
            width=110,
            height=36,
            bg_color="#475569",
            parent_bg=bg,
        ).pack(side="right", padx=(8, 0))

        ModernButton(
            btn_bar,
            text="Save Settings",
            command=self._save,
            width=140,
            height=36,
            bg_color=primary,
            parent_bg=bg,
        ).pack(side="right")

    def _save(self):
        try:
            item_r = float(self.item_rate_entry.get().strip())
            wallet_r = float(self.wallet_rate_entry.get().strip())
            fee_p = float(self.fee_entry.get().strip())
        except ValueError:
            return

        self.config.set("default_item_rate", item_r, auto_save=False)
        self.config.set("default_wallet_rate", wallet_r, auto_save=False)
        self.config.set("custom_fee_pct", fee_p, auto_save=False)
        self.config.set("use_comma_bdt", self.comma_var.get(), auto_save=False)
        self.config.set("live_calc", self.live_calc_var.get(), auto_save=True)

        if self.on_save:
            self.on_save()
        self.destroy()


class TradeSlipDialog(BaseModal):
    """Trade slip exporter modal for copying formatted quotes."""
    def __init__(self, parent, quote: Dict[str, Any], config: ConfigManager, theme: dict):
        super().__init__(parent, "📋 Export Trade Slip", width=540, height=480, theme=theme)
        self.quote = quote
        self.config = config
        self.current_style = "box"
        self._build_ui()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0b0f17")
        text_main = self.theme.get("text_main", "#f8fafc")
        input_bg = self.theme.get("bg_input", "#0f1724")
        primary = self.theme.get("primary", "#3b82f6")

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
            width=100, height=28, bg_color=primary, parent_bg=bg, font=FONTS["small_bold"]
        )
        self.btn_box.pack(side="left", padx=(0, 6))

        self.btn_discord = ModernButton(
            format_bar, text="Discord", command=lambda: self.switch_style("discord"),
            width=100, height=28, bg_color="#475569", parent_bg=bg, font=FONTS["small_bold"]
        )
        self.btn_discord.pack(side="left", padx=6)

        self.btn_compact = ModernButton(
            format_bar, text="Compact", command=lambda: self.switch_style("compact"),
            width=100, height=28, bg_color="#475569", parent_bg=bg, font=FONTS["small_bold"]
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
        btn_bar.pack(fill="x", pady=(14, 0))

        self.copy_btn = ModernButton(
            btn_bar,
            text="Copy to Clipboard",
            command=self.copy_slip,
            width=180,
            height=36,
            bg_color=self.theme.get("success", "#10b981"),
            parent_bg=bg,
        )
        self.copy_btn.pack(side="left")

        ModernButton(
            btn_bar,
            text="Close",
            command=self.destroy,
            width=100,
            height=36,
            bg_color="#475569",
            parent_bg=bg,
        ).pack(side="right")

        self.refresh_text()

    def switch_style(self, style: str):
        self.current_style = style
        primary = self.theme.get("primary", "#3b82f6")
        self.btn_box.update_colors(primary if style == "box" else "#475569", self.theme.get("bg_app", "#0b0f17"))
        self.btn_discord.update_colors(primary if style == "discord" else "#475569", self.theme.get("bg_app", "#0b0f17"))
        self.btn_compact.update_colors(primary if style == "compact" else "#475569", self.theme.get("bg_app", "#0b0f17"))
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
            self.after(1500, lambda: self.copy_btn.set_text("Copy to Clipboard"))


class HistoryDialog(BaseModal):
    """Recent calculation history viewer."""
    def __init__(self, parent, config: ConfigManager, theme: dict, on_restore: Callable[[Dict[str, Any]], None]):
        super().__init__(parent, "📜 Calculation History", width=620, height=480, theme=theme)
        self.config = config
        self.on_restore = on_restore
        self._build_ui()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0b0f17")
        text_main = self.theme.get("text_main", "#f8fafc")
        input_bg = self.theme.get("bg_input", "#0f1724")
        text_muted = self.theme.get("text_muted", "#94a3b8")

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
            width=90,
            height=28,
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
            selectbackground=self.theme.get("primary", "#3b82f6"),
            selectforeground="#ffffff",
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Populate
        self.history_items = self.config.get("history", [])
        self._populate()

        # Bottom buttons
        btn_bar = tk.Frame(container, bg=bg)
        btn_bar.pack(fill="x", pady=(14, 0))

        ModernButton(
            btn_bar,
            text="Restore Selected",
            command=self._restore_selected,
            width=150,
            height=36,
            bg_color=self.theme.get("primary", "#3b82f6"),
            parent_bg=bg,
        ).pack(side="left")

        ModernButton(
            btn_bar,
            text="Close",
            command=self.destroy,
            width=100,
            height=36,
            bg_color="#475569",
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
            item_r = item.get("item_rate") or "-"
            wall_r = item.get("wallet_rate") or "-"
            line = f" [{ts}]  ${amt:<6.2f} | Item Rate: {item_r} | Wallet Rate: {wall_r}"
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
        super().__init__(parent, "About SkinRate Pro", width=540, height=480, theme=theme)
        self._build_ui()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0b0f17")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#94a3b8")
        primary = self.theme.get("primary", "#3b82f6")
        card_bg = self.theme.get("bg_card", "#161f30")

        container = tk.Frame(self, bg=bg, padx=24, pady=20)
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
            text="The ultimate CS2 & Steam wallet rate calculator for Bangladeshi traders.",
            font=FONTS["body"],
            bg=bg,
            fg=text_muted,
        ).pack(anchor="w", pady=(4, 14))

        card = tk.Frame(container, bg=card_bg, padx=16, pady=12, bd=1, relief="solid")
        card.pack(fill="both", expand=True)

        help_text = (
            "🔥 What's New in v3.0 Pro:\n"
            " • Top application toolbar with instant mode switching\n"
            " • Exact Steam Market 15% fee breakdown (Valve 5% + CS2 10%)\n"
            " • Reverse Calculator: Budget in BDT -> USD Skins/Wallet\n"
            " • CS2 Skin Flip Profit & ROI Calculator\n"
            " • Live cheat sheet rate matrix ($1 to $500)\n"
            " • MFS Cashout: bKash Agent, Priyo, and Nagad options\n"
            " • 1-Click Trade Slip Generator for Discord & Facebook\n"
            " • Calculation History log & customizable default presets\n\n"
            "⌨️ Keyboard Shortcuts:\n"
            " • Enter        : Calculate\n"
            " • Esc          : Clear fields\n"
            " • Ctrl+C       : Copy trade slip\n"
            " • Ctrl+H       : View calculation history\n"
            " • Ctrl+T       : Toggle Dark / Light theme\n"
            " • Ctrl+S       : Preferences & Settings\n"
            " • Ctrl+1..4    : Switch tabs"
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
        btn_bar.pack(fill="x", pady=(14, 0))

        ModernButton(
            btn_bar,
            text="Close",
            command=self.destroy,
            width=110,
            height=36,
            bg_color=primary,
            parent_bg=bg,
        ).pack(side="right")
