"""
Standard Calculator Tab:
Calculates CS2 item transfer, Steam wallet conversion, and MFS cashout options.
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
    calculate_full_quote,
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
        super().__init__(master, bg=theme.get("bg_app", "#0b0f17"))
        self.config = config
        self.theme = theme
        self.on_quote_change = on_quote_change
        self.on_status = on_status
        self.latest_quote: Optional[Dict[str, Any]] = None
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
        success = self.theme.get("success", "#10b981")
        border = self.theme.get("border", "#243247")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ----------------- Top Input Card -----------------
        input_card = tk.Frame(self, bg=card_bg, padx=16, pady=14, bd=1, relief="solid")
        input_card.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 10))
        input_card.grid_columnconfigure((0, 1, 2), weight=1, uniform="inputs")

        # Column 0: Amount
        col0 = tk.Frame(input_card, bg=card_bg)
        col0.grid(row=0, column=0, sticky="ew", padx=6)
        col0.grid_columnconfigure(0, weight=1)

        header0 = tk.Frame(col0, bg=card_bg)
        header0.pack(fill="x", pady=(0, 4))
        tk.Label(header0, text="💵 Amount ($)", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left")
        tk.Label(header0, text="USD", font=FONTS["badge"], bg="#10b981", fg="#ffffff", padx=6, pady=1).pack(side="right")

        self.amount_entry = tk.Entry(
            col0, font=FONTS["value_lg"], bg=input_bg, fg=text_main,
            insertbackground=text_main, bd=1, relief="solid"
        )
        self.amount_entry.pack(fill="x", ipady=5)
        self.amount_entry.bind("<KeyRelease>", self._on_input_changed)

        # Amount Preset Chips
        chips0 = tk.Frame(col0, bg=card_bg)
        chips0.pack(fill="x", pady=(6, 0))
        for chip_val in ["10", "25", "50", "100", "200"]:
            ChipButton(
                chips0, text=f"${chip_val}", command=lambda v=chip_val: self._set_amount(v),
                parent_bg=card_bg, width=44
            ).pack(side="left", padx=2)

        # Column 1: Item Rate
        col1 = tk.Frame(input_card, bg=card_bg)
        col1.grid(row=0, column=1, sticky="ew", padx=6)
        col1.grid_columnconfigure(0, weight=1)

        header1 = tk.Frame(col1, bg=card_bg)
        header1.pack(fill="x", pady=(0, 4))
        tk.Label(header1, text="💎 Item Transfer Rate", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left")
        tk.Label(header1, text="৳/$", font=FONTS["badge"], bg=primary, fg="#ffffff", padx=6, pady=1).pack(side="right")

        self.item_rate_entry = tk.Entry(
            col1, font=FONTS["value_lg"], bg=input_bg, fg=text_main,
            insertbackground=text_main, bd=1, relief="solid"
        )
        self.item_rate_entry.pack(fill="x", ipady=5)
        self.item_rate_entry.bind("<KeyRelease>", self._on_input_changed)

        # Item Rate Preset Chips
        chips1 = tk.Frame(col1, bg=card_bg)
        chips1.pack(fill="x", pady=(6, 0))
        for chip_val in ["118", "120", "121", "122", "125"]:
            ChipButton(
                chips1, text=chip_val, command=lambda v=chip_val: self._set_item_rate(v),
                parent_bg=card_bg, width=44
            ).pack(side="left", padx=2)

        # Column 2: Wallet Rate
        col2 = tk.Frame(input_card, bg=card_bg)
        col2.grid(row=0, column=2, sticky="ew", padx=6)
        col2.grid_columnconfigure(0, weight=1)

        header2 = tk.Frame(col2, bg=card_bg)
        header2.pack(fill="x", pady=(0, 4))
        tk.Label(header2, text="💼 Wallet Transfer Rate", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left")
        tk.Label(header2, text="৳/$", font=FONTS["badge"], bg=self.theme.get("purple", "#8b5cf6"), fg="#ffffff", padx=6, pady=1).pack(side="right")

        self.wallet_rate_entry = tk.Entry(
            col2, font=FONTS["value_lg"], bg=input_bg, fg=text_main,
            insertbackground=text_main, bd=1, relief="solid"
        )
        self.wallet_rate_entry.pack(fill="x", ipady=5)
        self.wallet_rate_entry.bind("<KeyRelease>", self._on_input_changed)

        # Wallet Rate Preset Chips
        chips2 = tk.Frame(col2, bg=card_bg)
        chips2.pack(fill="x", pady=(6, 0))
        for chip_val in ["114", "116", "118", "120", "122"]:
            ChipButton(
                chips2, text=chip_val, command=lambda v=chip_val: self._set_wallet_rate(v),
                parent_bg=card_bg, width=44
            ).pack(side="left", padx=2)

        # ----------------- Middle Action Strip -----------------
        action_strip = tk.Frame(input_card, bg=card_bg)
        action_strip.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        action_strip.grid_columnconfigure(0, weight=1)

        self.info_label = tk.Label(
            action_strip,
            text="💡 Tip: Enter Amount ($). Rates auto-fill from saved presets. Press Enter to calculate.",
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
            width=80,
            height=34,
            bg_color="#475569",
            parent_bg=card_bg,
            font=FONTS["small_bold"],
        ).pack(side="left", padx=(0, 8))

        ModernButton(
            btn_box,
            text="⚡ Calculate",
            command=self.calculate,
            width=130,
            height=34,
            bg_color=success,
            parent_bg=card_bg,
            font=FONTS["body_bold"],
        ).pack(side="left")

        # ----------------- Results Grid (3 Cards) -----------------
        results_grid = tk.Frame(self, bg=bg)
        results_grid.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        results_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="results")
        results_grid.grid_rowconfigure(0, weight=1)

        # Card 1: Item Transfer
        self.item_rows = self._build_result_card(
            results_grid,
            col=0,
            title="💎 Item Transfer",
            subtitle="CS2 skins / knife rate",
            accent=primary,
            keys=["Base Cost", "bKash Agent (+1.85%)", "bKash Priyo (+1.49%)", "Nagad App (+1.25%)", "Cash In Hand (-1.85%)"],
        )

        # Card 2: Wallet Transfer
        self.wallet_rows = self._build_result_card(
            results_grid,
            col=1,
            title="💼 Wallet Transfer",
            subtitle="Steam wallet balance rate",
            accent=self.theme.get("purple", "#8b5cf6"),
            keys=["Base Cost", "bKash Agent (+1.85%)", "bKash Priyo (+1.49%)", "Nagad App (+1.25%)", "Savings vs Item"],
        )

        # Card 3: Steam Market Fee
        self.steam_rows = self._build_result_card(
            results_grid,
            col=2,
            title="🏷️ Steam Market Tax",
            subtitle="Exact 15% CS2 Community Market",
            accent=self.theme.get("cyan", "#0891b2"),
            keys=["Buyer Pays (You Get $)", "Seller Gets (Buyer Pays $)", "Valve Fee (5%)", "Game Fee (10%)", "Effective BDT Cashout"],
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
        card_bg = self.theme.get("bg_card", "#161f30")
        inner_bg = self.theme.get("bg_card_inner", "#1d293d")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#94a3b8")

        card = tk.Frame(master, bg=card_bg, bd=1, relief="solid")
        card.grid(row=0, column=col, sticky="nsew", padx=6)
        card.grid_columnconfigure(0, weight=1)

        # Header with accent banner
        banner = tk.Frame(card, bg=accent, padx=14, pady=10)
        banner.pack(fill="x")

        tk.Label(banner, text=title, font=FONTS["h2"], bg=accent, fg="#ffffff").pack(anchor="w")
        tk.Label(banner, text=subtitle, font=FONTS["small"], bg=accent, fg="#e0f2fe").pack(anchor="w")

        # Body
        body = tk.Frame(card, bg=card_bg, padx=12, pady=10)
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

    def clear_fields(self):
        self.amount_entry.delete(0, tk.END)
        self.reset_to_defaults()
        for group in (self.item_rows, self.wallet_rows, self.steam_rows):
            for row in group.values():
                row.set_value("-", is_active=False)
        self.latest_quote = None
        if self.on_status:
            self.on_status("Ready. Enter amount to calculate.", self.theme.get("text_muted", "#94a3b8"))

    def set_inputs(self, amount: float, item_rate: Optional[float] = None, wallet_rate: Optional[float] = None):
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, str(amount))
        if item_rate is not None:
            self.item_rate_entry.delete(0, tk.END)
            self.item_rate_entry.insert(0, str(item_rate))
        if wallet_rate is not None:
            self.wallet_rate_entry.delete(0, tk.END)
            self.wallet_rate_entry.insert(0, str(wallet_rate))
        self.calculate()

    def calculate(self):
        try:
            amt_val = clean_input(self.amount_entry.get())
            if amt_val is None:
                for group in (self.item_rows, self.wallet_rows, self.steam_rows):
                    for row in group.values():
                        row.set_value("-", is_active=False)
                return

            item_rate = clean_input(self.item_rate_entry.get())
            wallet_rate = clean_input(self.wallet_rate_entry.get())
            custom_fee = float(self.config.get("custom_fee_pct", 1.85))
            use_comma = self.config.get("use_comma_bdt", False)
            sym = self.config.get("currency_symbol", TAKA)

            quote = calculate_full_quote(
                amount_usd=amt_val,
                item_rate=item_rate,
                wallet_rate=wallet_rate,
                custom_fee_pct=custom_fee,
            )
            self.latest_quote = quote

            # Update Item Card
            if quote["item"]:
                it = quote["item"]
                self.item_rows["Base Cost"].set_value(format_bdt(it["base_cost"], sym, use_comma))
                self.item_rows["bKash Agent (+1.85%)"].set_value(format_bdt(it["buyer_sends_agent"], sym, use_comma))
                self.item_rows["bKash Priyo (+1.49%)"].set_value(format_bdt(it["buyer_sends_priyo"], sym, use_comma))
                self.item_rows["Nagad App (+1.25%)"].set_value(format_bdt(it["buyer_sends_nagad"], sym, use_comma))
                self.item_rows["Cash In Hand (-1.85%)"].set_value(format_bdt(it["net_in_hand_agent"], sym, use_comma))
            else:
                for row in self.item_rows.values():
                    row.set_value("Enter item rate", is_active=False)

            # Update Wallet Card
            if quote["wallet"]:
                wt = quote["wallet"]
                self.wallet_rows["Base Cost"].set_value(format_bdt(wt["base_cost"], sym, use_comma))
                self.wallet_rows["bKash Agent (+1.85%)"].set_value(format_bdt(wt["buyer_sends_agent"], sym, use_comma))
                self.wallet_rows["bKash Priyo (+1.49%)"].set_value(format_bdt(wt["buyer_sends_priyo"], sym, use_comma))
                self.wallet_rows["Nagad App (+1.25%)"].set_value(format_bdt(wt["buyer_sends_nagad"], sym, use_comma))
                if quote["savings"]:
                    diff = quote["savings"]["diff_base"]
                    if diff > 0:
                        self.wallet_rows["Savings vs Item"].set_value(f"Save {format_bdt(diff, sym, use_comma)}")
                    elif diff < 0:
                        self.wallet_rows["Savings vs Item"].set_value(f"+{format_bdt(abs(diff), sym, use_comma)} more")
                    else:
                        self.wallet_rows["Savings vs Item"].set_value("Equal rate")
            else:
                for row in self.wallet_rows.values():
                    row.set_value("Enter wallet rate", is_active=False)

            # Update Steam Tax Card
            st = quote["steam"]
            self.steam_rows["Buyer Pays (You Get $)"].set_value(format_usd(st["buyer_pays_when_you_receive"]))
            self.steam_rows["Seller Gets (Buyer Pays $)"].set_value(format_usd(st["seller_receives_when_buyer_pays"]))
            self.steam_rows["Valve Fee (5%)"].set_value(format_usd(st["valve_fee_when_buyer_pays"]))
            self.steam_rows["Game Fee (10%)"].set_value(format_usd(st["game_fee_when_buyer_pays"]))

            if wallet_rate:
                net_wallet_bdt = st["seller_receives_when_buyer_pays"] * wallet_rate
                self.steam_rows["Effective BDT Cashout"].set_value(format_bdt(net_wallet_bdt, sym, use_comma))
            else:
                self.steam_rows["Effective BDT Cashout"].set_value("-")

            # Record in history
            self.config.add_history_entry({
                "amount_usd": amt_val,
                "item_rate": item_rate,
                "wallet_rate": wallet_rate,
            })

            if self.on_quote_change:
                self.on_quote_change(quote)

            if self.on_status:
                self.on_status(f"✓ Calculated for {format_usd(amt_val)}", self.theme.get("success", "#10b981"))
        except ValueError as exc:
            if self.on_status:
                self.on_status(str(exc), self.theme.get("danger", "#ef4444"))
