"""CemaNeige-style degree-day snow accounting (daily, lumped).

References
----------
Valéry, A., Andréassian, V. and Perrin, C. (2014). "As simple as possible but
not simpler": What is useful in a temperature-based snow-accounting routine?
Part 1–2. Journal of Hydrology, 517, 1166–1187.
doi:10.1016/j.jhydrol.2014.04.059 / 10.1016/j.jhydrol.2014.04.058

airGR implementation (Coron et al.): CemaNeige X1 = CTG [-], X2 = Kf
[mm/°C/day]. Typical Kf ≈ 2–6 mm/°C/day (search range often 0–10);
CTG in [0, 1]. See https://webgr.inrae.fr/eng/tools/hydrological-models/snow-model/

This module is **lumped** (one elevation band) because Caravan supplies
catchment-mean temperature. Original CemaNeige uses five equal-area
elevation zones; that spatialisation is intentionally omitted here.

Units (daily time step)
-----------------------
P, rain, snow, melt, SWE : mm/day or mm
T, Ts, G (thermal state) : °C
Kf : mm/°C/day
CTG : dimensionless in [0, 1]
"""

from __future__ import annotations

from typing import Optional

import numpy as np

# Float tolerance for "isothermal snowpack" (G == 0°C) tests.
_G_ISOTHERMAL = 1e-8
# Avoid division by zero when mean annual snowfall is ~0 (snow-free basins).
_GTHR_MIN = 1e-6


def _as_1d_basin(value, n_basin: int, name: str) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if arr.ndim == 0:
        return np.full(n_basin, float(arr), dtype=float)
    arr = np.reshape(arr, -1)
    if arr.size == 1:
        return np.full(n_basin, float(arr[0]), dtype=float)
    if arr.size != n_basin:
        raise ValueError(f"{name} length {arr.size} != n_basin {n_basin}")
    return arr.astype(float)


