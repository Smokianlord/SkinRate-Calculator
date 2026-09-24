"""
Theme and Design Tokens for SkinRate Calculator Pro.
Supports Dark and Light themes with modern typography and color palettes.
"""

from typing import Dict, Any

THEMES: Dict[str, Dict[str, str]] = {
    "dark": {
        "bg_app": "#0b0f17",
        "bg_toolbar": "#111827",
        "bg_toolbar_border": "#1f293d",
        "bg_card": "#161f30",
        "bg_card_inner": "#1d293d",
        "bg_input": "#0f1724",
        "border": "#243247",
        "border_focus": "#3b82f6",
        "text_main": "#f8fafc",
        "text_muted": "#94a3b8",
        "text_dim": "#64748b",
        "primary": "#3b82f6",
        "primary_hover": "#2563eb",
        "primary_fg": "#ffffff",
        "success": "#10b981",
        "success_hover": "#059669",
        "success_fg": "#ffffff",
        "purple": "#8b5cf6",
        "purple_hover": "#7c3aed",
        "purple_fg": "#ffffff",
        "amber": "#f59e0b",
        "amber_hover": "#d97706",
        "amber_fg": "#0f172a",
        "cyan": "#06b6d4",
        "cyan_hover": "#0891b2",
        "danger": "#ef4444",
        "danger_hover": "#dc2626",
        "danger_fg": "#ffffff",
        "chip_bg": "#202c40",
        "chip_hover": "#2b3b54",
        "chip_text": "#93c5fd",
        "tab_active_bg": "#2563eb",
        "tab_active_fg": "#ffffff",
        "tab_inactive_bg": "transparent",
        "tab_inactive_fg": "#94a3b8",
        "tab_hover_bg": "#1e293b",
        "row_alt": "#141c2c",
        "status_bg": "#0c1320",
    },
    "light": {
        "bg_app": "#f1f5f9",
        "bg_toolbar": "#ffffff",
        "bg_toolbar_border": "#e2e8f0",
        "bg_card": "#ffffff",
        "bg_card_inner": "#f8fafc",
        "bg_input": "#ffffff",
        "border": "#e2e8f0",
        "border_focus": "#2563eb",
        "text_main": "#0f172a",
        "text_muted": "#475569",
        "text_dim": "#94a3b8",
        "primary": "#2563eb",
        "primary_hover": "#1d4ed8",
        "primary_fg": "#ffffff",
        "success": "#059669",
        "success_hover": "#047857",
        "success_fg": "#ffffff",
        "purple": "#7c3aed",
        "purple_hover": "#6d28d9",
        "purple_fg": "#ffffff",
        "amber": "#d97706",
        "amber_hover": "#b45309",
        "amber_fg": "#ffffff",
        "cyan": "#0891b2",
        "cyan_hover": "#0e7490",
        "danger": "#dc2626",
        "danger_hover": "#b91c1c",
        "danger_fg": "#ffffff",
        "chip_bg": "#e2e8f0",
        "chip_hover": "#cbd5e1",
        "chip_text": "#1d4ed8",
        "tab_active_bg": "#2563eb",
        "tab_active_fg": "#ffffff",
        "tab_inactive_bg": "transparent",
        "tab_inactive_fg": "#64748b",
        "tab_hover_bg": "#f1f5f9",
        "row_alt": "#f8fafc",
        "status_bg": "#ffffff",
    },
}

FONTS = {
    "title": ("Segoe UI", 16, "bold"),
    "h2": ("Segoe UI", 13, "bold"),
    "h3": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "small_bold": ("Segoe UI", 9, "bold"),
    "mono": ("Consolas", 10),
    "value_lg": ("Segoe UI", 13, "bold"),
    "badge": ("Segoe UI", 8, "bold"),
}


def shade(hex_color: str, amount: int) -> str:
    """Lighten or darken a hex color string."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r = max(0, min(255, int(hex_color[0:2], 16) + amount))
    g = max(0, min(255, int(hex_color[2:4], 16) + amount))
    b = max(0, min(255, int(hex_color[4:6], 16) + amount))
    return f"#{r:02x}{g:02x}{b:02x}"
