"""
Unit tests for SkinRate calculation engine.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skinrate.engine import (
    clean_input,
    format_bdt,
    format_usd,
    steam_calc_seller_receives,
    steam_calc_buyer_pays,
    calculate_steam_market_details,
    calculate_transfer,
    calculate_full_quote,
    calculate_reverse,
    calculate_steam_trade_profit,
    generate_trade_slip,
    TAKA,
)


def test_clean_input_valid():
    assert clean_input("25") == 25.0
    assert clean_input("25.50") == 25.50
    assert clean_input("$100") == 100.0
    assert clean_input(f"{TAKA}5000") == 5000.0
    assert clean_input("1,250.75") == 1250.75
    assert clean_input(" 120 tk ") == 120.0
    assert clean_input("120TK") == 120.0
    assert clean_input("120 bdt") == 120.0


def test_clean_input_bangla():
    # Bangla numerals "১২০" -> 120
    assert clean_input("১২০") == 120.0
    assert clean_input("৳৫০০") == 500.0


def test_clean_input_empty_and_invalid():
    assert clean_input("") is None
    assert clean_input("   ") is None

    try:
        clean_input("-10")
        assert False, "Should raise ValueError for negative numbers"
    except ValueError:
        pass

    try:
        clean_input("0")
        assert False, "Should raise ValueError for 0"
    except ValueError:
        pass

    try:
        clean_input("abc")
        assert False, "Should raise ValueError for text"
    except ValueError:
        pass


def test_format_bdt():
    # Test community standard: no comma
    assert format_bdt(12000) == f"{TAKA}12000"
    assert format_bdt(12000.4) == f"{TAKA}12000"
    assert format_bdt(12000.6) == f"{TAKA}12001"

    # Test with comma option
    assert format_bdt(12000, use_comma=True) == f"{TAKA}12,000"


def test_format_usd():
    assert format_usd(12.5) == "$12.50"
    assert format_usd(1500.00) == "$1,500.00"


def test_steam_calculations():
    # $10.00 seller receives
    buyer, v, g = steam_calc_seller_receives(1000)
    assert buyer == 1150
    assert v == 50
    assert g == 100

    # $10.00 buyer pays -> seller receives $8.70 (exact)
    seller, v, g, b = steam_calc_buyer_pays(1000)
    assert seller == 870
    assert b == 1000
    assert seller + v + g == 1000

    # $100.00 buyer pays -> seller receives $86.97 (exact)
    seller100, v100, g100, b100 = steam_calc_buyer_pays(10000)
    assert seller100 == 8697
    assert b100 == 10000


def test_calculate_transfer():
    res = calculate_transfer(100.0, 120.0)
    assert res["base_cost"] == 12000.0
    # bKash agent fee: 1.85% -> 222
    assert round(res["agent_fee"], 2) == 222.0
    assert round(res["buyer_sends_agent"], 2) == 12222.0
    # bKash priyo fee: 1.49% -> 178.8
    assert round(res["priyo_fee"], 2) == 178.8
    assert round(res["buyer_sends_priyo"], 2) == 12178.8


def test_calculate_reverse():
    # Budget ৳12,000 at rate 120 without fee
    res = calculate_reverse(12000, 120, fee_mode="none")
    assert res["usd_value"] == 100.0

    # Budget ৳12,222 at rate 120 with agent fee included
    res_agent = calculate_reverse(12222, 120, fee_mode="agent")
    assert round(res_agent["usd_value"], 2) == 100.0


def test_trade_slip_generation():
    quote = calculate_full_quote(50.0, 120.0, 118.0)
    slip = generate_trade_slip(quote, style="box")
    assert "SKINRATE TRADE SLIP" in slip
    assert "$50.00" in slip
    assert f"{TAKA}6000" in slip


if __name__ == "__main__":
    test_clean_input_valid()
    test_clean_input_bangla()
    test_clean_input_empty_and_invalid()
    test_format_bdt()
    test_format_usd()
    test_steam_calculations()
    test_calculate_transfer()
    test_calculate_reverse()
    test_trade_slip_generation()
    print("All unit tests passed successfully!")