def partition_rain_snow(
    prcp: np.ndarray,
    temp: np.ndarray,
    ts: float = 0.0,
    tr: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Split precipitation into rain and snow using a linear T band.

    Parameters
    ----------
    prcp : ndarray
        Precipitation [mm/day], shape [time, basin].
    temp : ndarray
        Air temperature [°C], same shape.
    ts : float
        Rain/snow threshold temperature [°C]. CemaNeige default is 0°C.
    tr : float
        Half-width of the linear mix band [°C]. All snow if T <= ts-tr;
        all rain if T >= ts+tr. tr=0 is a sharp 0/1 split at ts.

    Returns
    -------
    rain, snow : ndarray
        Liquid and solid precipitation [mm/day], same shape as ``prcp``.
        Mass conservation: rain + snow == prcp (clipped at 0).
    """
    p = np.maximum(np.asarray(prcp, dtype=float), 0.0)
    t = np.asarray(temp, dtype=float)
    tr = max(float(tr), 0.0)
    ts = float(ts)
    if tr == 0.0:
        snow_frac = (t <= ts).astype(float)
    else:
        # 1 at T = ts-tr, 0 at T = ts+tr
        snow_frac = np.clip((ts + tr - t) / (2.0 * tr), 0.0, 1.0)
    snow = p * snow_frac
    rain = p - snow
    return rain, snow


def estimate_g_threshold(snow: np.ndarray, steps_per_year: float = 365.25) -> np.ndarray:
    """CemaNeige snow-cover threshold: 0.9 × mean annual snowfall [mm].

    airGR / Valéry: Gthreshold = 0.9 * mean(Psol) * 365.25 for daily data.
    Computed independently per basin. A tiny floor is used on snow-free basins.
    """
    psol = np.asarray(snow, dtype=float)
    mean_daily = np.nanmean(psol, axis=0)
    gthr = 0.9 * mean_daily * float(steps_per_year)
    return np.maximum(gthr, _GTHR_MIN)


def cema_neige(
    prcp: np.ndarray,
    temp: np.ndarray,
    kf,
    ctg,
    ts: float = 0.0,
    tr: float = 1.0,
    g_threshold: Optional[np.ndarray] = None,
    swe0: float = 0.0,
    g0: float = 0.0,
    steps_per_year: float = 365.25,
) -> dict[str, np.ndarray]:
    """Run lumped CemaNeige snow accounting.

    Parameters
    ----------
    prcp, temp : ndarray
        [time, basin] precipitation [mm/day] and temperature [°C].
        Temperatures > 200 are treated as Kelvin and converted to °C.
    kf : float or ndarray
        Degree-day melt factor [mm/°C/day], shape [] or [basin].
        Literature: typically 2–6, calibration range often 0–10.
    ctg : float or ndarray
        Snowpack thermal-state inertia [-] in [0, 1].
    ts, tr : float
        Rain/snow split threshold and linear band (see ``partition_rain_snow``).
    g_threshold : ndarray, optional
        Melt-modulating SWE threshold [mm], shape [basin]. If None, set to
        0.9 × mean annual snowfall from this series (CemaNeige default).
    swe0, g0 : float
        Initial SWE [mm] and thermal state G [°C] (G is always ≤ 0).
    steps_per_year : float
        Used only when estimating ``g_threshold`` (365.25 for daily data).

    Returns
    -------
    dict
        rain, snow, melt, p_eff (rain+melt), swe, thermal_state, gratio
        all [time, basin] except scalars used internally.
    """
    p = np.asarray(prcp, dtype=float)
    t = np.asarray(temp, dtype=float)
    if p.ndim != 2 or t.shape != p.shape:
        raise ValueError(
            f"prcp and temp must be [time, basin]; got {p.shape} and {t.shape}"
        )
    n_time, n_basin = p.shape

    # Kelvin → °C if the series is clearly not in Celsius
    t_mean = np.nanmean(t)
    if np.isfinite(t_mean) and t_mean > 200.0:
        t = t - 273.15

    kf_b = np.maximum(_as_1d_basin(kf, n_basin, "Kf"), 0.0)
    ctg_b = np.clip(_as_1d_basin(ctg, n_basin, "CTG"), 0.0, 1.0)

    rain, snow = partition_rain_snow(p, t, ts=ts, tr=tr)
    if g_threshold is None:
        g_thr = estimate_g_threshold(snow, steps_per_year=steps_per_year)
    else:
        g_thr = np.maximum(_as_1d_basin(g_threshold, n_basin, "g_threshold"), _GTHR_MIN)

    melt = np.zeros_like(p)
    swe_ts = np.zeros_like(p)
    g_ts = np.zeros_like(p)
    gratio_ts = np.zeros_like(p)

    swe = np.full(n_basin, float(swe0), dtype=float)
    g = np.minimum(0.0, np.full(n_basin, float(g0), dtype=float))

    for i in range(n_time):
        ti = t[i]
        # NaN temperature: cannot classify; keep pack, treat P as rain (explicit).
        ti_ok = np.where(np.isfinite(ti), ti, ts)

        swe = swe + snow[i]

        # Thermal state: G_t = min(0, CTG * G_{t-1} + (1-CTG) * T_t)  [°C]
        g = np.minimum(0.0, ctg_b * g + (1.0 - ctg_b) * ti_ok)

        # Potential melt only when the pack is isothermal at 0°C (Valéry / airGR).
        # MeltPot = min(SWE, max(0, Kf * T))
        isothermal = g >= -_G_ISOTHERMAL
        melt_pot = np.where(
            isothermal,
            np.minimum(swe, np.maximum(0.0, kf_b * ti_ok)),
            0.0,
        )

        # Snow-covered area factor: Gratio = min(1, SWE / Gthreshold)
        # Actual melt = (0.9 * Gratio + 0.1) * MeltPot  (10% residual melt)
        gratio = np.minimum(1.0, swe / g_thr)
        melt_i = np.minimum(swe, (0.9 * gratio + 0.1) * melt_pot)
        melt_i = np.maximum(melt_i, 0.0)
        swe = np.maximum(swe - melt_i, 0.0)

        melt[i] = melt_i
        swe_ts[i] = swe
        g_ts[i] = g
        gratio_ts[i] = gratio

    p_eff = rain + melt
    return {
        "rain": rain,
        "snow": snow,
        "melt": melt,
        "p_eff": p_eff,
        "swe": swe_ts,
        "thermal_state": g_ts,
        "gratio": gratio_ts,
        "g_threshold": g_thr,
    }


def apply_snow_to_forcing(
    p_and_e: np.ndarray,
    kf,
    ctg,
    ts: float = 0.0,
    tr: float = 1.0,
    require_temperature: bool = True,
) -> tuple[np.ndarray, dict]:
    """Replace precipitation with rain+melt; keep PET as feature 1.

    Parameters
    ----------
    p_and_e : ndarray
        [time, basin, features]. Feature 0 = P [mm/day], 1 = PET [mm/day],
        2 = T [°C] when present.
    require_temperature : bool
        If True and features < 3, raise. If False, return inputs unchanged
        (used only for diagnostics; XAJ-Snow always requires T).
    """
    arr = np.asarray(p_and_e, dtype=float)
    if arr.ndim != 3:
        raise ValueError(f"p_and_e must be [time, basin, features], got {arr.shape}")
    if arr.shape[2] < 3:
        if require_temperature:
            raise ValueError(
                "Snow module requires air temperature as p_and_e[..., 2] (°C). "
                f"Got shape {arr.shape}. Rebuild the CARAVAN minicache with "
                "temperature_2m_mean and keep UnifiedDataLoader 3-feature output. "
                "Snowfall must not be silently treated as rainfall."
            )
        return arr, {}
    out = cema_neige(arr[:, :, 0], arr[:, :, 2], kf=kf, ctg=ctg, ts=ts, tr=tr)
    pe = arr.copy()
    pe[:, :, 0] = out["p_eff"]
    return pe, out
