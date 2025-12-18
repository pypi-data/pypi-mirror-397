import numpy as np
from omegaconf import DictConfig

from .fitting_algorithms import calc_force_shift
from .fitting_algorithms import tire_param_fitting
from .parameters import MFSimpleParams


def fit_tire_parameters(
    force_n: np.array,
    load_n: np.array,
    sigma: np.array,
    config: DictConfig,
    fit_flags: dict,
):
    params_min = MFSimpleParams(**config.params_min)
    params_max = MFSimpleParams(**config.params_max)
    params_init = MFSimpleParams(**config.params_init)

    params_init.S_V, params_init.S_H = calc_force_shift(sigma, force_n)
    params_init.D = np.max(force_n)

    params_svi, std_svi, _ = tire_param_fitting(
        "SVI", "MFSimple", sigma, force_n, load_n, params_init, params_min, params_max, config.svi_options, fit_flags
    )
    params_nelder, _, _ = tire_param_fitting(
        "Nelder",
        "MFSimple",
        sigma,
        force_n,
        load_n,
        params_init,
        params_min,
        params_max,
        config.nelder_options,
        fit_flags,
    )

    results = {
        "svi": {"parameters": params_svi, "std": std_svi},
        "nelder": {"parameters": params_nelder, "std": None},
        "params_min": params_min,
        "params_max": params_max,
        "params_init": params_init,
    }

    return results
