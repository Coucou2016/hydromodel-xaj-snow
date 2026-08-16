"""Unit tests for CemaNeige-style snow accounting (no external data)."""

import numpy as np
import pytest

from hydromodel.models.snow import (
    cema_neige,
    partition_rain_snow,
    apply_snow_to_forcing,
)
from hydromodel.models.xaj_snow import xaj_snow
from hydromodel.models.xaj import xaj


def test_rain_snow_mass_conservation():
    rng = np.random.default_rng(0)
    prcp = rng.uniform(0.0, 20.0, size=(40, 2))
    temp = rng.uniform(-15.0, 15.0, size=(40, 2))
    rain, snow = partition_rain_snow(prcp, temp, ts=0.0, tr=1.0)
    np.testing.assert_allclose(rain + snow, prcp, rtol=0.0, atol=1e-10)
    assert np.all(rain >= -1e-12)
    assert np.all(snow >= -1e-12)


def test_all_snow_when_far_below_zero():
    prcp = np.full((10, 1), 5.0)
    temp = np.full((10, 1), -20.0)
    rain, snow = partition_rain_snow(prcp, temp, ts=0.0, tr=1.0)
    np.testing.assert_allclose(snow, prcp)
    np.testing.assert_allclose(rain, 0.0)


def test_all_rain_when_far_above_zero():
    prcp = np.full((10, 1), 5.0)
    temp = np.full((10, 1), 20.0)
    rain, snow = partition_rain_snow(prcp, temp, ts=0.0, tr=1.0)
    np.testing.assert_allclose(rain, prcp)
    np.testing.assert_allclose(snow, 0.0)


def test_no_snow_means_melt_near_zero():
    n = 60
    prcp = np.full((n, 1), 3.0)
    temp = np.full((n, 1), 12.0)
    out = cema_neige(prcp, temp, kf=4.0, ctg=0.25)
    np.testing.assert_allclose(out["snow"], 0.0, atol=1e-12)
    np.testing.assert_allclose(out["melt"], 0.0, atol=1e-12)
    np.testing.assert_allclose(out["swe"], 0.0, atol=1e-12)
    np.testing.assert_allclose(out["p_eff"], prcp, atol=1e-12)


def test_single_peak_melt_response():
    """Accumulate snow in a cold spell, then a warm pulse produces melt."""
    n = 40
    prcp = np.zeros((n, 1))
    temp = np.full((n, 1), -8.0)
    prcp[5:15, 0] = 4.0  # 10 days × 4 mm = 40 mm snow
    temp[20:28, 0] = 6.0  # warm melt window
    out = cema_neige(prcp, temp, kf=5.0, ctg=0.2, ts=0.0, tr=0.0)
    snow_in = float(out["snow"].sum())
    melt_sum = float(out["melt"].sum())
    swe_end = float(out["swe"][-1, 0])
    assert snow_in == pytest.approx(40.0)
    # SWE + melt accounts for snowfall
    assert melt_sum + swe_end == pytest.approx(snow_in, abs=1e-6)
    # Melt should concentrate after the warm-up, not during accumulation
    melt_during_cold = float(out["melt"][5:15].sum())
    melt_during_warm = float(out["melt"][20:28].sum())
    assert melt_during_cold < 1.0
    assert melt_during_warm > 5.0
    peak = int(np.argmax(out["melt"][:, 0]))
    assert 20 <= peak <= 30


def test_apply_snow_requires_temperature():
    pe = np.ones((20, 1, 2))
    with pytest.raises(ValueError, match="temperature"):
        apply_snow_to_forcing(pe, kf=3.0, ctg=0.3, require_temperature=True)


def test_xaj_snow_output_shape_and_xaj_mz_ignores_extra_t():
    n_time = 80
    warmup = 10
    p_and_e = np.zeros((n_time, 1, 3))
    p_and_e[:, 0, 0] = 4.0
    p_and_e[:, 0, 1] = 2.0
    p_and_e[:, 0, 2] = 8.0  # rain-only
    params17 = np.full((1, 17), 0.5)
    qsim, es = xaj_snow(
        p_and_e,
        params17,
        warmup_length=warmup,
        return_state=False,
        name="xaj_snow",
        source_book="HF",
        source_type="sources",
    )
    assert qsim.shape[0] == n_time - warmup
    assert es.shape[0] == n_time - warmup

    params15 = np.full((1, 15), 0.5)
    q_mz, _ = xaj(
        p_and_e,
        params15,
        warmup_length=warmup,
        return_state=False,
        name="xaj_mz",
        source_book="HF",
        source_type="sources",
    )
    # Warm rain-only: snow module should leave P almost unchanged → similar Q
    np.testing.assert_allclose(qsim.squeeze(), q_mz.squeeze(), rtol=0.15, atol=0.5)


def test_xaj_snow_raises_without_temperature():
    p_and_e = np.ones((50, 1, 2))
    params17 = np.full((1, 17), 0.5)
    with pytest.raises(ValueError, match="temperature"):
        xaj_snow(p_and_e, params17, warmup_length=5, return_state=False)
