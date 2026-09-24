"""
Theme and Design Tokens for SkinRate Calculator Pro.
Cohesive, elegant modern dark and light design inspired by Linear, Steam 2026, and Windows 11.
"""

from typing import Dict, Any

THEMES: Dict[str, Dict[str, str]] = {
    "dark": {
        # App Backgrounds
        "bg_app": "#0f131c",
        "bg_toolbar": "#161b26",
        "bg_toolbar_border": "#232a3b",
        "bg_nav": "#131822",
        "bg_card": "#181e2b",
        "bg_card_inner": "#202738",
        "bg_input": "#111622",
        "border": "#273145",
        "border_light": "#33415c",
        "border_focus": "#38bdf8",

        # Typography
        "text_main": "#f8fafc",
        "text_secondary": "#cbd5e1",
        "text_muted": "#8593a8",
        "text_dim": "#526075",

        # Accents
        "primary": "#38bdf8",          # Ice Sky Blue
        "primary_hover": "#0284c7",
        "primary_fg": "#0f172a",
        "success": "#10b981",          # Emerald
        "success_hover": "#059669",
        "success_fg": "#ffffff",
        "item_accent": "#38bdf8",      # Item Transfer Accent
        "wallet_accent": "#a855f7",    # Wallet Transfer Accent
        "steam_accent": "#06b6d4",     # Steam Market Accent
        "amber": "#f59e0b",
        "danger": "#f43f5e",

        # Controls & Buttons
        "btn_neutral_bg": "#222a3a",
        "btn_neutral_hover": "#2d374d",
        "btn_neutral_fg": "#e2e8f0",
        "chip_bg": "#1c2333",
        "chip_hover": "#28334a",
        "chip_fg": "#7dd3fc",

        # Navigation Tabs
        "tab_bar_bg": "#161b26",
        "tab_active_bg": "#2563eb",
        "tab_active_fg": "#ffffff",
        "tab_inactive_bg": "#161b26",
        "tab_inactive_fg": "#94a3b8",
        "tab_hover_bg": "#202738",

        "statusbar_bg": "#0c1017",
    },
    "light": {
        # App Backgrounds
        "bg_app": "#f8fafc",
        "bg_toolbar": "#ffffff",
        "bg_toolbar_border": "#e2e8f0",
        "bg_nav": "#f1f5f9",
        "bg_card": "#ffffff",
        "bg_card_inner": "#f8fafc",
        "bg_input": "#ffffff",
        "border": "#e2e8f0",
        "border_light": "#cbd5e1",
        "border_focus": "#2563eb",

        # Typography
        "text_main": "#0f172a",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "text_dim": "#94a3b8",

        # Accents
        "primary": "#2563eb",
        "primary_hover": "#1d4ed8",
        "primary_fg": "#ffffff",
        "success": "#059669",
        "success_hover": "#047857",
        "success_fg": "#ffffff",
        "item_accent": "#2563eb",
        "wallet_accent": "#7c3aed",
        "steam_accent": "#0891b2",
        "amber": "#d97706",
        "danger": "#dc2626",

        # Controls & Buttons
        "btn_neutral_bg": "#f1f5f9",
        "btn_neutral_hover": "#e2e8f0",
        "btn_neutral_fg": "#334155",
        "chip_bg": "#f1f5f9",
        "chip_hover": "#e2e8f0",
        "chip_fg": "#2563eb",

        # Navigation Tabs
        "tab_bar_bg": "#f1f5f9",
        "tab_active_bg": "#2563eb",
        "tab_active_fg": "#ffffff",
        "tab_inactive_bg": "#f1f5f9",
        "tab_inactive_fg": "#64748b",
        "tab_hover_bg": "#e2e8f0",

        "statusbar_bg": "#ffffff",
    },
}

FONTS = {
    "title": ("Segoe UI", 15, "bold"),
    "h2": ("Segoe UI", 12, "bold"),
    "h3": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "small_bold": ("Segoe UI", 9, "bold"),
    "mono": ("Consolas", 10),
    "value_lg": ("Segoe UI", 12, "bold"),
    "badge": ("Segoe UI", 8, "bold"),
}


def shade(hex_color: str, amount: int) -> str:
    """Lighten or darken a hex color string safely."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r = max(0, min(255, int(hex_color[0:2], 16) + amount))
    g = max(0, min(255, int(hex_color[2:4], 16) + amount))
    b = max(0, min(255, int(hex_color[4:6], 16) + amount))
    return f"#{r:02x}{g:02x}{b:02x}"
