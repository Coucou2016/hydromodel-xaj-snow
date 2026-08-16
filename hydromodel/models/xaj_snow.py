"""XAJ-Snow: CemaNeige-style snow accounting in front of XAJ-MZ.

Interface matches MODEL_DICT / UnifiedSimulator: ``xaj_snow(p_and_e, params, ...)``.

Parameter vector (17): the 15 XAJ-MZ parameters, then Kf, CTG.
Forcing: p_and_e [time, basin, 3+] = (P, PET, T[°C]). Missing T raises;
it is never silently treated as rainfall.
"""

from __future__ import annotations

from typing import Union

import numpy as np

from hydromodel.models.model_config import MODEL_PARAM_DICT
from hydromodel.models.param_utils import process_parameters
from hydromodel.models.snow import apply_snow_to_forcing
from hydromodel.models.xaj import xaj

N_XAJ_MZ = 15


def xaj_snow(
    p_and_e,
    params: np.ndarray,
    return_state=False,
    warmup_length=365,
    return_warmup_states=False,
    normalized_params="auto",
    **kwargs,
) -> Union[tuple, np.ndarray]:
    """XAJ with CemaNeige snow, mizuRoute (xaj_mz) channel routing.

    Parameters
    ----------
    p_and_e : ndarray
        [time, basin, features >= 3] with (precipitation, PET, temperature_°C).
    params : ndarray
        [basin, 17] normalized [0, 1] or original scale (see ``normalized_params``).
        Order: K, B, IM, UM, LM, DM, C, SM, EX, KI, KG, A, THETA, CI, CG, Kf, CTG.
    """
    p_and_e = np.asarray(p_and_e, dtype=float)
    params = np.asarray(params, dtype=float)
    if params.ndim == 1:
        params = params.reshape(1, -1)

    model_param_dict = kwargs.get("xaj_snow") or MODEL_PARAM_DICT["xaj_snow"]
    param_ranges = model_param_dict["param_range"]
    processed = process_parameters(
        params, param_ranges, normalized=normalized_params
    )
    if processed.shape[1] < N_XAJ_MZ + 2:
        raise ValueError(
            "xaj_snow expects 17 parameters (15 xaj_mz + Kf + CTG); "
            f"got {processed.shape[1]}"
        )

    xaj_params = processed[:, :N_XAJ_MZ]
    kf = processed[:, N_XAJ_MZ]
    ctg = processed[:, N_XAJ_MZ + 1]
    ts = float(kwargs.get("ts", 0.0))
    tr = float(kwargs.get("tr", 1.0))

    pe_snow, snow_diag = apply_snow_to_forcing(
        p_and_e,
        kf=kf,
        ctg=ctg,
        ts=ts,
        tr=tr,
        require_temperature=True,
    )
    # XAJ generation uses only features 0–1; drop T so xaj_mz is unchanged.
    pe_xaj = pe_snow[:, :, :2]

    xaj_kwargs = {
        k: v
        for k, v in kwargs.items()
        if k not in ("name", "xaj_snow", "ts", "tr", "xaj_mz")
    }
    xaj_kwargs["name"] = "xaj_mz"
    xaj_result = xaj(
        pe_xaj,
        xaj_params,
        return_state=return_state,
        warmup_length=warmup_length,
        return_warmup_states=return_warmup_states,
        normalized_params=False,
        **xaj_kwargs,
    )
    # Attach snow diagnostics only when callers ask for warmup/state dicts.
    if return_warmup_states:
        if isinstance(xaj_result, tuple) and xaj_result and isinstance(
            xaj_result[-1], dict
        ):
            xaj_result[-1]["snow"] = {
                "swe_end": snow_diag["swe"][-1],
                "g_threshold": snow_diag["g_threshold"],
            }
    return xaj_result
