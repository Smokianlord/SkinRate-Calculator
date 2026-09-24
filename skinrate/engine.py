"""
SkinRate Calculation Engine
Streamlined, high-precision math for CS2 skins and Steam wallet transfers,
Bangladeshi MFS cashout options, 15% Steam tax, and reverse conversions.
"""

from __future__ import annotations
import math
from typing import Dict, Any, Optional

TAKA = "\u09F3"
BANGLA_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

# Standard Bangladesh Mobile Financial Services (MFS) Cashout Percentages
BKASH_AGENT_FEE_PCT = 1.85      # 18.5 Tk per 1000 Tk (1.85%)
BKASH_PRIYO_APP_FEE_PCT = 1.49  # 14.9 Tk per 1000 Tk (1.49%)
NAGAD_APP_FEE_PCT = 1.25        # 12.5 Tk per 1000 Tk (1.25%)


def clean_input(raw: str) -> Optional[float]:
    """
    Sanitize and parse user input number.
    Supports Bangla digits, comma separation, currency symbols ($ and ৳),
    and common suffixes ('tk', 'bdt').
    Returns float if valid, None if empty, or raises ValueError if invalid.
    """
    if raw is None:
        return None
    cleaned = raw.strip().translate(BANGLA_DIGITS)
    for token in (",", "$", TAKA, "tk", "TK", "Tk", "tK", "bdt", "BDT"):
        cleaned = cleaned.replace(token, "")
    cleaned = cleaned.strip()

    if not cleaned:
        return None

    try:
        val = float(cleaned)
    except ValueError as exc:
        raise ValueError(f"'{raw.strip()}' is not a valid number.") from exc

    if val <= 0:
        raise ValueError("Amount must be greater than 0.")
    if math.isnan(val) or math.isinf(val):
        raise ValueError("Amount is invalid.")
    return val


def format_bdt(val: float, symbol: str = TAKA, use_comma: bool = False) -> str:
    """Format Bangladeshi Taka. Default is no commas (e.g. ৳850) per community standard."""
    rounded = int(round(val))
    if use_comma:
        return f"{symbol}{rounded:,}"
    return f"{symbol}{rounded}"


def format_usd(val: float) -> str:
    """Format USD currency."""
    return f"${val:,.2f}"


def calculate_quote(
    amount_usd: float,
    rate: float,
    custom_fee_pct: float = BKASH_AGENT_FEE_PCT,
) -> Dict[str, Any]:
    """
    Unified calculation for CS2 skins & Steam wallet transfer + 15% Steam tax.
    """
    base_cost = amount_usd * rate

    # Cashout amounts
    agent_cost = base_cost * (1 + BKASH_AGENT_FEE_PCT / 100.0)
    priyo_cost = base_cost * (1 + BKASH_PRIYO_APP_FEE_PCT / 100.0)
    nagad_cost = base_cost * (1 + NAGAD_APP_FEE_PCT / 100.0)
    custom_cost = base_cost * (1 + custom_fee_pct / 100.0)

    # 15% Steam Tax (Unified)
    with_15_tax = round(amount_usd * 1.15, 2)
    without_15_tax = round(amount_usd * 0.85, 2)

    return {
        "amount_usd": amount_usd,
        "rate": rate,
        "base_cost": base_cost,
        "agent_cost": agent_cost,
        "priyo_cost": priyo_cost,
        "nagad_cost": nagad_cost,
        "custom_cost": custom_cost,
        "with_15_tax": with_15_tax,
        "without_15_tax": without_15_tax,
    }


