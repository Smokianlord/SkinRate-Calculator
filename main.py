import tkinter as tk
from pathlib import Path
import sys

TAKA = "\u09F3"
APP_NAME = "SkinRate Calculator"
BG = "#edf3fb"
PANEL = "#ffffff"
PANEL_ALT = "#f7faff"
TEXT = "#172033"
MUTED = "#64748b"
PRIMARY = "#2563eb"
PRIMARY_DARK = "#1d4ed8"
SUCCESS = "#16a34a"
ERROR = "#dc2626"
BUTTON_SHADOW = "#0f172a"


def resource_path(relative_path: str) -> Path:
    """Return a usable path both in source mode and PyInstaller mode."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def money_bdt(value: float) -> str:
    return f"{TAKA}{int(value):,}"


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


class ThreeDButton(tk.Button):
    def __init__(self, master, *, bg, active_bg, **kwargs):
        super().__init__(
            master,
            bg=bg,
            activebackground=active_bg,
            fg=kwargs.pop("fg", "white"),
            activeforeground=kwargs.pop("activeforeground", "white"),
            relief=tk.RAISED,
            bd=4,
            cursor="hand2",
            highlightthickness=0,
            takefocus=True,
            **kwargs,
        )
        self.default_bg = bg
        self.active_bg = active_bg
        self.bind("<Enter>", self._hover_on, add="+")
        self.bind("<Leave>", self._hover_off, add="+")
        self.bind("<ButtonPress-1>", self._press, add="+")
        self.bind("<ButtonRelease-1>", self._release, add="+")

    def _hover_on(self, _event):
        self.configure(bg=self.active_bg)

    def _hover_off(self, _event):
        self.configure(bg=self.default_bg, relief=tk.RAISED)

    def _press(self, _event):
        self.configure(relief=tk.SUNKEN)

    def _release(self, _event):
        self.configure(relief=tk.RAISED)


class SkinRateCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title(APP_NAME)
        self.configure(bg=BG)
        self.minsize(900, 620)
        self.resizable(True, True)
        self.copied_after_id = None
        self.copy_values = {}

        icon_path = resource_path("assets/skinrate.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except tk.TclError:
                pass

        self._build_ui()
        self.bind("<Return>", self.calculate)
        self.amount_entry.focus_set()
        self.update_idletasks()
        self.deiconify()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        shell = tk.Frame(self, bg=BG)
        shell.grid(row=0, column=0, sticky="nsew", padx=28, pady=24)
        shell.grid_columnconfigure(0, weight=1)

        header = tk.Frame(shell, bg=BG)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        tk.Label(
            header,
            text=APP_NAME,
            font=("Segoe UI", 25, "bold"),
            bg=BG,
            fg=TEXT,
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            header,
            text="Fast CS2 item, wallet and cashout conversion",
            font=("Segoe UI", 11),
            bg=BG,
            fg=MUTED,
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        form_card = self._card(shell)
        form_card.grid(row=1, column=0, sticky="ew", pady=(22, 16))
        for i in range(6):
            form_card.grid_columnconfigure(i, weight=1)

        self.amount_entry = self._input_group(form_card, "Amount ($)", "Example: 25", 0, 0)
        self.item_rate_entry = self._input_group(form_card, "Item rate", "Example: 120", 0, 2)
        self.wallet_rate_entry = self._input_group(form_card, "Wallet rate", "Example: 118", 0, 4)

        action_row = tk.Frame(form_card, bg=PANEL)
        action_row.grid(row=2, column=0, columnspan=6, sticky="ew", pady=(16, 0))
        action_row.grid_columnconfigure(0, weight=1)

        self.status_label = tk.Label(
            action_row,
            text="Enter amount. Item and wallet rates are optional.",
            font=("Segoe UI", 10),
            bg=PANEL,
            fg=MUTED,
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=(2, 12))

        ThreeDButton(
            action_row,
            text="Calculate",
            command=self.calculate,
            bg=SUCCESS,
            active_bg="#15803d",
            font=("Segoe UI", 13, "bold"),
            width=18,
            pady=6,
        ).grid(row=0, column=1, sticky="e")

        self.results = tk.Frame(shell, bg=BG)
        self.results.grid(row=2, column=0, sticky="nsew")
        self.results.grid_columnconfigure((0, 1, 2), weight=1, uniform="results")

        self.item_values = self._result_card(self.results, "Item Transfer", 0)
        self.wallet_values = self._result_card(self.results, "Wallet Transfer", 1)
        self.misc_values = self._result_card(self.results, "Steam Tax", 2)

        footer = tk.Label(
            shell,
            text="Tip: Press Enter to calculate. Copy buttons copy only the final value.",
            font=("Segoe UI", 9),
            bg=BG,
            fg=MUTED,
        )
        footer.grid(row=3, column=0, sticky="w", pady=(14, 0))

    def _card(self, master):
        return tk.Frame(
            master,
            bg=PANEL,
            bd=3,
            relief=tk.RAISED,
            highlightthickness=1,
            highlightbackground="#dbe5f0",
            padx=18,
            pady=18,
        )

    def _input_group(self, master, label: str, placeholder: str, row: int, col: int):
        group = tk.Frame(master, bg=PANEL)
        group.grid(row=row, column=col, columnspan=2, sticky="ew", padx=8)
        group.grid_columnconfigure(0, weight=1)

        tk.Label(
            group,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg=PANEL,
            fg=TEXT,
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        entry = tk.Entry(
            group,
            font=("Segoe UI", 13),
            relief=tk.SUNKEN,
            bd=3,
            bg="#fbfdff",
            fg=TEXT,
            insertbackground=TEXT,
            highlightthickness=1,
            highlightbackground="#dbe5f0",
            highlightcolor=PRIMARY,
        )
        entry.grid(row=1, column=0, sticky="ew")
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

    def _result_card(self, master, title: str, column: int):
        card = self._card(master)
        card.grid(row=0, column=column, sticky="nsew", padx=8)
        card.grid_columnconfigure(1, weight=1)

        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 15, "bold"),
            bg=PANEL,
            fg=TEXT,
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        keys = ["Cost", "Cashout Agent", "Cashout Priyo"]
        if title == "Steam Tax":
            keys = ["With 15% Tax", "Without 15% Tax", "Base Amount"]

        value_labels = {}
        for r, key in enumerate(keys, start=1):
            tk.Label(
                card,
                text=key,
                font=("Segoe UI", 10),
                bg=PANEL,
                fg=MUTED,
            ).grid(row=r, column=0, sticky="w", pady=6)

            value_label = tk.Label(
                card,
                text="—",
                font=("Segoe UI", 12, "bold"),
                bg=PANEL,
                fg=TEXT,
                anchor="e",
            )
            value_label.grid(row=r, column=1, sticky="ew", padx=(8, 8), pady=6)
            value_labels[key] = value_label

            ThreeDButton(
                card,
                text="Copy",
                command=lambda label=value_label: self.copy_value(label),
                bg=PRIMARY,
                active_bg=PRIMARY_DARK,
                font=("Segoe UI", 9, "bold"),
                width=7,
                pady=1,
            ).grid(row=r, column=2, sticky="e", pady=6)

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
                item_cost = int(amount * item_rate)
                self._set_result(self.item_values["Cost"], money_bdt(item_cost))
                self._set_result(self.item_values["Cashout Agent"], money_bdt(item_cost * 1.0185))
                self._set_result(self.item_values["Cashout Priyo"], money_bdt(item_cost * 1.0149))
            else:
                self._clear_group(self.item_values, "Enter item rate")

            if wallet_rate:
                wallet_cost = int(amount * wallet_rate)
                self._set_result(self.wallet_values["Cost"], money_bdt(wallet_cost))
                self._set_result(self.wallet_values["Cashout Agent"], money_bdt(wallet_cost * 1.0185))
                self._set_result(self.wallet_values["Cashout Priyo"], money_bdt(wallet_cost * 1.0149))
            else:
                self._clear_group(self.wallet_values, "Enter wallet rate")

            self._status("Calculated successfully.", SUCCESS)
        except ValueError as exc:
            self._status(str(exc), ERROR)

    def _set_result(self, label: tk.Label, value: str):
        label.configure(text=value, fg=TEXT)

    def _clear_group(self, labels: dict, message: str):
        first = True
        for label in labels.values():
            label.configure(text=message if first else "—", fg=MUTED)
            first = False

    def copy_value(self, label: tk.Label):
        value = label.cget("text")
        if value in {"—", "Enter item rate", "Enter wallet rate"}:
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
