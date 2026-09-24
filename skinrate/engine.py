"""
SkinRate Calculation Engine
High-precision math for CS2/Steam community market fees, Bangladeshi cashout rates,
reverse conversions, and formatted trade slips.
"""

from __future__ import annotations
import math
from typing import Dict, Any, Tuple, Optional

TAKA = "\u09F3"
BANGLA_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

# Standard Bangladesh Mobile Financial Services (MFS) Cashout Percentages
BKASH_AGENT_FEE_PCT = 1.85      # 18.5 Tk per 1000 Tk
BKASH_PRIYO_APP_FEE_PCT = 1.49  # 14.9 Tk per 1000 Tk
NAGAD_APP_FEE_PCT = 1.25        # 12.5 Tk per 1000 Tk
NAGAD_USSD_FEE_PCT = 1.50       # 15.0 Tk per 1000 Tk


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
    """Format Bangladeshi Taka. Default is no commas (e.g. ৳12000) as per community standard."""
    rounded = int(round(val))
    if use_comma:
        return f"{symbol}{rounded:,}"
    return f"{symbol}{rounded}"


def format_usd(val: float) -> str:
    """Format USD currency."""
    return f"${val:,.2f}"


def steam_calc_seller_receives(cents: int) -> Tuple[int, int, int]:
    """
    Exact Steam Community Market fee formula when seller receives a specific amount.
    Valve takes 5% (min 1 cent), Game developer (CS2) takes 10% (min 1 cent).
    Returns (buyer_cents, valve_fee_cents, game_fee_cents).
    """
    if cents <= 0:
        return 0, 0, 0
    valve = max(1, int(math.floor(cents * 0.05)))
    game = max(1, int(math.floor(cents * 0.10)))
    buyer = cents + valve + game
    return buyer, valve, game


def steam_calc_buyer_pays(cents: int) -> Tuple[int, int, int, int]:
    """
    Exact Steam Community Market fee formula when buyer pays a specific amount.
    Finds the exact seller cents such that buyer pays cents.
    Returns (seller_cents, valve_fee_cents, game_fee_cents, total_buyer_cents).
    """
    if cents <= 2:
        return 1, 1, 1, 3
    approx = int(cents / 1.15)
    best_s = 1
    # Search around approx
    for s in range(max(1, approx - 12), approx + 13):
        b, v, g = steam_calc_seller_receives(s)
        if b <= cents:
            best_s = s
    b, v, g = steam_calc_seller_receives(best_s)
    return best_s, v, g, b


def calculate_steam_market_details(amount_usd: float) -> Dict[str, Any]:
    """
    Compute full Steam market fee breakdown for an amount.
    Handles both scenarios:
      1. If amount is what buyer pays -> what seller receives.
      2. If amount is what seller receives -> what buyer pays.
    """
    cents = int(round(amount_usd * 100))
    buyer_if_seller, v_if_seller, g_if_seller = steam_calc_seller_receives(cents)
    seller_if_buyer, v_if_buyer, g_if_buyer, _ = steam_calc_buyer_pays(cents)

    return {
        "base_usd": amount_usd,
        # Scenario A: You list item such that you get amount_usd
        "buyer_pays_when_you_receive": buyer_if_seller / 100.0,
        "valve_fee_when_you_receive": v_if_seller / 100.0,
        "game_fee_when_you_receive": g_if_seller / 100.0,
        # Scenario B: Item is listed on market for amount_usd (buyer pays amount_usd)
        "seller_receives_when_buyer_pays": seller_if_buyer / 100.0,
        "valve_fee_when_buyer_pays": v_if_buyer / 100.0,
        "game_fee_when_buyer_pays": g_if_buyer / 100.0,
        # Percentage takes
        "steam_fee_pct": 15.0,
    }


