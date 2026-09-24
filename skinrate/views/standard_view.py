"""
Standard Rate Calculator Tab:
Unified CS2 skin & Steam wallet transfer rate calculation with MFS cashout and 15% Steam tax.
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
    calculate_quote,
    TAKA,
)


class StandardView(tk.Frame):
    def __init__(
        self,
        master,
        config,
        theme: dict,
        on_quote_change: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_status: Optional[Callable[[str, str], None]] = None,
    ):
        super().__init__(master, bg=theme.get("bg_app", "#0f131c"))
        self.config = config
        self.theme = theme
        self.on_quote_change = on_quote_change
        self.on_status = on_status
        self.latest_quote: Optional[Dict[str, Any]] = None
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

        # ----------------- Top Input Card (2 Columns) -----------------
        input_card = tk.Frame(self, bg=card_bg, padx=20, pady=14, bd=1, relief="solid")
        input_card.grid(row=0, column=0, sticky="ew", padx=20, pady=(12, 10))
        input_card.grid_columnconfigure((0, 1), weight=1, uniform="inputs_2col")

        # Column 0: Amount
        col0 = tk.Frame(input_card, bg=card_bg)
        col0.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        col0.grid_columnconfigure(0, weight=1)

        h0 = tk.Frame(col0, bg=card_bg)
        h0.pack(fill="x", pady=(0, 4))
        tk.Label(h0, text="Amount ($)", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left")
        tk.Label(h0, text="USD", font=FONTS["badge"], bg=shade(card_bg, 14), fg=primary, padx=6, pady=1).pack(side="right")

        self.amount_entry = tk.Entry(
            col0, font=FONTS["value_lg"], bg=input_bg, fg=text_main,
            insertbackground=text_main, bd=1, relief="solid"
        )
        self.amount_entry.pack(fill="x", ipady=5)
        self.amount_entry.bind("<KeyRelease>", self._on_input_changed)

        chips0 = tk.Frame(col0, bg=card_bg)
        chips0.pack(fill="x", pady=(6, 0))
        for chip_val in ["5", "10", "25", "50", "100", "200"]:
            ChipButton(chips0, text=f"${chip_val}", command=lambda v=chip_val: self._set_amount(v), parent_bg=card_bg).pack(side="left", padx=2)

        # Column 1: Rate (৳/$)
        col1 = tk.Frame(input_card, bg=card_bg)
        col1.grid(row=0, column=1, sticky="ew", padx=(12, 0))
        col1.grid_columnconfigure(0, weight=1)

        h1 = tk.Frame(col1, bg=card_bg)
        h1.pack(fill="x", pady=(0, 4))
        tk.Label(h1, text="Rate (৳/$)", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left")
        tk.Label(h1, text="Normal: 85/$", font=FONTS["badge"], bg=shade(card_bg, 14), fg="#38bdf8", padx=6, pady=1).pack(side="right")

        self.rate_entry = tk.Entry(
            col1, font=FONTS["value_lg"], bg=input_bg, fg=text_main,
            insertbackground=text_main, bd=1, relief="solid"
        )
        self.rate_entry.pack(fill="x", ipady=5)
        self.rate_entry.bind("<KeyRelease>", self._on_input_changed)

        chips1 = tk.Frame(col1, bg=card_bg)
        chips1.pack(fill="x", pady=(6, 0))
        for chip_val in ["80", "82", "85", "87", "90"]:
            ChipButton(chips1, text=chip_val, command=lambda v=chip_val: self._set_rate(v), parent_bg=card_bg).pack(side="left", padx=2)

        # Action row
        action_strip = tk.Frame(input_card, bg=card_bg)
        action_strip.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        action_strip.grid_columnconfigure(0, weight=1)

        self.info_label = tk.Label(
            action_strip,
            text="💡 Enter amount in USD. Skin and Steam wallet rates calculate automatically in real time.",
            font=FONTS["small"],
            bg=card_bg,
            fg=text_muted,
            anchor="w",
        )
        self.info_label.grid(row=0, column=0, sticky="w")

        btn_box = tk.Frame(action_strip, bg=card_bg)
        btn_box.grid(row=0, column=1, sticky="e")

        ModernButton(
            btn_box,
            text="Clear",
            command=self.clear_fields,
            width=76,
            height=30,
            bg_color=self.theme.get("btn_neutral_bg", "#222a3a"),
            hover_color=self.theme.get("btn_neutral_hover", "#2d374d"),
            text_color=self.theme.get("btn_neutral_fg", "#e2e8f0"),
            parent_bg=card_bg,
            font=FONTS["small_bold"],
        ).pack(side="left", padx=(0, 6))

        ModernButton(
            btn_box,
            text="⚡ Calculate",
            command=self.calculate,
            width=116,
            height=30,
            bg_color="#2563eb",
            hover_color="#1d4ed8",
            parent_bg=card_bg,
            font=FONTS["small_bold"],
        ).pack(side="left")

        # ----------------- Results Grid (2 Balanced Cards) -----------------
        results_grid = tk.Frame(self, bg=bg)
        results_grid.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 14))
        results_grid.grid_columnconfigure((0, 1), weight=1, uniform="results_2col")
        results_grid.grid_rowconfigure(0, weight=1)

        # Card 1: Transfer & Cashout
        self.transfer_rows = self._build_result_card(
            results_grid,
            col=0,
            title="💸 Transfer & Cashout",
            subtitle="CS2 skins & Steam wallet transfer rate",
            accent=primary,
            keys=["Cost (Base)", "bKash Agent (+1.85%)", "bKash Priyo (+1.49%)", "Nagad App (+1.25%)"],
        )

        # Card 2: Steam Tax
        self.steam_rows = self._build_result_card(
            results_grid,
            col=1,
            title="🏷️ Steam Tax (15%)",
            subtitle="Standard 15% Steam Community Market tax",
            accent=steam_acc,
            keys=["With 15% Tax", "Without 15% Tax", "Base Amount"],
        )

    def _build_result_card(
        self,
        master,
        col: int,
        title: str,
        subtitle: str,
        accent: str,
        keys: list[str],
    ) -> dict[str, ResultRow]:
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

    def _set_amount(self, val: str):
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, val)
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

    def clear_fields(self):
        self.amount_entry.delete(0, tk.END)
        self.reset_to_defaults()
        for group in (self.transfer_rows, self.steam_rows):
            for row in group.values():
                row.set_value("-", is_active=False)
        self.latest_quote = None
        if self.on_status:
            self.on_status("Ready. Enter amount to calculate.", self.theme.get("text_muted", "#8593a8"))

    def set_inputs(self, amount: float, rate: Optional[float] = None):
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, str(amount))
        if rate is not None:
            self.rate_entry.delete(0, tk.END)
            self.rate_entry.insert(0, str(rate))
        self.calculate()

    def calculate(self):
        try:
            amt_val = clean_input(self.amount_entry.get())
            if amt_val is None:
                for group in (self.transfer_rows, self.steam_rows):
                    for row in group.values():
                        row.set_value("-", is_active=False)
                return

            rate = clean_input(self.rate_entry.get()) or 85.0
            custom_fee = float(self.config.get("custom_fee_pct", 1.85))
            use_comma = self.config.get("use_comma_bdt", False)
            sym = self.config.get("currency_symbol", TAKA)

            quote = calculate_quote(
                amount_usd=amt_val,
                rate=rate,
                custom_fee_pct=custom_fee,
            )
            self.latest_quote = quote

            # Update Transfer & Cashout Card
            self.transfer_rows["Cost (Base)"].set_value(format_bdt(quote["base_cost"], sym, use_comma))
            self.transfer_rows["bKash Agent (+1.85%)"].set_value(format_bdt(quote["agent_cost"], sym, use_comma))
            self.transfer_rows["bKash Priyo (+1.49%)"].set_value(format_bdt(quote["priyo_cost"], sym, use_comma))
            self.transfer_rows["Nagad App (+1.25%)"].set_value(format_bdt(quote["nagad_cost"], sym, use_comma))

            # Update Steam Tax Card
            self.steam_rows["With 15% Tax"].set_value(format_usd(quote["with_15_tax"]))
            self.steam_rows["Without 15% Tax"].set_value(format_usd(quote["without_15_tax"]))
            self.steam_rows["Base Amount"].set_value(format_usd(amt_val))

            # History entry
            self.config.add_history_entry({
                "amount_usd": amt_val,
                "rate": rate,
            })

            if self.on_quote_change:
                self.on_quote_change(quote)

            if self.on_status:
                self.on_status(f"✓ Calculated for {format_usd(amt_val)} @ {format_bdt(rate, sym, use_comma)}/$", self.theme.get("success", "#10b981"))
        except ValueError as exc:
            if self.on_status:
                self.on_status(str(exc), self.theme.get("danger", "#f43f5e"))
