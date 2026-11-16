"""Sanity tests.  Run with:  python tests/test_fuzzy.py   (or pytest)"""
import itertools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from fuzzy_systems import (karnik_mendel, Type1Sugeno, IntervalType2Sugeno, default_vector, n_params, rule_table,
                           RULE_Z)
from simulator import get_instance, simulate
from config import SCENARIOS


def test_km_matches_brute_force():
    rng = np.random.default_rng(0)
    for _ in range(200):
        R = 8
        z = np.sort(rng.uniform(-6, 6, R))
        wu = rng.uniform(0, 1, R)
        wl = wu * rng.uniform(0, 1, R)
        yl, yr = karnik_mendel(z, wl, wu)
        best_l, best_r = np.inf, -np.inf
        for bits in itertools.product([0, 1], repeat=R):          # every extreme weight combination
            w = np.where(np.array(bits) == 1, wu, wl)
            if w.sum() > 1e-12:
                y = np.dot(w, z) / w.sum()
                best_l, best_r = min(best_l, y), max(best_r, y)
        assert abs(yl - best_l) < 1e-9 and abs(yr - best_r) < 1e-9


def test_it2_without_fou_equals_type1():
    """If lower MF == upper MF (and height 1) the IT2 output collapses to the Type-1 output."""
    import fuzzy_systems as fs
    old = fs.LOWER_HEIGHT
    fs.LOWER_HEIGHT = 1.0
    try:
        v1 = default_vector("t1")
        v2 = default_vector("it2", fou=1.0)
        t1, t2 = Type1Sugeno(v1), IntervalType2Sugeno(v2)
        for c, q in [(3, 20), (10, 60), (25, 120), (38, 170), (0, 0)]:
            assert abs(t1(c, q) - t2(c, q)) < 1e-9, (c, q)
    finally:
        fs.LOWER_HEIGHT = old


def test_rule_table_monotone():
    tab = rule_table()
    assert tab.shape == (7, 6) and RULE_Z.size == 42
    assert np.all(np.diff(tab, axis=0) >= 0) and np.all(np.diff(tab, axis=1) >= 0)
    assert tab[0, 0] == 0 and tab[-1, -1] == 6


def test_output_range_and_param_count():
    assert n_params("t1") == 39 and n_params("it2") == 65
    f = IntervalType2Sugeno(default_vector("it2"))
    for c in np.linspace(0, 40, 9):
        for q in np.linspace(0, 175, 9):
            assert -6.0 - 1e-9 <= f(c, q) <= 6.0 + 1e-9


def test_simulator_basic():
    vol = SCENARIOS["4leg"]["med_equal500"]
    inst = get_instance(vol, 1)
    d = simulate(inst, [25.0] * 4)
    assert d >= 0.0
    assert simulate(inst, [25.0] * 4) == d                 # deterministic for a given instance
    # more green for everybody (longer cycle) must not be better than at low demand with short cycle
    low = get_instance(SCENARIOS["4leg"]["low_equal100"], 1)
    assert simulate(low, [10.0] * 4) < simulate(low, [60.0] * 4)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
