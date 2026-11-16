"""Fixed-time plans: Webster's method and the HCM-delay based FPA green optimisation (FPA-TSC).

The phase plan is fixed to split phasing (one phase per approach).  The FPA of the reference paper also
selects the phase plan; that part is outside this project's minimum reproduction requirement (MRR).
"""
import numpy as np

from config import (LANES_PER_LEG, SAT_FLOW_EFF, LOST_PER_PHASE, G_MIN, G_MAX, SIM_TIME)
import optimizers


def webster_greens(volumes, c_max=120.0, c_min=30.0):
    """Webster (1958): C0 = (1.5 L + 5) / (1 - Y); greens proportional to the critical flow ratios."""
    n = len(volumes)
    y = np.array(volumes, dtype=float) / LANES_PER_LEG / SAT_FLOW_EFF
    L = LOST_PER_PHASE * n
    Y = y.sum()
    C = c_max if Y >= 0.9 else float(np.clip((1.5 * L + 5.0) / (1.0 - Y), c_min, c_max))
    g = (C - L) * y / Y
    return np.clip(g, G_MIN, G_MAX)


def hcm_delay(volumes, greens, T=SIM_TIME / 3600.0, k=0.5, I=1.0):
    """Flow-weighted HCM control delay (Eqs. 7-9 of the reference paper, PF = 1, d3 = 0) in s/veh.

    Returns (delay, max_X).  X = v / c is the degree of saturation of a leg (per-lane flow)."""
    g = np.asarray(greens, dtype=float)
    q = np.asarray(volumes, dtype=float)
    C = g.sum() + LOST_PER_PHASE * len(g)
    s = SAT_FLOW_EFF
    cap = s * g / C                                   # veh/h/lane
    X = (q / LANES_PER_LEG) / cap
    d1 = 0.5 * C * (1 - g / C) ** 2 / (1 - np.minimum(1.0, X) * g / C)
    d2 = 900 * T * ((X - 1) + np.sqrt((X - 1) ** 2 + 8 * k * I * X / (cap * T)))
    d = d1 + d2
    return float(np.dot(d, q) / q.sum()), float(X.max())


def fpa_greens(volumes, seed=0, pop=25, iters=200):
    """Green times found by the flower pollination algorithm minimising the HCM delay (reference paper, Table 4)."""
    n = len(volumes)
    lo, hi = G_MIN, G_MAX

    def f(u):
        g = lo + (hi - lo) * u
        d, xmax = hcm_delay(volumes, g)
        if xmax > 1.4:                                # constraint 0 <= qC/(s g) <= 1.4
            d += 1000.0 * (xmax - 1.4)
        return d

    x0 = np.full(n, 0.4)
    best, _, _ = optimizers.fpa(f, n, pop=pop, iters=iters, seed=seed, x0=x0, init_sigma=0.3)
    return lo + (hi - lo) * best
