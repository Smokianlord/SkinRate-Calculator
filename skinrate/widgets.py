"""
Modern UI widgets for SkinRate Calculator Pro.
Custom-drawn high-DPI widgets with smooth rounded shapes, hover states, and animations.
"""

from __future__ import annotations
import tkinter as tk
from typing import Callable, Optional, List, Tuple
from skinrate.theme import shade, FONTS


def draw_rounded_rect(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: float = 8.0,
    **kwargs
) -> int:
    """Draw a smooth anti-aliased rounded rectangle on a Tkinter canvas."""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=20, **kwargs)


class ModernButton(tk.Canvas):
    """
    Modern button with smooth rounded corners, hover transitions, and press feedback.
    """
    def __init__(
        self,
        master,
        text: str = "",
        command: Optional[Callable] = None,
        *,
        width: int = 140,
        height: int = 38,
        radius: int = 8,
        bg_color: str = "#2563eb",
        hover_color: Optional[str] = None,
        active_color: Optional[str] = None,
        text_color: str = "#ffffff",
        font=FONTS["body_bold"],
        parent_bg: str = "#161f30",
        border_color: Optional[str] = None,
        border_width: int = 0,
        cursor: str = "hand2",
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            cursor=cursor,
            takefocus=1,
        )
        self.w = width
        self.h = height
        self.radius = radius
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color or shade(bg_color, 20)
        self.active_color = active_color or shade(bg_color, -20)
        self.current_color = self.bg_color
        self.text_color = text_color
        self.font = font
        self.parent_bg = parent_bg
        self.border_color = border_color
        self.border_width = border_width
        self.is_pressed = False
        self.is_hovered = False

        self._draw()
        self.bind("<Enter>", self._on_enter, add="+")
        self.bind("<Leave>", self._on_leave, add="+")
        self.bind("<ButtonPress-1>", self._on_press, add="+")
        self.bind("<ButtonRelease-1>", self._on_release, add="+")
        self.bind("<Return>", lambda _e: self.invoke(), add="+")
        self.bind("<space>", lambda _e: self.invoke(), add="+")

    def _draw(self):
        self.delete("all")
        y_offset = 1 if self.is_pressed else 0
        pad = 2
        fill = self.active_color if self.is_pressed else (self.hover_color if self.is_hovered else self.current_color)

        draw_rounded_rect(
            self,
            pad,
            pad + y_offset,
            self.w - pad,
            self.h - pad + y_offset,
            radius=self.radius,
            fill=fill,
            outline=self.border_color if self.border_color else "",
            width=self.border_width,
        )

        self.create_text(
            self.w / 2,
            self.h / 2 + y_offset,
            text=self.text,
            fill=self.text_color,
            font=self.font,
        )

    def _on_enter(self, _event):
        self.is_hovered = True
        self._draw()

    def _on_leave(self, _event):
        self.is_hovered = False
        self.is_pressed = False
        self._draw()

    def _on_press(self, _event):
        self.focus_set()
        self.is_pressed = True
        self._draw()

    def _on_release(self, event):
        was_pressed = self.is_pressed
        self.is_pressed = False
        self._draw()
        if was_pressed and 0 <= event.x <= self.w and 0 <= event.y <= self.h:
            self.invoke()

    def set_text(self, new_text: str):
        self.text = new_text
        self._draw()

    def update_colors(self, bg_color: str, parent_bg: str, text_color: str = "#ffffff"):
        self.bg_color = bg_color
        self.current_color = bg_color
        self.hover_color = shade(bg_color, 20)
        self.active_color = shade(bg_color, -20)
        self.parent_bg = parent_bg
        self.text_color = text_color
        self.configure(bg=parent_bg)
        self._draw()

    def invoke(self):
        if self.command:
            self.command()


class ChipButton(ModernButton):
    """Compact preset chip button (e.g. +$10, 120, etc.)."""
    def __init__(
        self,
        master,
        text: str,
        command: Optional[Callable] = None,
        *,
        width: int = 56,
        height: int = 24,
        bg_color: str = "#202c40",
        text_color: str = "#93c5fd",
        parent_bg: str = "#161f30",
        font=FONTS["small_bold"],
    ):
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            radius=6,
            bg_color=bg_color,
            hover_color=shade(bg_color, 25),
            active_color=shade(bg_color, -15),
            text_color=text_color,
            parent_bg=parent_bg,
            font=font,
        )


