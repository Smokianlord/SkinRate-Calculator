"""
SkinRate Calculator Pro - v3.0.0
The Ultimate CS2 Skins & Steam Wallet Rate Calculator for Bangladeshi Traders.

Features:
- Dedicated Top Application Header & Mode Navigation Bar
- Unified Skin & Steam Wallet Rate Transfer Calculation (Normal rate: 85/$)
- MFS Cashout (bKash Agent 1.85%, bKash Priyo 1.49%, Nagad App 1.25%)
- 15% Steam Community Market Tax (+15% / -15%)
- Reverse Calculator (BDT Budget -> USD Skins/Wallet)
- Rate Matrix & Live Cheat Sheet ($1 to $1000)
- 1-Click Formatted Trade Slip Exporter for Discord & Facebook
- Persistent Preferences & Calculation History
- High-DPI Razor-Sharp Windows Antialiasing
- Dark & Light Themes
"""

from __future__ import annotations
import sys
import os
import tkinter as tk
from pathlib import Path
from typing import Dict, Any, Optional

# Enable Windows High DPI Awareness before any Tkinter windows are created
if sys.platform == "win32":
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor High DPI
        except Exception:
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)  # System High DPI
            except Exception:
                ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from skinrate import __app_name__, __version__
from skinrate.theme import THEMES, FONTS, shade
from skinrate.config import ConfigManager
from skinrate.widgets import ModernButton, PillTabBar
from skinrate.dialogs import SettingsDialog, HistoryDialog, TradeSlipDialog, AboutDialog
from skinrate.views import StandardView, ReverseView, MatrixView


