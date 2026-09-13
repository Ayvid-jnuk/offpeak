import pytest

from app.services.transaction_service import compute_amounts


def test_120_bill_25_percent_discount_matches_spec_example():
    """$120 bill, 25% discount -> $90 paid, $9 commission, $81 payout."""
    result = compute_amounts(original_amount_cents=12000, discount_percent=25)
    assert result["discount_amount_cents"] == 3000
    assert result["final_amount_cents"] == 9000
    assert result["platform_commission_cents"] == 900
    assert result["restaurant_payout_cents"] == 8100


def test_commission_and_payout_sum_to_final_amount():
    result = compute_amounts(original_amount_cents=15050, discount_percent=17)
    assert result["platform_commission_cents"] + result["restaurant_payout_cents"] == result["final_amount_cents"]


def test_rejects_discount_over_100_percent():
    with pytest.raises(ValueError):
        compute_amounts(original_amount_cents=10000, discount_percent=150)


def test_rejects_negative_original_amount():
    with pytest.raises(ValueError):
        compute_amounts(original_amount_cents=-500, discount_percent=10)


def test_zero_discount_is_allowed():
    result = compute_amounts(original_amount_cents=10000, discount_percent=0)
    assert result["discount_amount_cents"] == 0
    assert result["final_amount_cents"] == 10000
    assert result["platform_commission_cents"] == 1000
    assert result["restaurant_payout_cents"] == 9000


def test_no_negative_commission_or_payout_across_range():
    for amount in [100, 999, 12345, 500000]:
        for discount in [0, 1, 25, 50, 99, 100]:
            result = compute_amounts(amount, discount)
            assert result["platform_commission_cents"] >= 0
            assert result["restaurant_payout_cents"] >= 0
            assert result["final_amount_cents"] >= 0
