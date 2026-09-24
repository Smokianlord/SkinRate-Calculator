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
    calculate_quote,
    calculate_reverse,
    generate_trade_slip,
    TAKA,
)


def test_clean_input_valid():
    assert clean_input("25") == 25.0
    assert clean_input("85") == 85.0
    assert clean_input("$100") == 100.0
    assert clean_input(f"{TAKA}5000") == 5000.0
    assert clean_input("1,250.75") == 1250.75
    assert clean_input(" 85 tk ") == 85.0
    assert clean_input("85TK") == 85.0
    assert clean_input("85 bdt") == 85.0


def test_clean_input_bangla():
    assert clean_input("৮৫") == 85.0
    assert clean_input("৳৫০০") == 500.0


def test_clean_input_empty_and_invalid():
    assert clean_input("") is None
    assert clean_input("   ") is None

    try:
        clean_input("-10")
        assert False
    except ValueError:
        pass

    try:
        clean_input("0")
        assert False
    except ValueError:
        pass


def test_format_bdt():
    assert format_bdt(850) == f"{TAKA}850"
    assert format_bdt(12000, use_comma=True) == f"{TAKA}12,000"


def test_format_usd():
    assert format_usd(12.5) == "$12.50"


def test_calculate_quote():
    # $10 at 85 rate
    q = calculate_quote(10.0, 85.0)
    assert q["base_cost"] == 850.0
    assert abs(q["agent_cost"] - 865.725) < 0.01
    assert abs(q["priyo_cost"] - 862.665) < 0.01
    assert abs(q["nagad_cost"] - 860.625) < 0.01
    assert q["with_15_tax"] == 11.50
    assert q["without_15_tax"] == 8.50


def test_calculate_reverse():
    r = calculate_reverse(850.0, 85.0, fee_mode="none")
    assert r["usd_value"] == 10.0
    assert r["with_15_tax"] == 11.50
    assert r["without_15_tax"] == 8.50


def test_trade_slip_generation():
    q = calculate_quote(10.0, 85.0)
    slip = generate_trade_slip(q, style="box")
    assert "SKINRATE TRADE SLIP" in slip
    assert "$10.00" in slip
    assert f"{TAKA}850" in slip


if __name__ == "__main__":
    test_clean_input_valid()
    test_clean_input_bangla()
    test_clean_input_empty_and_invalid()
    test_format_bdt()
    test_format_usd()
    test_calculate_quote()
    test_calculate_reverse()
    test_trade_slip_generation()
    print("All unit tests passed successfully!")