class PillTabBar(tk.Frame):
    """
    Segmented top control tab bar.
    """
    def __init__(
        self,
        master,
        tabs: List[Tuple[str, str]],  # [(id, label), ...]
        on_change: Callable[[str], None],
        *,
        bg: str = "#111827",
        active_bg: str = "#2563eb",
        inactive_fg: str = "#94a3b8",
        active_fg: str = "#ffffff",
    ):
        super().__init__(master, bg=bg)
        self.tabs = tabs
        self.on_change = on_change
        self.active_id = tabs[0][0] if tabs else ""
        self.bg = bg
        self.active_bg = active_bg
        self.inactive_fg = inactive_fg
        self.active_fg = active_fg
        self.buttons: dict[str, tk.Label] = {}
        self._build()

    def _build(self):
        container = tk.Frame(self, bg=shade(self.bg, 10), padx=3, pady=3)
        container.pack(fill="y")

        for tab_id, label in self.tabs:
            is_active = (tab_id == self.active_id)
            btn = tk.Label(
                container,
                text=label,
                font=FONTS["body_bold"],
                bg=self.active_bg if is_active else shade(self.bg, 10),
                fg=self.active_fg if is_active else self.inactive_fg,
                padx=12,
                pady=6,
                cursor="hand2",
            )
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda _e, t=tab_id: self.select_tab(t))
            btn.bind("<Enter>", lambda _e, b=btn, t=tab_id: self._on_hover(b, t))
            btn.bind("<Leave>", lambda _e, b=btn, t=tab_id: self._on_leave(b, t))
            self.buttons[tab_id] = btn

    def select_tab(self, tab_id: str):
        if tab_id == self.active_id:
            return
        self.active_id = tab_id
        self._update_styles()
        if self.on_change:
            self.on_change(tab_id)

    def _update_styles(self):
        for tab_id, btn in self.buttons.items():
            is_active = (tab_id == self.active_id)
            btn.configure(
                bg=self.active_bg if is_active else shade(self.bg, 10),
                fg=self.active_fg if is_active else self.inactive_fg,
            )

    def _on_hover(self, btn: tk.Label, tab_id: str):
        if tab_id != self.active_id:
            btn.configure(bg=shade(self.bg, 20), fg="#f8fafc")

    def _on_leave(self, btn: tk.Label, tab_id: str):
        if tab_id != self.active_id:
            btn.configure(bg=shade(self.bg, 10), fg=self.inactive_fg)


class ResultRow(tk.Frame):
    """
    Row in a result card: Label + Value + Compact 1-Click Copy Button.
    """
    def __init__(
        self,
        master,
        title: str,
        initial_value: str = "-",
        *,
        accent_color: str = "#3b82f6",
        bg: str = "#1d293d",
        text_color: str = "#f8fafc",
        muted_color: str = "#94a3b8",
        on_copy_feedback: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(master, bg=bg, padx=10, pady=7)
        self.title_text = title
        self.accent_color = accent_color
        self.bg = bg
        self.text_color = text_color
        self.muted_color = muted_color
        self.on_copy_feedback = on_copy_feedback
        self.reset_timer_id = None

        self.grid_columnconfigure(1, weight=1)

        self.label_title = tk.Label(
            self,
            text=title,
            font=FONTS["small_bold"],
            bg=bg,
            fg=muted_color,
            anchor="w",
        )
        self.label_title.grid(row=0, column=0, sticky="w")

        self.label_value = tk.Label(
            self,
            text=initial_value,
            font=FONTS["value_lg"],
            bg=bg,
            fg=text_color,
            anchor="e",
        )
        self.label_value.grid(row=0, column=1, sticky="ew", padx=(8, 10))

        self.copy_btn = ModernButton(
            self,
            text="Copy",
            command=self.copy_to_clipboard,
            width=64,
            height=26,
            radius=5,
            bg_color=shade(accent_color, -10),
            hover_color=accent_color,
            text_color="#ffffff",
            font=FONTS["small_bold"],
            parent_bg=bg,
        )
        self.copy_btn.grid(row=0, column=2, sticky="e")

    def set_value(self, value: str, is_active: bool = True):
        self.label_value.configure(
            text=value,
            fg=self.text_color if is_active else self.muted_color,
        )

    def get_value(self) -> str:
        return self.label_value.cget("text")

    def copy_to_clipboard(self):
        val = self.get_value()
        if not val or val in ("-", "...", "N/A"):
            return
        self.clipboard_clear()
        self.clipboard_append(val)
        self.update()

        # Temporary button feedback
        self.copy_btn.set_text("✓")
        self.copy_btn.update_colors("#10b981", self.bg, "#ffffff")

        if self.on_copy_feedback:
            self.on_copy_feedback(f"Copied {val} ({self.title_text})")

        if self.reset_timer_id:
            self.after_cancel(self.reset_timer_id)
        self.reset_timer_id = self.after(1400, self._restore_copy_btn)

    def _restore_copy_btn(self):
        self.copy_btn.set_text("Copy")
        self.copy_btn.update_colors(shade(self.accent_color, -10), self.bg, "#ffffff")
        self.reset_timer_id = None
