"""SDK tests against the live production API (uses a real key when available,
otherwise verifies the error surface with an invalid key)."""

import os

import pytest

import voltcast


def test_error_surface_with_bad_key():
    vc = voltcast.Client("invalid-key")
    with pytest.raises(voltcast.VoltcastError) as err:
        vc.prices("DE-LU")
    assert err.value.status == 401


def test_zones_public_shape():
    # /v1/zones is public; the client still sends the (invalid) key harmlessly.
    vc = voltcast.Client("invalid-key")
    zones = vc.zones()
    assert len(zones) >= 40
    codes = {z["code"] for z in zones}
    assert "DE-LU" in codes and "SE3" in codes


@pytest.mark.skipif(not os.environ.get("VOLTCAST_TEST_KEY"), reason="needs VOLTCAST_TEST_KEY")
def test_prices_with_real_key():
    vc = voltcast.Client(os.environ["VOLTCAST_TEST_KEY"])
    prices = vc.prices("DE-LU")
    assert len(prices) > 0
    row = prices[0]
    assert {"delivery_start", "delivery_end", "price_eur_mwh", "resolution_flag"} <= set(row)