def calculate_transfer(
    amount_usd: float,
    rate: float,
    custom_fee_pct: float = BKASH_AGENT_FEE_PCT
) -> Dict[str, Any]:
    """
    Calculate BDT transfer costs and MFS cashout options.
    """
    base_cost = amount_usd * rate
    agent_fee = base_cost * (BKASH_AGENT_FEE_PCT / 100.0)
    priyo_fee = base_cost * (BKASH_PRIYO_APP_FEE_PCT / 100.0)
    nagad_fee = base_cost * (NAGAD_APP_FEE_PCT / 100.0)
    custom_fee = base_cost * (custom_fee_pct / 100.0)

    # Cashout Option 1: Buyer sends extra so seller receives full base_cost after cashout
    buyer_sends_agent = base_cost + agent_fee
    buyer_sends_priyo = base_cost + priyo_fee
    buyer_sends_nagad = base_cost + nagad_fee
    buyer_sends_custom = base_cost + custom_fee

    # Cashout Option 2: Buyer sends base_cost, seller pays cashout fee from it (net cash in hand)
    net_in_hand_agent = max(0.0, base_cost - agent_fee)
    net_in_hand_priyo = max(0.0, base_cost - priyo_fee)
    net_in_hand_nagad = max(0.0, base_cost - nagad_fee)

    return {
        "rate": rate,
        "base_cost": base_cost,
        "agent_fee": agent_fee,
        "priyo_fee": priyo_fee,
        "nagad_fee": nagad_fee,
        "custom_fee": custom_fee,
        "custom_fee_pct": custom_fee_pct,
        # Send amount (with cashout added)
        "buyer_sends_agent": buyer_sends_agent,
        "buyer_sends_priyo": buyer_sends_priyo,
        "buyer_sends_nagad": buyer_sends_nagad,
        "buyer_sends_custom": buyer_sends_custom,
        # Net in hand (with cashout deducted)
        "net_in_hand_agent": net_in_hand_agent,
        "net_in_hand_priyo": net_in_hand_priyo,
        "net_in_hand_nagad": net_in_hand_nagad,
    }


def calculate_full_quote(
    amount_usd: float,
    item_rate: Optional[float] = None,
    wallet_rate: Optional[float] = None,
    custom_fee_pct: float = BKASH_AGENT_FEE_PCT,
) -> Dict[str, Any]:
    """
    Run full calculation for Item rate, Wallet rate, and Steam market fee.
    """
    item_calc = calculate_transfer(amount_usd, item_rate, custom_fee_pct) if item_rate else None
    wallet_calc = calculate_transfer(amount_usd, wallet_rate, custom_fee_pct) if wallet_rate else None
    steam_calc = calculate_steam_market_details(amount_usd)

    savings = None
    if item_calc and wallet_calc:
        diff = item_calc["base_cost"] - wallet_calc["base_cost"]
        savings = {
            "diff_base": diff,
            "cheaper": "wallet" if diff > 0 else "item" if diff < 0 else "equal",
            "abs_diff": abs(diff),
        }

    return {
        "amount_usd": amount_usd,
        "item": item_calc,
        "wallet": wallet_calc,
        "steam": steam_calc,
        "savings": savings,
        "custom_fee_pct": custom_fee_pct,
    }


