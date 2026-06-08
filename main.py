import tkinter as tk
from pathlib import Path
import sys

TAKA = "\u09F3"
APP_NAME = "SkinRate Calculator"

BG = "#eaf1ff"
BG_DARK = "#0f172a"
PANEL = "#ffffff"
PANEL_ALT = "#f8fbff"
TEXT = "#162033"
MUTED = "#64748b"
BORDER = "#d8e2f0"
PRIMARY = "#2563eb"
PRIMARY_HOVER = "#1d4ed8"
SUCCESS = "#16a34a"
SUCCESS_HOVER = "#15803d"
WARNING = "#f97316"
WARNING_HOVER = "#ea580c"
PURPLE = "#7c3aed"
PURPLE_HOVER = "#6d28d9"
ERROR = "#dc2626"


def resource_path(relative_path: str) -> Path:
    """Return a usable path both in source mode and PyInstaller mode."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def money_bdt(value: float) -> str:
    # Customer requested no comma and no space: e.g. \u09F31200
    return f"{TAKA}{int(round(value))}"


def money_usd(value: float) -> str:
    return f"${value:,.2f}"


def clean_number(raw: str) -> str:
    return (
        raw.strip()
        .replace(",", "")
        .replace("$", "")
        .replace(TAKA, "")
        .replace("t" + "k", "")
        .replace("T" + "k", "")
        .replace("t" + "K", "")
        .replace("T" + "K", "")
    )


def parse_positive_value(raw: str, label: str, required: bool = False):
    cleaned = clean_number(raw)
    if not cleaned:
        if required:
            raise ValueError(f"Please enter {label}.")
        return None
    try:
        value = float(cleaned)
    except ValueError as exc:
        raise ValueError(f"{label} must be a valid number.") from exc
    if value <= 0:
        raise ValueError(f"{label} must be greater than 0.")
    return value


def shade(hex_color: str, amount: int) -> str:
    hex_color = hex_color.lstrip("#")
    r = max(0, min(255, int(hex_color[0:2], 16) + amount))
    g = max(0, min(255, int(hex_color[2:4], 16) + amount))
    b = max(0, min(255, int(hex_color[4:6], 16) + amount))
    return f"#{r:02x}{g:02x}{b:02x}"


class Color3DButton(tk.Canvas):
    def __init__(
        self,
        master,
        *,
        text: str,
        command,
        color: str,
        hover_color: str,
        width: int = 150,
        height: int = 42,
        font=("Segoe UI", 11, "bold"),
        text_color: str = "white",
        bg: str = PANEL,
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            takefocus=1,
        )
        self.text = text
        self.command = command
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_color = text_color
        self.font = font
        self.w = width
        self.h = height
        self.pressed = False
        self._draw()
        self.bind("<Enter>", self._on_enter, add="+")
        self.bind("<Leave>", self._on_leave, add="+")
        self.bind("<ButtonPress-1>", self._on_press, add="+")
        self.bind("<ButtonRelease-1>", self._on_release, add="+")
        self.bind("<Return>", lambda _event: self.invoke(), add="+")
        self.bind("<space>", lambda _event: self.invoke(), add="+")

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return self.create_polygon(points, smooth=True, splinesteps=16, **kwargs)

    def _draw(self):
        self.delete("all")
        lift = 2 if self.pressed else 0
        depth = 3 if self.pressed else 7
        base = self.current_color
        dark = shade(base, -45)
        darker = shade(base, -70)
        light = shade(base, 32)

        self._rounded_rect(7, 8, self.w - 2, self.h - 1, 14, fill="#9aa8bd", outline="")
        self._rounded_rect(3, 5 + lift, self.w - 5, self.h - 2, 14, fill=darker, outline="")
        self._rounded_rect(3, 1 + lift, self.w - 8, self.h - depth, 14, fill=base, outline=dark, width=1)
        self.create_line(13, 8 + lift, self.w - 21, 8 + lift, fill=light, width=2)
        self.create_text(
            (self.w - 8) // 2,
            (self.h - depth) // 2 + lift + 1,
            text=self.text,
            fill=self.text_color,
            font=self.font,
        )

    def _on_enter(self, _event):
        self.current_color = self.hover_color
        self._draw()

    def _on_leave(self, _event):
        self.pressed = False
        self.current_color = self.color
        self._draw()

    def _on_press(self, _event):
        self.focus_set()
        self.pressed = True
        self._draw()

    def _on_release(self, event):
        inside = 0 <= event.x <= self.w and 0 <= event.y <= self.h
        self.pressed = False
        self._draw()
        if inside:
            self.invoke()

    def invoke(self):
        if self.command:
            self.command()


class SkinRateCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title(APP_NAME)
        self.configure(bg=BG)
        self.minsize(990, 670)
        self.resizable(True, True)
        self.copied_after_id = None
        self.icons = {}

        icon_path = resource_path("assets/skinrate.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except tk.TclError:
                pass

        self._load_icons()
        self._build_ui()
        self.bind("<Return>", self.calculate)
        self.amount_entry.focus_set()
        self.update_idletasks()
        self.deiconify()

    def _load_icons(self):
        for name in ("amount", "item", "wallet"):
            path = resource_path(f"assets/{name}.png")
            if path.exists():
                try:
                    self.icons[name] = tk.PhotoImage(file=str(path))
                except tk.TclError:
                    self.icons[name] = None

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        shell = tk.Frame(self, bg=BG)
        shell.grid(row=0, column=0, sticky="nsew", padx=28, pady=24)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(2, weight=1)

        self._build_header(shell)
        self._build_form(shell)
        self._build_results(shell)


    def _build_header(self, master):
        header = tk.Frame(master, bg=BG_DARK, bd=0, relief=tk.RAISED, padx=18, pady=16)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        logo = tk.Label(
            header,
            text="SR",
            font=("Segoe UI", 18, "bold"),
            bg="#38bdf8",
            fg="#082f49",
            width=4,
            height=1,
            relief=tk.RAISED,
            bd=3,
        )
        logo.grid(row=0, column=0, sticky="w", padx=(0, 14))

        tk.Label(
            header,
            text=APP_NAME,
            font=("Segoe UI", 27, "bold"),
            bg=BG_DARK,
            fg="white",
        ).grid(row=0, column=1, sticky="w")
        badge = tk.Label(
            header,
            text="v2",
            font=("Segoe UI", 11, "bold"),
            bg="#facc15",
            fg="#422006",
            relief=tk.RAISED,
            bd=3,
            padx=16,
            pady=6,
        )
        badge.grid(row=0, column=2, sticky="e")

    def _build_form(self, master):
        form_card = self._card(master, bg=PANEL, padx=18, pady=18)
        form_card.grid(row=1, column=0, sticky="ew", pady=(18, 16))
        form_card.grid_columnconfigure((0, 1, 2), weight=1, uniform="inputs")

        self.amount_entry = self._input_group(
            form_card,
            label="Amount ($)",
            placeholder="Example: 25",
            icon_name="amount",
            accent="#10b981",
            row=0,
            col=0,
        )
        self.item_rate_entry = self._input_group(
            form_card,
            label="Item rate",
            placeholder="Example: 120",
            icon_name="item",
            accent="#2563eb",
            row=0,
            col=1,
        )
        self.wallet_rate_entry = self._input_group(
            form_card,
            label="Wallet rate",
            placeholder="Example: 118",
            icon_name="wallet",
            accent="#7c3aed",
            row=0,
            col=2,
        )

        action_row = tk.Frame(form_card, bg=PANEL)
        action_row.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(18, 0))
        action_row.grid_columnconfigure(0, weight=1)

        self.status_label = tk.Label(
            action_row,
            text="Enter amount. Item and wallet rates are optional.",
            font=("Segoe UI", 10, "bold"),
            bg=PANEL,
            fg=MUTED,
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=(2, 12))

        Color3DButton(
            action_row,
            text="Reset",
            command=self.reset_fields,
            color=WARNING,
            hover_color=WARNING_HOVER,
            width=120,
            height=44,
            bg=PANEL,
        ).grid(row=0, column=1, sticky="e", padx=(0, 10))

        Color3DButton(
            action_row,
            text="Calculate",
            command=self.calculate,
            color=SUCCESS,
            hover_color=SUCCESS_HOVER,
            width=180,
            height=44,
            font=("Segoe UI", 13, "bold"),
            bg=PANEL,
        ).grid(row=0, column=2, sticky="e")

    def _build_results(self, master):
        self.results = tk.Frame(master, bg=BG)
        self.results.grid(row=2, column=0, sticky="nsew")
        self.results.grid_columnconfigure((0, 1, 2), weight=1, uniform="results")
        self.results.grid_rowconfigure(0, weight=1)

        self.item_values = self._result_card(self.results, "Item Transfer", 0, "#2563eb")
        self.wallet_values = self._result_card(self.results, "Wallet Transfer", 1, "#7c3aed")
        self.misc_values = self._result_card(self.results, "Steam Tax", 2, "#0891b2")

    def _card(self, master, *, bg=PANEL, padx=14, pady=14):
        return tk.Frame(
            master,
            bg=bg,
            bd=3,
            relief=tk.RAISED,
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=padx,
            pady=pady,
        )

    def _input_group(self, master, label: str, placeholder: str, icon_name: str, accent: str, row: int, col: int):
        outer = tk.Frame(master, bg=shade(accent, -25), bd=0, padx=3, pady=3)
        outer.grid(row=row, column=col, sticky="ew", padx=8)
        outer.grid_columnconfigure(0, weight=1)

        group = tk.Frame(outer, bg=PANEL_ALT, bd=2, relief=tk.RAISED, padx=10, pady=10)
        group.grid(row=0, column=0, sticky="ew")
        group.grid_columnconfigure(1, weight=1)

        icon_box = tk.Frame(group, bg=accent, width=48, height=52, bd=3, relief=tk.RAISED)
        icon_box.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(0, 10))
        icon_box.grid_propagate(False)

        icon_img = self.icons.get(icon_name)
        if icon_img:
            tk.Label(icon_box, image=icon_img, bg=accent).place(relx=0.5, rely=0.5, anchor="center")
        else:
            tk.Label(icon_box, text=icon_name[:1].upper(), font=("Segoe UI", 16, "bold"), bg=accent, fg="white").place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            group,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg=PANEL_ALT,
            fg=TEXT,
        ).grid(row=0, column=1, sticky="w", pady=(0, 4))

        entry_shell = tk.Frame(group, bg="#cbd5e1", bd=0, padx=2, pady=2)
        entry_shell.grid(row=1, column=1, sticky="ew")
        entry_shell.grid_columnconfigure(0, weight=1)

        entry = tk.Entry(
            entry_shell,
            font=("Segoe UI", 13, "bold"),
            relief=tk.FLAT,
            bd=0,
            bg="white",
            fg=TEXT,
            insertbackground=TEXT,
        )
        entry.grid(row=0, column=0, sticky="ew", ipady=5, padx=1, pady=1)
        self._add_placeholder(entry, placeholder)
        return entry

    def _add_placeholder(self, entry: tk.Entry, text: str):
        entry.placeholder = text
        entry.placeholder_active = True
        entry.insert(0, text)
        entry.configure(fg="#94a3b8")

        def on_focus_in(_event):
            if getattr(entry, "placeholder_active", False):
                entry.delete(0, tk.END)
                entry.configure(fg=TEXT)
                entry.placeholder_active = False

        def on_focus_out(_event):
            if not entry.get():
                entry.insert(0, entry.placeholder)
                entry.configure(fg="#94a3b8")
                entry.placeholder_active = True

        entry.bind("<FocusIn>", on_focus_in, add="+")
        entry.bind("<FocusOut>", on_focus_out, add="+")

    def _entry_value(self, entry: tk.Entry):
        if getattr(entry, "placeholder_active", False):
            return ""
        return entry.get()

    def _result_card(self, master, title: str, column: int, accent: str):
        card = self._card(master, bg=PANEL, padx=0, pady=0)
        card.grid(row=0, column=column, sticky="nsew", padx=8)
        card.grid_columnconfigure(0, weight=1)

        header = tk.Frame(card, bg=accent, bd=0, padx=14, pady=11)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        tk.Label(
            header,
            text=title,
            font=("Segoe UI", 15, "bold"),
            bg=accent,
            fg="white",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        body = tk.Frame(card, bg=PANEL, padx=14, pady=14)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)

        keys = ["Cost", "Cashout Agent", "Cashout Priyo"]
        if title == "Steam Tax":
            keys = ["With 15% Tax", "Without 15% Tax", "Base Amount"]

        value_labels = {}
        for r, key in enumerate(keys):
            row_frame = tk.Frame(body, bg=PANEL_ALT, bd=2, relief=tk.RAISED, padx=10, pady=8)
            row_frame.grid(row=r, column=0, columnspan=3, sticky="ew", pady=5)
            row_frame.grid_columnconfigure(1, weight=1)

            tk.Label(
                row_frame,
                text=key,
                font=("Segoe UI", 9, "bold"),
                bg=PANEL_ALT,
                fg=MUTED,
            ).grid(row=0, column=0, sticky="w")

            value_label = tk.Label(
                row_frame,
                text="-",
                font=("Segoe UI", 12, "bold"),
                bg=PANEL_ALT,
                fg=TEXT,
                anchor="e",
            )
            value_label.grid(row=0, column=1, sticky="ew", padx=(8, 8))
            value_labels[key] = value_label

            Color3DButton(
                row_frame,
                text="Copy",
                command=lambda label=value_label: self.copy_value(label),
                color=accent,
                hover_color=shade(accent, -20),
                width=82,
                height=33,
                font=("Segoe UI", 8, "bold"),
                bg=PANEL_ALT,
            ).grid(row=0, column=2, sticky="e")

        return value_labels

    def calculate(self, _event=None):
        try:
            amount = parse_positive_value(self._entry_value(self.amount_entry), "Amount", required=True)
            item_rate = parse_positive_value(self._entry_value(self.item_rate_entry), "Item rate")
            wallet_rate = parse_positive_value(self._entry_value(self.wallet_rate_entry), "Wallet rate")

            self._set_result(self.misc_values["With 15% Tax"], money_usd(amount * 1.15))
            self._set_result(self.misc_values["Without 15% Tax"], money_usd(amount * 0.85))
            self._set_result(self.misc_values["Base Amount"], money_usd(amount))

            if item_rate:
                item_cost = amount * item_rate
                self._set_result(self.item_values["Cost"], money_bdt(item_cost))
                self._set_result(self.item_values["Cashout Agent"], money_bdt(item_cost * 1.0185))
                self._set_result(self.item_values["Cashout Priyo"], money_bdt(item_cost * 1.0149))
            else:
                self._clear_group(self.item_values, "Enter item rate")

            if wallet_rate:
                wallet_cost = amount * wallet_rate
                self._set_result(self.wallet_values["Cost"], money_bdt(wallet_cost))
                self._set_result(self.wallet_values["Cashout Agent"], money_bdt(wallet_cost * 1.0185))
                self._set_result(self.wallet_values["Cashout Priyo"], money_bdt(wallet_cost * 1.0149))
            else:
                self._clear_group(self.wallet_values, "Enter wallet rate")

            self._status("Calculated successfully.", SUCCESS)
        except ValueError as exc:
            self._status(str(exc), ERROR)

    def reset_fields(self):
        for entry in (self.amount_entry, self.item_rate_entry, self.wallet_rate_entry):
            entry.delete(0, tk.END)
            entry.placeholder_active = False
            entry.event_generate("<FocusOut>")
        for group in (self.item_values, self.wallet_values, self.misc_values):
            for label in group.values():
                label.configure(text="-", fg=TEXT)
        self._status("Cleared. Ready for new calculation.", PRIMARY)
        self.amount_entry.focus_set()

    def _set_result(self, label: tk.Label, value: str):
        label.configure(text=value, fg=TEXT)

    def _clear_group(self, labels: dict, message: str):
        first = True
        for label in labels.values():
            label.configure(text=message if first else "-", fg=MUTED)
            first = False

    def copy_value(self, label: tk.Label):
        value = label.cget("text")
        if value in {"-", "Enter item rate", "Enter wallet rate"}:
            self._status("Nothing to copy yet.", ERROR)
            return
        self.clipboard_clear()
        self.clipboard_append(value)
        self.update()
        self._status(f"Copied {value}", PRIMARY)

    def _status(self, text: str, color: str):
        self.status_label.configure(text=text, fg=color)
        if self.copied_after_id:
            self.after_cancel(self.copied_after_id)
            self.copied_after_id = None
        if color != ERROR:
            self.copied_after_id = self.after(
                2500,
                lambda: self.status_label.configure(
                    text="Enter amount. Item and wallet rates are optional.",
                    fg=MUTED,
                ),
            )


if __name__ == "__main__":
    SkinRateCalculator().mainloop()
