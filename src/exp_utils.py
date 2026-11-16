"""Helpers shared by all experiment scripts."""
import time
import numpy as np

from config import SCENARIOS, TEST_SEEDS, TRAIN_SEEDS
from fuzzy_systems import Type1Sugeno, IntervalType2Sugeno, default_vector, n_params
from simulator import get_instance, simulate
from signal_plans import webster_greens, fpa_greens
import optimizers


def make_fis(kind, vec, reduction="km"):
    return Type1Sugeno(vec) if kind == "t1" else IntervalType2Sugeno(vec, reduction=reduction)


def evaluate(volumes, base_green, fis=None, seeds=TEST_SEEDS, pss=False, noise=0.0):
    """Average delay (s/veh) for every seed.  Common random numbers: the demand realisation depends only on the seed."""
    out = []
    for s in seeds:
        rng = np.random.default_rng(900000 + s) if noise > 0 else None
        out.append(simulate(get_instance(volumes, s), list(base_green), fis=fis, pss=pss, noise=noise, noise_rng=rng))
    return np.array(out)


def optimise(volumes, base_green, kind, method="CSA", run_seed=0, pop=20, iters=100):
    """Tune the MF parameters of one fuzzy controller for one traffic scenario on the TRAIN seeds."""
    insts = [get_instance(volumes, s) for s in TRAIN_SEEDS]
    bg = list(base_green)

    def fitness(vec):
        fis = make_fis(kind, vec)
        return float(np.mean([simulate(i, bg, fis=fis) for i in insts]))

    x0 = default_vector(kind)
    t0 = time.time()
    best, fbest, hist = optimizers.OPTIMIZERS[method](fitness, n_params(kind), pop=pop, iters=iters,
                                                      seed=run_seed, x0=x0)
    return {"vec": best, "train_fit": fbest, "train_fit_default": float(fitness(x0)), "hist": hist,
            "time_s": time.time() - t0}


def base_plans(geo, name):
    vol = SCENARIOS[geo][name]
    return vol, webster_greens(vol), fpa_greens(vol)


def pct_improvement(ref, new):
    """Positive = `new` has lower delay than `ref` (the paper prints this quantity with a negative sign)."""
    return 100.0 * (ref - new) / ref
