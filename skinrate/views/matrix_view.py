"""
Rate Matrix / Quick Cheat Sheet Tab:
Interactive matrix of common CS2 trading amounts ($1 to $1000) with 1-click table export.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any
from skinrate.theme import FONTS, shade
from skinrate.widgets import ModernButton
from skinrate.engine import (
    clean_input,
    format_bdt,
    format_usd,
    calculate_full_quote,
    TAKA,
)

AMOUNTS = [1.0, 2.5, 5.0, 10.0, 15.0, 20.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0, 250.0, 500.0, 1000.0]


class MatrixView(tk.Frame):
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

        self._build_ui()
        self.recalculate()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0b0f17")
        card_bg = self.theme.get("bg_card", "#161f30")
        input_bg = self.theme.get("bg_input", "#0f1724")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#94a3b8")
        primary = self.theme.get("primary", "#3b82f6")
        purple = self.theme.get("purple", "#8b5cf6")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ----------------- Top Rate Controls -----------------
        ctrl_card = tk.Frame(self, bg=card_bg, padx=16, pady=10, bd=1, relief="solid")
        ctrl_card.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 10))

        tk.Label(ctrl_card, text="📊 Rate Cheat Sheet Matrix", font=FONTS["h2"], bg=card_bg, fg=text_main).pack(side="left")

        # Item rate input
        tk.Label(ctrl_card, text="Item Rate:", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left", padx=(20, 6))
        self.item_entry = tk.Entry(ctrl_card, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, width=8, bd=1, relief="solid")
        self.item_entry.pack(side="left")
        self.item_entry.insert(0, str(self.config.get("default_item_rate", 120.0)))
        self.item_entry.bind("<KeyRelease>", lambda _e: self.recalculate())

        # Wallet rate input
        tk.Label(ctrl_card, text="Wallet Rate:", font=FONTS["body_bold"], bg=card_bg, fg=text_main).pack(side="left", padx=(16, 6))
        self.wallet_entry = tk.Entry(ctrl_card, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, width=8, bd=1, relief="solid")
        self.wallet_entry.pack(side="left")
        self.wallet_entry.insert(0, str(self.config.get("default_wallet_rate", 118.0)))
        self.wallet_entry.bind("<KeyRelease>", lambda _e: self.recalculate())

        ModernButton(
            ctrl_card,
            text="📋 Copy Table",
            command=self.copy_table,
            width=130,
            height=32,
            bg_color=primary,
            parent_bg=card_bg,
            font=FONTS["small_bold"],
        ).pack(side="right")

        # ----------------- Treeview / Table -----------------
        table_frame = tk.Frame(self, bg=card_bg, padx=12, pady=12, bd=1, relief="solid")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Style Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Matrix.Treeview",
            background=input_bg,
            foreground=text_main,
            fieldbackground=input_bg,
            rowheight=26,
            font=FONTS["small"],
        )
        style.configure(
            "Matrix.Treeview.Heading",
            background=shade(card_bg, 15),
            foreground=text_main,
            font=FONTS["small_bold"],
            relief="flat",
        )
        style.map("Matrix.Treeview", background=[("selected", primary)], foreground=[("selected", "#ffffff")])

        columns = ("usd", "item_base", "item_agent", "wallet_base", "wallet_agent", "steam_buyer", "steam_seller")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Matrix.Treeview")

        self.tree.heading("usd", text="USD Amount")
        self.tree.heading("item_base", text="Item Cost")
        self.tree.heading("item_agent", text="Item (bKash Agent)")
        self.tree.heading("wallet_base", text="Wallet Cost")
        self.tree.heading("wallet_agent", text="Wallet (bKash Agent)")
        self.tree.heading("steam_buyer", text="Steam Buyer Pays")
        self.tree.heading("steam_seller", text="Steam Seller Gets")

        for col in columns:
            self.tree.column(col, anchor="center", width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def recalculate(self):
        try:
            item_r = clean_input(self.item_entry.get()) or 120.0
            wallet_r = clean_input(self.wallet_entry.get()) or 118.0
            use_comma = self.config.get("use_comma_bdt", False)
            sym = self.config.get("currency_symbol", TAKA)

            for item in self.tree.get_children():
                self.tree.delete(item)

            for amt in AMOUNTS:
                quote = calculate_full_quote(amt, item_r, wallet_r)
                it = quote["item"]
                wt = quote["wallet"]
                st = quote["steam"]

                row = (
                    format_usd(amt),
                    format_bdt(it["base_cost"], sym, use_comma),
                    format_bdt(it["buyer_sends_agent"], sym, use_comma),
                    format_bdt(wt["base_cost"], sym, use_comma),
                    format_bdt(wt["buyer_sends_agent"], sym, use_comma),
                    format_usd(st["buyer_pays_when_you_receive"]),
                    format_usd(st["seller_receives_when_buyer_pays"]),
                )
                self.tree.insert("", "end", values=row)

        except ValueError:
            pass

    def copy_table(self):
        try:
            item_r = clean_input(self.item_entry.get()) or 120.0
            wallet_r = clean_input(self.wallet_entry.get()) or 118.0
            use_comma = self.config.get("use_comma_bdt", False)
            sym = self.config.get("currency_symbol", TAKA)

            lines = [
                f"=== CS2 SKINRATE CHEAT SHEET (Item: {format_bdt(item_r, sym, use_comma)} | Wallet: {format_bdt(wallet_r, sym, use_comma)}) ===",
                f"{'USD':<8} | {'Item Cost':<10} | {'bKash Agent':<12} | {'Wallet Cost':<12} | {'Steam Seller':<12}",
                "-" * 65,
            ]

            for amt in AMOUNTS:
                quote = calculate_full_quote(amt, item_r, wallet_r)
                it = quote["item"]
                wt = quote["wallet"]
                st = quote["steam"]
                lines.append(
                    f"{format_usd(amt):<8} | {format_bdt(it['base_cost'], sym, use_comma):<10} | {format_bdt(it['buyer_sends_agent'], sym, use_comma):<12} | {format_bdt(wt['base_cost'], sym, use_comma):<12} | {format_usd(st['seller_receives_when_buyer_pays']):<12}"
                )

            table_text = "\n".join(lines)
            self.clipboard_clear()
            self.clipboard_append(table_text)
            self.update()
            if self.on_status:
                self.on_status("✓ Copied cheat sheet table to clipboard!", self.theme.get("success", "#10b981"))
        except Exception as exc:
            if self.on_status:
                self.on_status(str(exc), self.theme.get("danger", "#ef4444"))