def calculate_reverse(
    bdt_amount: float,
    rate: float,
    fee_mode: str = "none",  # 'none', 'agent', 'priyo', 'nagad'
) -> Dict[str, Any]:
    """
    Reverse calculate USD value from a BDT budget or cashout target.
    Modes:
      - 'none': Direct conversion (bdt / rate)
      - 'agent': BDT includes 1.85% cashout fee -> net BDT / rate
      - 'priyo': BDT includes 1.49% cashout fee -> net BDT / rate
      - 'nagad': BDT includes 1.25% cashout fee -> net BDT / rate
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
    }


def calculate_steam_trade_profit(
    buy_price_usd: float,
    sell_price_usd: float,
    cashout_rate: float,
) -> Dict[str, Any]:
    """
    Calculate trade profit/loss for flipping CS2 skins on Steam Market.
    - Buy Price (e.g. from third-party market like Buff / CSFloat in USD)
    - Sell Price on Steam Community Market
    - Cashout rate to BDT
    """
    # Buyer pays sell_price_usd on Steam -> what seller receives into wallet
    cents = int(round(sell_price_usd * 100))
    seller_cents, v_cents, g_cents, _ = steam_calc_buyer_pays(cents)
    wallet_received_usd = seller_cents / 100.0
    steam_fee_total = (v_cents + g_cents) / 100.0

    net_profit_usd = wallet_received_usd - buy_price_usd
    roi_pct = (net_profit_usd / buy_price_usd * 100.0) if buy_price_usd > 0 else 0.0

    # BDT conversions
    cost_bdt = buy_price_usd * cashout_rate
    wallet_bdt = wallet_received_usd * cashout_rate
    profit_bdt = net_profit_usd * cashout_rate

    return {
        "buy_price_usd": buy_price_usd,
        "sell_price_usd": sell_price_usd,
        "wallet_received_usd": wallet_received_usd,
        "steam_fee_usd": steam_fee_total,
        "valve_fee_usd": v_cents / 100.0,
        "game_fee_usd": g_cents / 100.0,
        "net_profit_usd": net_profit_usd,
        "roi_pct": roi_pct,
        "cashout_rate": cashout_rate,
        "cost_bdt": cost_bdt,
        "wallet_bdt": wallet_bdt,
        "profit_bdt": profit_bdt,
    }


def generate_trade_slip(
    quote: Dict[str, Any],
    use_comma: bool = False,
    symbol: str = TAKA,
    style: str = "box"
) -> str:
    """
    Generate a formatted trade receipt / summary ready for posting to
    Discord, Facebook CS2 trading groups, Messenger, or WhatsApp.
    """
    amt_usd = quote["amount_usd"]
    item = quote.get("item")
    wallet = quote.get("wallet")
    steam = quote.get("steam")

    lines = []
    if style == "box":
        lines.append("╔════════════════════════════════════════╗")
        lines.append("║       🎮 SKINRATE TRADE SLIP           ║")
        lines.append("╠════════════════════════════════════════╣")
        lines.append(f"║ Amount        : {format_usd(amt_usd):<22} ║")

        if item:
            lines.append("╟────────────────────────────────────────╢")
            lines.append(f"║ 💎 ITEM TRANSFER (Rate {format_bdt(item['rate'], symbol, use_comma)})       ║")
            lines.append(f"║ • Base Cost   : {format_bdt(item['base_cost'], symbol, use_comma):<22} ║")
            lines.append(f"║ • bKash Agent : {format_bdt(item['buyer_sends_agent'], symbol, use_comma):<22} ║")
            lines.append(f"║ • Priyo / App : {format_bdt(item['buyer_sends_priyo'], symbol, use_comma):<22} ║")
            lines.append(f"║ • Nagad App   : {format_bdt(item['buyer_sends_nagad'], symbol, use_comma):<22} ║")

        if wallet:
            lines.append("╟────────────────────────────────────────╢")
            lines.append(f"║ 💼 WALLET TRANSFER (Rate {format_bdt(wallet['rate'], symbol, use_comma)})     ║")
            lines.append(f"║ • Base Cost   : {format_bdt(wallet['base_cost'], symbol, use_comma):<22} ║")
            lines.append(f"║ • bKash Agent : {format_bdt(wallet['buyer_sends_agent'], symbol, use_comma):<22} ║")
            lines.append(f"║ • Priyo / App : {format_bdt(wallet['buyer_sends_priyo'], symbol, use_comma):<22} ║")

        if steam:
            lines.append("╟────────────────────────────────────────╢")
            buyer_val = steam["buyer_pays_when_you_receive"]
            seller_val = steam["seller_receives_when_buyer_pays"]
            lines.append("║ 🏷️ STEAM COMMUNITY MARKET              ║")
            lines.append(f"║ • Buyer Pays  : {format_usd(buyer_val):<22} ║")
            lines.append(f"║ • Seller Gets : {format_usd(seller_val):<22} ║")

        lines.append("╚════════════════════════════════════════╝")
    elif style == "discord":
        lines.append(f"**__SkinRate Trade Quote__**")
        lines.append(f"> **Amount:** `{format_usd(amt_usd)}`")
        if item:
            lines.append(f"> **Item Rate ({format_bdt(item['rate'], symbol, use_comma)}):** `{format_bdt(item['base_cost'], symbol, use_comma)}`")
            lines.append(f"> ↳ bKash Agent (+1.85%): `{format_bdt(item['buyer_sends_agent'], symbol, use_comma)}`")
            lines.append(f"> ↳ bKash Priyo (+1.49%): `{format_bdt(item['buyer_sends_priyo'], symbol, use_comma)}`")
        if wallet:
            lines.append(f"> **Wallet Rate ({format_bdt(wallet['rate'], symbol, use_comma)}):** `{format_bdt(wallet['base_cost'], symbol, use_comma)}`")
            lines.append(f"> ↳ bKash Agent (+1.85%): `{format_bdt(wallet['buyer_sends_agent'], symbol, use_comma)}`")
        if steam:
            lines.append(f"> **Steam 15% Tax:** Buyer pays `{format_usd(steam['buyer_pays_when_you_receive'])}` | Seller receives `{format_usd(steam['seller_receives_when_buyer_pays'])}`")
    else:  # compact plain text for quick SMS / Messenger
        lines.append(f"SkinRate: {format_usd(amt_usd)}")
        if item:
            lines.append(f"Item ({format_bdt(item['rate'], symbol, use_comma)}): {format_bdt(item['base_cost'], symbol, use_comma)} | Agent: {format_bdt(item['buyer_sends_agent'], symbol, use_comma)}")
        if wallet:
            lines.append(f"Wallet ({format_bdt(wallet['rate'], symbol, use_comma)}): {format_bdt(wallet['base_cost'], symbol, use_comma)} | Agent: {format_bdt(wallet['buyer_sends_agent'], symbol, use_comma)}")
        if steam:
            lines.append(f"Steam: Buyer {format_usd(steam['buyer_pays_when_you_receive'])} / Seller {format_usd(steam['seller_receives_when_buyer_pays'])}")

    return "\n".join(lines)