def calculate_reverse(
    bdt_amount: float,
    rate: float,
    fee_mode: str = "none",  # 'none', 'agent', 'priyo', 'nagad'
) -> Dict[str, Any]:
    """
    Reverse calculate USD value from a BDT budget.
    """
    fee_pct = 0.0
    if fee_mode == "agent":
        fee_pct = BKASH_AGENT_FEE_PCT
    elif fee_mode == "priyo":
        fee_pct = BKASH_PRIYO_APP_FEE_PCT
    elif fee_mode == "nagad":
        fee_pct = NAGAD_APP_FEE_PCT

    if fee_pct > 0:
        net_bdt = bdt_amount / (1 + fee_pct / 100.0)
        fee_amount = bdt_amount - net_bdt
    else:
        net_bdt = bdt_amount
        fee_amount = 0.0

    usd_value = net_bdt / rate if rate > 0 else 0.0

    return {
        "gross_bdt": bdt_amount,
        "net_bdt": net_bdt,
        "fee_amount": fee_amount,
        "fee_mode": fee_mode,
        "fee_pct": fee_pct,
        "rate": rate,
        "usd_value": usd_value,
        "with_15_tax": round(usd_value * 1.15, 2),
        "without_15_tax": round(usd_value * 0.85, 2),
    }


def generate_trade_slip(
    quote: Dict[str, Any],
    use_comma: bool = False,
    symbol: str = TAKA,
    style: str = "box"
) -> str:
    """
    Generate a clean trade receipt ready for Discord, Facebook, or Messenger.
    """
    amt_usd = quote["amount_usd"]
    rate = quote["rate"]
    base_cost = quote["base_cost"]
    agent_cost = quote["agent_cost"]
    priyo_cost = quote["priyo_cost"]
    nagad_cost = quote["nagad_cost"]
    with_15 = quote["with_15_tax"]
    without_15 = quote["without_15_tax"]

    lines = []
    if style == "box":
        lines.append("╔════════════════════════════════════════╗")
        lines.append("║       🎮 SKINRATE TRADE SLIP           ║")
        lines.append("╠════════════════════════════════════════╣")
        lines.append(f"║ Amount        : {format_usd(amt_usd):<22} ║")
        lines.append(f"║ Rate          : {format_bdt(rate, symbol, use_comma) + '/$' :<22} ║")
        lines.append("╟────────────────────────────────────────╢")
        lines.append("║ 💸 TRANSFER & CASHOUT                  ║")
        lines.append(f"║ • Cost (Base) : {format_bdt(base_cost, symbol, use_comma):<22} ║")
        lines.append(f"║ • bKash Agent : {format_bdt(agent_cost, symbol, use_comma):<22} ║")
        lines.append(f"║ • bKash Priyo : {format_bdt(priyo_cost, symbol, use_comma):<22} ║")
        lines.append(f"║ • Nagad App   : {format_bdt(nagad_cost, symbol, use_comma):<22} ║")
        lines.append("╟────────────────────────────────────────╢")
        lines.append("║ 🏷️ STEAM TAX (15%)                     ║")
        lines.append(f"║ • With 15%    : {format_usd(with_15):<22} ║")
        lines.append(f"║ • Without 15% : {format_usd(without_15):<22} ║")
        lines.append("╚════════════════════════════════════════╝")
    elif style == "discord":
        lines.append(f"**__SkinRate Trade Quote__**")
        lines.append(f"> **Amount:** `{format_usd(amt_usd)}` | **Rate:** `{format_bdt(rate, symbol, use_comma)}/$`")
        lines.append(f"> **Cost (Base):** `{format_bdt(base_cost, symbol, use_comma)}`")
        lines.append(f"> ↳ bKash Agent (+1.85%): `{format_bdt(agent_cost, symbol, use_comma)}`")
        lines.append(f"> ↳ bKash Priyo (+1.49%): `{format_bdt(priyo_cost, symbol, use_comma)}`")
        lines.append(f"> ↳ Nagad App   (+1.25%): `{format_bdt(nagad_cost, symbol, use_comma)}`")
        lines.append(f"> **Steam 15% Tax:** With: `{format_usd(with_15)}` | Without: `{format_usd(without_15)}`")
    else:  # compact plain text
        lines.append(f"SkinRate: {format_usd(amt_usd)} @ {format_bdt(rate, symbol, use_comma)}")
        lines.append(f"Cost: {format_bdt(base_cost, symbol, use_comma)} | Agent: {format_bdt(agent_cost, symbol, use_comma)} | Priyo: {format_bdt(priyo_cost, symbol, use_comma)}")
        lines.append(f"Steam Tax (15%): +15%: {format_usd(with_15)} | -15%: {format_usd(without_15)}")

    return "\n".join(lines)
