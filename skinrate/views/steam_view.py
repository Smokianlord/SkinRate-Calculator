"""
Steam Market & Skin Flip Profit Tab:
Exact 15% Steam Community Market breakdown and skin flipping profit / ROI calculator.
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
    calculate_steam_market_details,
    calculate_steam_trade_profit,
    TAKA,
)


class SteamView(tk.Frame):
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
        self._debounce_id = None

        self._build_ui()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0b0f17")
        card_bg = self.theme.get("bg_card", "#161f30")
        inner_bg = self.theme.get("bg_card_inner", "#1d293d")
        input_bg = self.theme.get("bg_input", "#0f1724")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#94a3b8")
        cyan = self.theme.get("cyan", "#0891b2")
        amber = self.theme.get("amber", "#f59e0b")
        success = self.theme.get("success", "#10b981")

        self.grid_columnconfigure((0, 1), weight=1, uniform="steam_cols")
        self.grid_rowconfigure(0, weight=1)

        # ----------------- Left Panel: Exact Steam Fee Breakdown -----------------
        left_card = tk.Frame(self, bg=card_bg, padx=16, pady=14, bd=1, relief="solid")
        left_card.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=12)

        banner_l = tk.Frame(left_card, bg=cyan, padx=12, pady=8)
        banner_l.pack(fill="x", pady=(0, 12))
        tk.Label(banner_l, text="🏷️ Steam Market Fee Calculator", font=FONTS["h2"], bg=cyan, fg="#ffffff").pack(anchor="w")
        tk.Label(banner_l, text="Valve 5% + CS2 10% exact cent rounding", font=FONTS["small"], bg=cyan, fg="#e0f2fe").pack(anchor="w")

        # Input
        tk.Label(left_card, text="Item Amount ($)", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(anchor="w", pady=(0, 4))
        self.fee_entry = tk.Entry(left_card, font=FONTS["value_lg"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid")
        self.fee_entry.pack(fill="x", ipady=5)
        self.fee_entry.bind("<KeyRelease>", self._on_input_changed)

        chips_l = tk.Frame(left_card, bg=card_bg)
        chips_l.pack(fill="x", pady=(6, 12))
        for val in ["5", "10", "25", "50", "100"]:
            ChipButton(chips_l, text=f"${val}", command=lambda v=val: self._set_fee_input(v), parent_bg=card_bg, width=44).pack(side="left", padx=2)

        # Result Rows for Fee Breakdown
        self.fee_rows = {}
        for key in [
            "If Buyer Pays $X -> Seller Gets",
            "Valve Fee (5%)",
            "CS2 Game Fee (10%)",
            "Total Steam Fee Deducted",
            "If You Want $X -> Buyer Must Pay",
            "Total Added Tax",
        ]:
            row = ResultRow(
                left_card, title=key, accent_color=cyan, bg=inner_bg, text_color=text_main,
                muted_color=text_muted, on_copy_feedback=self._on_copy_feedback
            )
            row.pack(fill="x", pady=4)
            self.fee_rows[key] = row

        # ----------------- Right Panel: CS2 Skin Flip & Profit -----------------
        right_card = tk.Frame(self, bg=card_bg, padx=16, pady=14, bd=1, relief="solid")
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=12)

        banner_r = tk.Frame(right_card, bg=amber, padx=12, pady=8)
        banner_r.pack(fill="x", pady=(0, 12))
        tk.Label(banner_r, text="📈 CS2 Skin Flip & ROI Calculator", font=FONTS["h2"], bg=amber, fg="#ffffff").pack(anchor="w")
        tk.Label(banner_r, text="Buy price vs Steam sell price profit margin", font=FONTS["small"], bg=amber, fg="#fef3c7").pack(anchor="w")

        # Inputs
        flip_inputs = tk.Frame(right_card, bg=card_bg)
        flip_inputs.pack(fill="x", pady=(0, 10))
        flip_inputs.grid_columnconfigure((0, 1, 2), weight=1)

        tk.Label(flip_inputs, text="Buy Price ($):", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=0, column=0, sticky="w")
        self.buy_entry = tk.Entry(flip_inputs, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid", width=10)
        self.buy_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6), ipady=4)
        self.buy_entry.bind("<KeyRelease>", self._on_input_changed)

        tk.Label(flip_inputs, text="Sell on Steam ($):", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=0, column=1, sticky="w")
        self.sell_entry = tk.Entry(flip_inputs, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid", width=10)
        self.sell_entry.grid(row=1, column=1, sticky="ew", padx=(0, 6), ipady=4)
        self.sell_entry.bind("<KeyRelease>", self._on_input_changed)

        tk.Label(flip_inputs, text="Cashout Rate (৳/$):", font=FONTS["body_bold"], bg=card_bg, fg=text_main).grid(row=0, column=2, sticky="w")
        self.cashout_entry = tk.Entry(flip_inputs, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, bd=1, relief="solid", width=10)
        self.cashout_entry.grid(row=1, column=2, sticky="ew", ipady=4)
        self.cashout_entry.insert(0, str(self.config.get("default_wallet_rate", 118.0)))
        self.cashout_entry.bind("<KeyRelease>", self._on_input_changed)

        # Result Rows for Flip Profit
        self.flip_rows = {}
        for key in [
            "Net Wallet Received ($)",
            "Steam Fee Paid ($)",
            "Net Profit ($)",
            "Net Profit (৳)",
            "Return on Investment (ROI)",
        ]:
            row = ResultRow(
                right_card, title=key, accent_color=amber, bg=inner_bg, text_color=text_main,
                muted_color=text_muted, on_copy_feedback=self._on_copy_feedback
            )
            row.pack(fill="x", pady=4)
            self.flip_rows[key] = row

        # Set default values for initial view
        self.fee_entry.insert(0, "50")
        self.buy_entry.insert(0, "40")
        self.sell_entry.insert(0, "55")
        self.calculate()

    def _on_copy_feedback(self, msg: str):
        if self.on_status:
            self.on_status(f"✓ {msg}", self.theme.get("success", "#10b981"))

    def _set_fee_input(self, val: str):
        self.fee_entry.delete(0, tk.END)
        self.fee_entry.insert(0, val)
        self.calculate()

    def _on_input_changed(self, _event=None):
        if not self.config.get("live_calc", True):
            return
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(150, self.calculate)

    def calculate(self):
        try:
            # 1. Left Panel Calculation
            fee_amt = clean_input(self.fee_entry.get())
            if fee_amt is not None:
                st = calculate_steam_market_details(fee_amt)
                self.fee_rows["If Buyer Pays $X -> Seller Gets"].set_value(format_usd(st["seller_receives_when_buyer_pays"]))
                self.fee_rows["Valve Fee (5%)"].set_value(format_usd(st["valve_fee_when_buyer_pays"]))
                self.fee_rows["CS2 Game Fee (10%)"].set_value(format_usd(st["game_fee_when_buyer_pays"]))
                total_ded = fee_amt - st["seller_receives_when_buyer_pays"]
                self.fee_rows["Total Steam Fee Deducted"].set_value(format_usd(total_ded))

                self.fee_rows["If You Want $X -> Buyer Must Pay"].set_value(format_usd(st["buyer_pays_when_you_receive"]))
                total_add = st["buyer_pays_when_you_receive"] - fee_amt
                self.fee_rows["Total Added Tax"].set_value(format_usd(total_add))
            else:
                for r in self.fee_rows.values():
                    r.set_value("-", is_active=False)

            # 2. Right Panel Calculation
            buy_val = clean_input(self.buy_entry.get())
            sell_val = clean_input(self.sell_entry.get())
            rate_val = clean_input(self.cashout_entry.get()) or 118.0
            use_comma = self.config.get("use_comma_bdt", False)
            sym = self.config.get("currency_symbol", TAKA)

            if buy_val is not None and sell_val is not None:
                profit = calculate_steam_trade_profit(buy_val, sell_val, rate_val)
                self.flip_rows["Net Wallet Received ($)"].set_value(format_usd(profit["wallet_received_usd"]))
                self.flip_rows["Steam Fee Paid ($)"].set_value(format_usd(profit["steam_fee_usd"]))

                p_usd = profit["net_profit_usd"]
                p_bdt = profit["profit_bdt"]
                roi = profit["roi_pct"]

                sign = "+" if p_usd >= 0 else ""
                self.flip_rows["Net Profit ($)"].set_value(f"{sign}{format_usd(p_usd)}")
                self.flip_rows["Net Profit (৳)"].set_value(f"{sign}{format_bdt(p_bdt, sym, use_comma)}")
                self.flip_rows["Return on Investment (ROI)"].set_value(f"{sign}{roi:.2f}%")
            else:
                for r in self.flip_rows.values():
                    r.set_value("-", is_active=False)

        except ValueError as exc:
            if self.on_status:
                self.on_status(str(exc), self.theme.get("danger", "#ef4444"))
