"""
Reverse Calculator Tab:
Calculates how much USD skin/wallet can be bought with a given BDT budget.
Clean, modern aesthetic with zero clutter.
"""

from __future__ import annotations
import tkinter as tk
from typing import Callable, Optional, Dict, Any
from skinrate.theme import FONTS, shade
from skinrate.widgets import ModernButton, ChipButton, ResultRow
from skinrate.engine import (
    clean_input,
    format_bdt,
    format_usd,
    calculate_reverse,
    TAKA,
)


class ReverseView(tk.Frame):
    def __init__(
        self,
        master,
        config,
        theme: dict,
        on_status: Optional[Callable[[str, str], None]] = None,
    ):
        super().__init__(master, bg=theme.get("bg_app", "#0f131c"))
        self.config = config
        self.theme = theme
        self.on_status = on_status
        self.fee_mode_var = tk.StringVar(value="none")
        self._debounce_id = None

        self._build_ui()
        self.reset_to_defaults()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0f131c")
        card_bg = self.theme.get("bg_card", "#181e2b")
        inner_bg = self.theme.get("bg_card_inner", "#202738")
        input_bg = self.theme.get("bg_input", "#111622")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#8593a8")
        primary = self.theme.get("primary", "#38bdf8")
        steam_acc = self.theme.get("steam_accent", "#06b6d4")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ----------------- Input Card (2 Columns) -----------------
        input_card = tk.Frame(self, bg=card_bg, padx=20, pady=14, bd=1, relief="solid")
        input_card.grid(row=0, column=0, sticky="ew", padx=20, pady=(12, 10))
        input_card.grid_columnconfigure((0, 1), weight=1, uniform="reverse_inputs")

        # Column 0: BDT Amount
        col0 = tk.Frame(input_card, bg=card_bg)
        col0.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        col0.grid_columnconfigure(0, weight=1)

        h0 = tk.Frame(col0, bg=card_bg)
        h0.pack(fill="x", pady=(0, 4))
        tk.Label(h0, text="BDT Budget / Cash", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left")
        tk.Label(h0, text="BDT ৳", font=FONTS["badge"], bg=shade(card_bg, 14), fg=primary, padx=6, pady=1).pack(side="right")

        self.bdt_entry = tk.Entry(col0, font=FONTS["value_lg"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid")
        self.bdt_entry.pack(fill="x", ipady=5)
        self.bdt_entry.bind("<KeyRelease>", self._on_input_changed)

        chips0 = tk.Frame(col0, bg=card_bg)
        chips0.pack(fill="x", pady=(6, 0))
        for chip_val in ["500", "1000", "2500", "5000", "10000"]:
            ChipButton(chips0, text=f"৳{chip_val}", command=lambda v=chip_val: self._set_bdt(v), parent_bg=card_bg, width=48).pack(side="left", padx=2)

        # Column 1: Rate
        col1 = tk.Frame(input_card, bg=card_bg)
        col1.grid(row=0, column=1, sticky="ew", padx=(12, 0))
        col1.grid_columnconfigure(0, weight=1)

        h1 = tk.Frame(col1, bg=card_bg)
        h1.pack(fill="x", pady=(0, 4))
        tk.Label(h1, text="Rate (৳/$)", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left")
        tk.Label(h1, text="Normal: 85/$", font=FONTS["badge"], bg=shade(card_bg, 14), fg="#38bdf8", padx=6, pady=1).pack(side="right")

        self.rate_entry = tk.Entry(col1, font=FONTS["value_lg"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid")
        self.rate_entry.pack(fill="x", ipady=5)
        self.rate_entry.bind("<KeyRelease>", self._on_input_changed)

        chips1 = tk.Frame(col1, bg=card_bg)
        chips1.pack(fill="x", pady=(6, 0))
        for chip_val in ["80", "82", "85", "87", "90"]:
            ChipButton(chips1, text=chip_val, command=lambda v=chip_val: self._set_rate(v), parent_bg=card_bg, width=44).pack(side="left", padx=2)

        # Mode Selection Row
        mode_strip = tk.Frame(input_card, bg=card_bg)
        mode_strip.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        tk.Label(mode_strip, text="MFS Cashout Deduction:", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left", padx=(0, 8))

        for mode_id, mode_label in [
            ("none", "Direct (0%)"),
            ("agent", "bKash Agent (1.85%)"),
            ("priyo", "bKash Priyo (1.49%)"),
            ("nagad", "Nagad App (1.25%)"),
        ]:
            rb = tk.Radiobutton(
                mode_strip,
                text=mode_label,
                value=mode_id,
                variable=self.fee_mode_var,
                command=self.calculate,
                font=FONTS["small_bold"],
                bg=card_bg,
                fg=text_main,
                selectcolor=input_bg,
                activebackground=card_bg,
                activeforeground=text_main,
            )
            rb.pack(side="left", padx=4)

        ModernButton(
            mode_strip,
            text="⚡ Calculate",
            command=self.calculate,
            width=116,
            height=30,
            bg_color="#2563eb",
            parent_bg=card_bg,
            font=FONTS["small_bold"],
        ).pack(side="right")

        # ----------------- Results Grid (2 Balanced Cards) -----------------
        results_grid = tk.Frame(self, bg=bg)
        results_grid.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 14))
        results_grid.grid_columnconfigure((0, 1), weight=1, uniform="reverse_results_2col")
        results_grid.grid_rowconfigure(0, weight=1)

        # Card 1: USD Purchase Value
        self.usd_rows = self._build_result_card(
            results_grid, col=0, title="💎 USD Purchase Power",
            subtitle="Equivalent skin & wallet balance value", accent=primary,
            keys=["USD Value ($)", "Net BDT Used", "MFS Fee Deducted"]
        )

        # Card 2: Steam Tax (15%)
        self.tax_rows = self._build_result_card(
            results_grid, col=1, title="🏷️ Steam Market Tax (15%)",
            subtitle="Listing and received amounts with 15% tax", accent=steam_acc,
            keys=["With 15% Tax", "Without 15% Tax"]
        )

    def _build_result_card(self, master, col: int, title: str, subtitle: str, accent: str, keys: list[str]):
        card_bg = self.theme.get("bg_card", "#181e2b")
        inner_bg = self.theme.get("bg_card_inner", "#202738")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#8593a8")

        card = tk.Frame(master, bg=card_bg, bd=1, relief="solid")
        card.grid(row=0, column=col, sticky="nsew", padx=6)
        card.grid_columnconfigure(0, weight=1)

        accent_bar = tk.Frame(card, bg=accent, height=3)
        accent_bar.pack(fill="x")

        head = tk.Frame(card, bg=card_bg, padx=16, pady=12)
        head.pack(fill="x")
        tk.Label(head, text=title, font=FONTS["h2"], bg=card_bg, fg=text_main).pack(anchor="w")
        tk.Label(head, text=subtitle, font=FONTS["small"], bg=card_bg, fg=text_muted).pack(anchor="w", pady=(1, 0))

        body = tk.Frame(card, bg=card_bg, padx=14, pady=8)
        body.pack(fill="both", expand=True)

        rows = {}
        for key in keys:
            row = ResultRow(
                body,
                title=key,
                accent_color=accent,
                bg=inner_bg,
                text_color=text_main,
                muted_color=text_muted,
                on_copy_feedback=self._on_copy_feedback,
            )
            row.pack(fill="x", pady=4)
            rows[key] = row
        return rows

    def _on_copy_feedback(self, msg: str):
        if self.on_status:
            self.on_status(f"✓ {msg}", self.theme.get("success", "#10b981"))

    def _set_bdt(self, val: str):
        self.bdt_entry.delete(0, tk.END)
        self.bdt_entry.insert(0, val)
        self.calculate()

    def _set_rate(self, val: str):
        self.rate_entry.delete(0, tk.END)
        self.rate_entry.insert(0, val)
        self.calculate()

    def _on_input_changed(self, _event=None):
        if not self.config.get("live_calc", True):
            return
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(120, self.calculate)

    def reset_to_defaults(self):
        default_r = self.config.get("default_rate", 85.0)
        self.rate_entry.delete(0, tk.END)
        self.rate_entry.insert(0, str(default_r))

    def calculate(self):
        try:
            bdt_val = clean_input(self.bdt_entry.get())
            if bdt_val is None:
                for group in (self.usd_rows, self.tax_rows):
                    for row in group.values():
                        row.set_value("-", is_active=False)
                return

            rate = clean_input(self.rate_entry.get()) or 85.0
            mode = self.fee_mode_var.get()
            use_comma = self.config.get("use_comma_bdt", False)
            sym = self.config.get("currency_symbol", TAKA)

            res = calculate_reverse(bdt_val, rate, fee_mode=mode)
            self.usd_rows["USD Value ($)"].set_value(format_usd(res["usd_value"]))
            self.usd_rows["Net BDT Used"].set_value(format_bdt(res["net_bdt"], sym, use_comma))
            self.usd_rows["MFS Fee Deducted"].set_value(format_bdt(res["fee_amount"], sym, use_comma))

            self.tax_rows["With 15% Tax"].set_value(format_usd(res["with_15_tax"]))
            self.tax_rows["Without 15% Tax"].set_value(format_usd(res["without_15_tax"]))

            if self.on_status:
                self.on_status(f"✓ Reverse calculated for {format_bdt(bdt_val, sym, use_comma)}", self.theme.get("success", "#10b981"))
        except ValueError as exc:
            if self.on_status:
                self.on_status(str(exc), self.theme.get("danger", "#f43f5e"))