def resource_path(relative_path: str) -> Path:
    """Return an absolute path usable both in development and PyInstaller standalone build."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


class SkinRateApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()

        self.config_manager = ConfigManager()
        self.current_theme_name = self.config_manager.get("theme", "dark")
        self.theme = THEMES.get(self.current_theme_name, THEMES["dark"])

        self.title(f"{__app_name__} v{__version__}")
        self.configure(bg=self.theme["bg_app"])
        self.minsize(900, 580)
        self.geometry("980x640")

        # Set window icon
        icon_path = resource_path("assets/skinrate.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        self.active_tab_id = "standard"
        self.status_clear_timer = None

        self._build_ui()
        self._bind_shortcuts()

        self.update_idletasks()
        self.deiconify()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_top_header()
        self._build_sub_navbar()
        self._build_content_area()
        self._build_bottom_statusbar()

    def _build_top_header(self):
        """Top bar with Brand on the left and utility buttons on the right."""
        toolbar_bg = self.theme["bg_toolbar"]
        text_main = self.theme["text_main"]

        self.header = tk.Frame(self, bg=toolbar_bg, bd=0, padx=20, pady=8)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)

        # Brand (Left)
        brand = tk.Frame(self.header, bg=toolbar_bg)
        brand.grid(row=0, column=0, sticky="w")

        logo = tk.Label(
            brand,
            text="SR",
            font=("Segoe UI", 12, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            padx=7,
            pady=2,
        )
        logo.pack(side="left", padx=(0, 10))

        tk.Label(
            brand,
            text="SkinRate Calculator",
            font=("Segoe UI", 14, "bold"),
            bg=toolbar_bg,
            fg=text_main,
        ).pack(side="left")

        tk.Label(
            brand,
            text="v3.0",
            font=FONTS["badge"],
            bg=shade(toolbar_bg, 14),
            fg="#38bdf8",
            padx=6,
            pady=2,
        ).pack(side="left", padx=(8, 0))

        # Utilities (Right)
        actions = tk.Frame(self.header, bg=toolbar_bg)
        actions.grid(row=0, column=1, sticky="e")

        theme_text = "☀️ Light" if self.current_theme_name == "dark" else "🌙 Dark"
        self.theme_btn = ModernButton(
            actions,
            text=theme_text,
            command=self.toggle_theme,
            width=76,
            height=28,
            radius=4,
            bg_color=self.theme.get("btn_neutral_bg", "#222a3a"),
            hover_color=self.theme.get("btn_neutral_hover", "#2d374d"),
            text_color=self.theme.get("btn_neutral_fg", "#e2e8f0"),
            font=FONTS["badge"],
            parent_bg=toolbar_bg,
        )
        self.theme_btn.pack(side="left", padx=3)

        self.hist_btn = ModernButton(
            actions,
            text="📜 History",
            command=self.open_history,
            width=76,
            height=28,
            radius=4,
            bg_color=self.theme.get("btn_neutral_bg", "#222a3a"),
            hover_color=self.theme.get("btn_neutral_hover", "#2d374d"),
            text_color=self.theme.get("btn_neutral_fg", "#e2e8f0"),
            font=FONTS["badge"],
            parent_bg=toolbar_bg,
        )
        self.hist_btn.pack(side="left", padx=3)

        self.slip_btn = ModernButton(
            actions,
            text="📋 Trade Slip",
            command=self.open_trade_slip,
            width=90,
            height=28,
            radius=4,
            bg_color="#10b981",
            hover_color="#059669",
            text_color="#ffffff",
            font=FONTS["badge"],
            parent_bg=toolbar_bg,
        )
        self.slip_btn.pack(side="left", padx=3)

        self.settings_btn = ModernButton(
            actions,
            text="⚙️",
            command=self.open_settings,
            width=34,
            height=28,
            radius=4,
            bg_color=self.theme.get("btn_neutral_bg", "#222a3a"),
            hover_color=self.theme.get("btn_neutral_hover", "#2d374d"),
            text_color=self.theme.get("btn_neutral_fg", "#e2e8f0"),
            font=FONTS["small_bold"],
            parent_bg=toolbar_bg,
        )
        self.settings_btn.pack(side="left", padx=3)

        self.about_btn = ModernButton(
            actions,
            text="ℹ️",
            command=self.open_about,
            width=34,
            height=28,
            radius=4,
            bg_color=self.theme.get("btn_neutral_bg", "#222a3a"),
            hover_color=self.theme.get("btn_neutral_hover", "#2d374d"),
            text_color=self.theme.get("btn_neutral_fg", "#e2e8f0"),
            font=FONTS["small_bold"],
            parent_bg=toolbar_bg,
        )
        self.about_btn.pack(side="left", padx=3)

    def _build_sub_navbar(self):
        """Dedicated mode navigation bar positioned cleanly in row 1 with zero risk of cut-off."""
        nav_bg = self.theme["bg_nav"]
        self.navbar = tk.Frame(self, bg=nav_bg, bd=0, padx=16, pady=5)
        self.navbar.grid(row=1, column=0, sticky="ew")

        # 3 clean tabs
        self.tab_bar = PillTabBar(
            self.navbar,
            tabs=[
                ("standard", "⚡ Rate Calculator"),
                ("reverse", "⇄ Reverse Calculator (৳ ➔ $)"),
                ("matrix", "📊 Rate Cheat Sheet"),
            ],
            on_change=self.switch_tab,
            bg=nav_bg,
            active_bg="#2563eb",
            inactive_fg=self.theme["text_muted"],
            active_fg="#ffffff",
        )
        self.tab_bar.pack()

    def _build_content_area(self):
        """Container for switching between view tabs."""
        self.content_container = tk.Frame(self, bg=self.theme["bg_app"])
        self.content_container.grid(row=2, column=0, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        self.views: Dict[str, tk.Frame] = {}

        self.views["standard"] = StandardView(
            self.content_container,
            config=self.config_manager,
            theme=self.theme,
            on_quote_change=self._on_quote_change,
            on_status=self.set_status,
        )

        self.views["reverse"] = ReverseView(
            self.content_container,
            config=self.config_manager,
            theme=self.theme,
            on_status=self.set_status,
        )

        self.views["matrix"] = MatrixView(
            self.content_container,
            config=self.config_manager,
            theme=self.theme,
            on_status=self.set_status,
        )

        self.views["standard"].grid(row=0, column=0, sticky="nsew")

    def _build_bottom_statusbar(self):
        """Bottom status bar with message on left and shortcuts on right."""
        status_bg = self.theme.get("statusbar_bg", "#0c1017")
        text_muted = self.theme["text_muted"]

        self.statusbar = tk.Frame(self, bg=status_bg, padx=16, pady=4)
        self.statusbar.grid(row=3, column=0, sticky="ew")
        self.statusbar.grid_columnconfigure(0, weight=1)

        self.status_label = tk.Label(
            self.statusbar,
            text="Ready. Enter Amount ($). Rate defaults to 85/$.",
            font=FONTS["small"],
            bg=status_bg,
            fg=text_muted,
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        shortcuts_label = tk.Label(
            self.statusbar,
            text="[Enter] Calc  |  [Esc] Clear  |  [Ctrl+C] Trade Slip  |  [Ctrl+T] Theme  |  [Ctrl+1..3] Tabs",
            font=FONTS["badge"],
            bg=status_bg,
            fg=self.theme.get("text_dim", "#526075"),
            anchor="e",
        )
        shortcuts_label.grid(row=0, column=1, sticky="e")

    def switch_tab(self, tab_id: str):
        if tab_id not in self.views:
            return
        self.active_tab_id = tab_id
        for vid, v in self.views.items():
            if vid == tab_id:
                v.grid(row=0, column=0, sticky="nsew")
                if hasattr(v, "calculate"):
                    v.calculate()
            else:
                v.grid_forget()

    def set_status(self, text: str, color: Optional[str] = None):
        color = color or self.theme["text_muted"]
        self.status_label.configure(text=text, fg=color)
        if self.status_clear_timer:
            self.after_cancel(self.status_clear_timer)
        self.status_clear_timer = self.after(
            3500,
            lambda: self.status_label.configure(
                text="Ready.",
                fg=self.theme["text_muted"],
            ),
        )

    def _on_quote_change(self, _quote: Dict[str, Any]):
        pass

    def toggle_theme(self):
        new_theme = "light" if self.current_theme_name == "dark" else "dark"
        self.current_theme_name = new_theme
        self.config_manager.set("theme", new_theme)
        self.theme = THEMES[new_theme]
        self._rebuild_all_views()

    def _rebuild_all_views(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(bg=self.theme["bg_app"])
        self._build_ui()
        self._bind_shortcuts()

    def open_settings(self):
        SettingsDialog(self, self.config_manager, self.theme, on_save=self._on_settings_saved)

    def _on_settings_saved(self):
        std_view = self.views.get("standard")
        if std_view and hasattr(std_view, "reset_to_defaults"):
            std_view.reset_to_defaults()
            std_view.calculate()
        matrix_view = self.views.get("matrix")
        if matrix_view and hasattr(matrix_view, "recalculate"):
            matrix_view.recalculate()
        self.set_status("✓ Settings saved and applied.", self.theme.get("success", "#10b981"))

    def open_history(self):
        HistoryDialog(self, self.config_manager, self.theme, on_restore=self._on_history_restore)

    def _on_history_restore(self, item: Dict[str, Any]):
        self.tab_bar.select_tab("standard")
        std_view = self.views.get("standard")
        if std_view and hasattr(std_view, "set_inputs"):
            std_view.set_inputs(
                amount=item.get("amount_usd", 0.0),
                rate=item.get("rate"),
            )
        self.set_status(f"✓ Restored calculation from {item.get('timestamp')}", self.theme.get("primary", "#38bdf8"))

    def open_trade_slip(self):
        std_view = self.views.get("standard")
        quote = std_view.latest_quote if std_view else None
        if not quote:
            self.set_status("Please perform a calculation first before exporting trade slip.", self.theme.get("danger", "#f43f5e"))
            return
        TradeSlipDialog(self, quote, self.config_manager, self.theme)

    def open_about(self):
        AboutDialog(self, self.theme)

    def _bind_shortcuts(self):
        self.bind("<Return>", self._on_enter_pressed)
        self.bind("<Escape>", self._on_escape_pressed)
        self.bind("<Control-c>", self._on_ctrl_c)
        self.bind("<Control-C>", self._on_ctrl_c)
        self.bind("<Control-t>", lambda _e: self.toggle_theme())
        self.bind("<Control-T>", lambda _e: self.toggle_theme())
        self.bind("<Control-h>", lambda _e: self.open_history())
        self.bind("<Control-H>", lambda _e: self.open_history())
        self.bind("<Control-s>", lambda _e: self.open_settings())
        self.bind("<Control-S>", lambda _e: self.open_settings())
        self.bind("<Control-Key-1>", lambda _e: self.tab_bar.select_tab("standard"))
        self.bind("<Control-Key-2>", lambda _e: self.tab_bar.select_tab("reverse"))
        self.bind("<Control-Key-3>", lambda _e: self.tab_bar.select_tab("matrix"))

    def _on_enter_pressed(self, _event=None):
        active = self.views.get(self.active_tab_id)
        if active and hasattr(active, "calculate"):
            active.calculate()

    def _on_escape_pressed(self, _event=None):
        active = self.views.get(self.active_tab_id)
        if active and hasattr(active, "clear_fields"):
            active.clear_fields()

    def _on_ctrl_c(self, _event=None):
        focus = self.focus_get()
        if isinstance(focus, tk.Entry):
            try:
                if focus.selection_present():
                    return
            except Exception:
                pass
        self.open_trade_slip()


if __name__ == "__main__":
    app = SkinRateApp()
    app.mainloop()
