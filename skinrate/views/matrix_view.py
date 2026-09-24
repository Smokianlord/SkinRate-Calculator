"""
Rate Matrix / Quick Cheat Sheet Tab:
Interactive matrix of common CS2 trading amounts ($1 to $1000) with 1-click table export.
Clean, modern aesthetic with zero clutter.
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
    calculate_quote,
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
        super().__init__(master, bg=theme.get("bg_app", "#0f131c"))
        self.config = config
        self.theme = theme
        self.on_status = on_status

        self._build_ui()
        self.recalculate()

    def _build_ui(self):
        bg = self.theme.get("bg_app", "#0f131c")
        card_bg = self.theme.get("bg_card", "#181e2b")
        input_bg = self.theme.get("bg_input", "#111622")
        text_main = self.theme.get("text_main", "#f8fafc")
        text_muted = self.theme.get("text_muted", "#8593a8")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ----------------- Top Rate Controls -----------------
        ctrl_card = tk.Frame(self, bg=card_bg, padx=16, pady=10, bd=1, relief="solid")
        ctrl_card.grid(row=0, column=0, sticky="ew", padx=20, pady=(12, 10))

        tk.Label(ctrl_card, text="Rate Cheat Sheet Matrix", font=FONTS["h2"], bg=card_bg, fg=text_main).pack(side="left")

        # Rate input
        tk.Label(ctrl_card, text="Rate (৳/$):", font=FONTS["body_bold"], bg=card_bg, fg=text_muted).pack(side="left", padx=(24, 6))
        self.rate_entry = tk.Entry(ctrl_card, font=FONTS["body"], bg=input_bg, fg=text_main, insertbackground=text_main, width=8, bd=1, relief="solid")
        self.rate_entry.pack(side="left")
        self.rate_entry.insert(0, str(self.config.get("default_rate", 85.0)))
        self.rate_entry.bind("<KeyRelease>", lambda _e: self.recalculate())

        ModernButton(
            ctrl_card,
            text="📋 Copy Table",
            command=self.copy_table,
            width=110,
            height=28,
            bg_color="#2563eb",
            parent_bg=card_bg,
            font=FONTS["small_bold"],
        ).pack(side="right")

        # ----------------- Treeview / Table -----------------
        table_frame = tk.Frame(self, bg=card_bg, padx=10, pady=10, bd=1, relief="solid")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 14))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Matrix.Treeview",
            background=input_bg,
            foreground=text_main,
            fieldbackground=input_bg,
            rowheight=25,
            font=FONTS["small"],
        )
        style.configure(
            "Matrix.Treeview.Heading",
            background=shade(card_bg, 10),
            foreground=text_main,
            font=FONTS["small_bold"],
            relief="flat",
        )
        style.map("Matrix.Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "#ffffff")])

        columns = ("usd", "cost_base", "agent_cost", "priyo_cost", "nagad_cost", "with_tax", "without_tax")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Matrix.Treeview")

        self.tree.heading("usd", text="USD Amount")
        self.tree.heading("cost_base", text="Cost (Base ৳)")
        self.tree.heading("agent_cost", text="bKash Agent (+1.85%)")
        self.tree.heading("priyo_cost", text="bKash Priyo (+1.49%)")
        self.tree.heading("nagad_cost", text="Nagad App (+1.25%)")
        self.tree.heading("with_tax", text="With 15% Tax ($)")
        self.tree.heading("without_tax", text="Without 15% Tax ($)")

        for col in columns:
            self.tree.column(col, anchor="center", width=130)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def recalculate(self):
        try:
            rate = clean_input(self.rate_entry.get()) or 85.0
            use_comma = self.config.get("use_comma_bdt", False)
            sym = self.config.get("currency_symbol", TAKA)

            for item in self.tree.get_children():
                self.tree.delete(item)

            for amt in AMOUNTS:
                q = calculate_quote(amt, rate)
                row = (
                    format_usd(amt),
                    format_bdt(q["base_cost"], sym, use_comma),
                    format_bdt(q["agent_cost"], sym, use_comma),
                    format_bdt(q["priyo_cost"], sym, use_comma),
                    format_bdt(q["nagad_cost"], sym, use_comma),
                    format_usd(q["with_15_tax"]),
                    format_usd(q["without_15_tax"]),
                )
                self.tree.insert("", "end", values=row)

        except ValueError:
            pass

    def copy_table(self):
        try:
            rate = clean_input(self.rate_entry.get()) or 85.0
            use_comma = self.config.get("use_comma_bdt", False)
            sym = self.config.get("currency_symbol", TAKA)

            lines = [
                f"=== CS2 SKINRATE CHEAT SHEET (Rate: {format_bdt(rate, sym, use_comma)}/$) ===",
                f"{'USD':<8} | {'Cost':<10} | {'bKash Agent':<12} | {'bKash Priyo':<12} | {'Nagad':<10} | {'+15% Tax':<10} | {'-15% Tax':<10}",
                "-" * 85,
            ]

            for amt in AMOUNTS:
                q = calculate_quote(amt, rate)
                lines.append(
                    f"{format_usd(amt):<8} | {format_bdt(q['base_cost'], sym, use_comma):<10} | {format_bdt(q['agent_cost'], sym, use_comma):<12} | {format_bdt(q['priyo_cost'], sym, use_comma):<12} | {format_bdt(q['nagad_cost'], sym, use_comma):<10} | {format_usd(q['with_15_tax']):<10} | {format_usd(q['without_15_tax']):<10}"
                )

            table_text = "\n".join(lines)
            self.clipboard_clear()
            self.clipboard_append(table_text)
            self.update()
            if self.on_status:
                self.on_status("✓ Copied cheat sheet table to clipboard!", self.theme.get("success", "#10b981"))
        except Exception as exc:
            if self.on_status:
                self.on_status(str(exc), self.theme.get("danger", "#f43f5e"))
