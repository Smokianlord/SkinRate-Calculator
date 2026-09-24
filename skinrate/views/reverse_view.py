"""
Reverse Calculator Tab:
Calculates how much USD skin/wallet can be bought with a given BDT budget or cashout target.
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
    steam_calc_seller_receives,
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
        super().__init__(master, bg=theme.get("bg_app", "#0b0f17"))
        self.config = config
        self.theme = theme
        self.on_status = on_status
        self.fee_mode_var = tk.StringVar(value="none")
        self._debounce_id = None

        self._build_ui()
        self.reset_to_defaults()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0b0f17")
        card_bg = self.theme.get("bg_card", "#161f30")
        inner_bg = self.theme.get("bg_card_inner", "#1d293d")
        input_bg = self.theme.get("bg_input", "#0f1724")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#94a3b8")
        primary = self.theme.get("primary", "#3b82f6")
        purple = self.theme.get("purple", "#8b5cf6")
        success = self.theme.get("success", "#10b981")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ----------------- Input Card -----------------
        input_card = tk.Frame(self, bg=card_bg, padx=16, pady=14, bd=1, relief="solid")
        input_card.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 10))
        input_card.grid_columnconfigure((0, 1, 2), weight=1, uniform="reverse_inputs")

        # Column 0: BDT Amount
        col0 = tk.Frame(input_card, bg=card_bg)
        col0.grid(row=0, column=0, sticky="ew", padx=6)
        col0.grid_columnconfigure(0, weight=1)

        tk.Label(col0, text="💰 BDT Budget / Cash", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(anchor="w", pady=(0, 4))
        self.bdt_entry = tk.Entry(col0, font=FONTS["value_lg"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid")
        self.bdt_entry.pack(fill="x", ipady=5)
        self.bdt_entry.bind("<KeyRelease>", self._on_input_changed)

        chips0 = tk.Frame(col0, bg=card_bg)
        chips0.pack(fill="x", pady=(6, 0))
        for chip_val in ["1000", "2500", "5000", "10000", "20000"]:
            ChipButton(
                chips0, text=f"৳{chip_val}", command=lambda v=chip_val: self._set_bdt(v),
                parent_bg=card_bg, width=48
            ).pack(side="left", padx=2)

        # Column 1: Item Rate
        col1 = tk.Frame(input_card, bg=card_bg)
        col1.grid(row=0, column=1, sticky="ew", padx=6)
        col1.grid_columnconfigure(0, weight=1)

        tk.Label(col1, text="💎 Item Rate (৳/$)", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(anchor="w", pady=(0, 4))
        self.item_rate_entry = tk.Entry(col1, font=FONTS["value_lg"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid")
        self.item_rate_entry.pack(fill="x", ipady=5)
        self.item_rate_entry.bind("<KeyRelease>", self._on_input_changed)

        chips1 = tk.Frame(col1, bg=card_bg)
        chips1.pack(fill="x", pady=(6, 0))
        for chip_val in ["118", "120", "121", "122"]:
            ChipButton(
                chips1, text=chip_val, command=lambda v=chip_val: self._set_item_rate(v),
                parent_bg=card_bg, width=44
            ).pack(side="left", padx=2)

        # Column 2: Wallet Rate
        col2 = tk.Frame(input_card, bg=card_bg)
        col2.grid(row=0, column=2, sticky="ew", padx=6)
        col2.grid_columnconfigure(0, weight=1)

        tk.Label(col2, text="💼 Wallet Rate (৳/$)", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(anchor="w", pady=(0, 4))
        self.wallet_rate_entry = tk.Entry(col2, font=FONTS["value_lg"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid")
        self.wallet_rate_entry.pack(fill="x", ipady=5)
        self.wallet_rate_entry.bind("<KeyRelease>", self._on_input_changed)

        chips2 = tk.Frame(col2, bg=card_bg)
        chips2.pack(fill="x", pady=(6, 0))
        for chip_val in ["114", "116", "118", "120"]:
            ChipButton(
                chips2, text=chip_val, command=lambda v=chip_val: self._set_wallet_rate(v),
                parent_bg=card_bg, width=44
            ).pack(side="left", padx=2)

        # Mode Selection Row
        mode_strip = tk.Frame(input_card, bg=card_bg)
        mode_strip.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(14, 0))

        tk.Label(mode_strip, text="MFS Fee Mode:", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left", padx=(0, 10))

        for mode_id, mode_label in [
            ("none", "Direct (No Fee)"),
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
            rb.pack(side="left", padx=6)

        ModernButton(
            mode_strip,
            text="⚡ Calculate",
            command=self.calculate,
            width=120,
            height=32,
            bg_color=success,
            parent_bg=card_bg,
            font=FONTS["body_bold"],
        ).pack(side="right")

        # ----------------- Results Grid -----------------
        results_grid = tk.Frame(self, bg=bg)
        results_grid.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        results_grid.grid_columnconfigure((0, 1), weight=1, uniform="reverse_results")
        results_grid.grid_rowconfigure(0, weight=1)

        # Card 1: Skins you can buy
        self.item_card = self._build_result_card(
            results_grid, col=0, title="💎 CS2 Skin Purchase Power",
            subtitle="Skin equivalent at current item rate", accent=primary,
            keys=["USD Skin Value ($)", "Net BDT Used", "Fee Deducted", "Steam Market Listing Price"]
        )

        # Card 2: Wallet you can buy
        self.wallet_card = self._build_result_card(
            results_grid, col=1, title="💼 Steam Wallet Balance Power",
            subtitle="Wallet equivalent at current wallet rate", accent=purple,
            keys=["USD Wallet Value ($)", "Net BDT Used", "Fee Deducted", "Extra USD vs Item"]
        )

    def _build_result_card(self, master, col: int, title: str, subtitle: str, accent: str, keys: list[str]):
        card_bg = self.theme.get("bg_card", "#161f30")
        inner_bg = self.theme.get("bg_card_inner", "#1d293d")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#94a3b8")

        card = tk.Frame(master, bg=card_bg, bd=1, relief="solid")
        card.grid(row=0, column=col, sticky="nsew", padx=6)
        card.grid_columnconfigure(0, weight=1)

        banner = tk.Frame(card, bg=accent, padx=14, pady=10)
        banner.pack(fill="x")

        tk.Label(banner, text=title, font=FONTS["h2"], bg=accent, fg="#ffffff").pack(anchor="w")
        tk.Label(banner, text=subtitle, font=FONTS["small"], bg=accent, fg="#e0f2fe").pack(anchor="w")

        body = tk.Frame(card, bg=card_bg, padx=12, pady=12)
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
            row.pack(fill="x", pady=5)
            rows[key] = row
        return rows

    def _on_copy_feedback(self, msg: str):
        if self.on_status:
            self.on_status(f"✓ {msg}", self.theme.get("success", "#10b981"))

    def _set_bdt(self, val: str):
        self.bdt_entry.delete(0, tk.END)
        self.bdt_entry.insert(0, val)
        self.calculate()

    def _set_item_rate(self, val: str):
        self.item_rate_entry.delete(0, tk.END)
        self.item_rate_entry.insert(0, val)
        self.calculate()

    def _set_wallet_rate(self, val: str):
        self.wallet_rate_entry.delete(0, tk.END)
        self.wallet_rate_entry.insert(0, val)
        self.calculate()

    def _on_input_changed(self, _event=None):
        if not self.config.get("live_calc", True):
            return
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(150, self.calculate)

    def reset_to_defaults(self):
        default_item = self.config.get("default_item_rate", 120.0)
        default_wallet = self.config.get("default_wallet_rate", 118.0)
        self.item_rate_entry.delete(0, tk.END)
        self.item_rate_entry.insert(0, str(default_item))
        self.wallet_rate_entry.delete(0, tk.END)
        self.wallet_rate_entry.insert(0, str(default_wallet))

    def calculate(self):
        try:
            bdt_val = clean_input(self.bdt_entry.get())
            if bdt_val is None:
                for group in (self.item_card, self.wallet_card):
                    for row in group.values():
                        row.set_value("-", is_active=False)
                return

            item_rate = clean_input(self.item_rate_entry.get())
            wallet_rate = clean_input(self.wallet_rate_entry.get())
            mode = self.fee_mode_var.get()
            use_comma = self.config.get("use_comma_bdt", False)
            sym = self.config.get("currency_symbol", TAKA)

            # Item calculation
            item_usd = 0.0
            if item_rate:
                res_it = calculate_reverse(bdt_val, item_rate, fee_mode=mode)
                item_usd = res_it["usd_value"]
                self.item_card["USD Skin Value ($)"].set_value(format_usd(item_usd))
                self.item_card["Net BDT Used"].set_value(format_bdt(res_it["net_bdt"], sym, use_comma))
                self.item_card["Fee Deducted"].set_value(format_bdt(res_it["fee_amount"], sym, use_comma))

                # What should buyer list item on Steam for to receive item_usd?
                cents = int(round(item_usd * 100))
                buyer_cents, _, _ = steam_calc_seller_receives(cents)
                self.item_card["Steam Market Listing Price"].set_value(format_usd(buyer_cents / 100.0))
            else:
                for row in self.item_card.values():
                    row.set_value("Enter item rate", is_active=False)

            # Wallet calculation
            wallet_usd = 0.0
            if wallet_rate:
                res_wt = calculate_reverse(bdt_val, wallet_rate, fee_mode=mode)
                wallet_usd = res_wt["usd_value"]
                self.wallet_card["USD Wallet Value ($)"].set_value(format_usd(wallet_usd))
                self.wallet_card["Net BDT Used"].set_value(format_bdt(res_wt["net_bdt"], sym, use_comma))
                self.wallet_card["Fee Deducted"].set_value(format_bdt(res_wt["fee_amount"], sym, use_comma))

                if item_usd > 0:
                    diff_usd = wallet_usd - item_usd
                    if diff_usd > 0:
                        self.wallet_card["Extra USD vs Item"].set_value(f"+{format_usd(diff_usd)}")
                    else:
                        self.wallet_card["Extra USD vs Item"].set_value(format_usd(diff_usd))
                else:
                    self.wallet_card["Extra USD vs Item"].set_value("-")
            else:
                for row in self.wallet_card.values():
                    row.set_value("Enter wallet rate", is_active=False)

            if self.on_status:
                self.on_status(f"✓ Reverse calculated for {format_bdt(bdt_val, sym, use_comma)}", self.theme.get("success", "#10b981"))
        except ValueError as exc:
            if self.on_status:
                self.on_status(str(exc), self.theme.get("danger", "#ef4444"))
