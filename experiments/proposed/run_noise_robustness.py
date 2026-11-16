"""Proposed extension B: robustness to detector noise, Type-1 vs interval Type-2.

The MFs tuned on noise-free data in the baseline experiment are re-used unchanged.  Multiplicative Gaussian
noise  x_obs = max(0, x (1 + sigma * N(0,1)))  is added to BOTH inputs (vehicle count and queue length) at every
decision.  Hypothesis (from the Type-2 literature): the footprint of uncertainty makes IT2 less sensitive.

usage: python experiments/proposed/run_noise_robustness.py
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from config import SCENARIOS, TEST_SEEDS                    # noqa: E402
from exp_utils import base_plans, make_fis, evaluate        # noqa: E402

SIGMAS = [0.0, 0.1, 0.2, 0.3, 0.5, 0.75]
PARAMS = json.load(open(os.path.join(ROOT, "results", "params", "baseline_params.json")))


def job(args):
    geo, name = args
    vol, gw, gf = base_plans(geo, name)
    t1 = make_fis("t1", np.array(PARAMS[f"{geo}/{name}/t1"]))
    it2 = make_fis("it2", np.array(PARAMS[f"{geo}/{name}/it2"]))
    rows = []
    for s in SIGMAS:
        for cname, fis in (("T1-FL(CSA)", t1), ("IT2-FL(CSA)", it2)):
            d = evaluate(vol, gf, fis, TEST_SEEDS, noise=s)
            for seed, v in zip(TEST_SEEDS, d):
                rows.append({"geo": geo, "scenario": name, "sigma": s, "controller": cname, "seed": seed, "delay": v})
    d = evaluate(vol, gf, None, TEST_SEEDS)
    for seed, v in zip(TEST_SEEDS, d):                          # sensor-free reference (does not depend on sigma)
        rows.append({"geo": geo, "scenario": name, "sigma": np.nan, "controller": "FPA-TSC", "seed": seed, "delay": v})
    return rows


if __name__ == "__main__":
    t0 = time.time()
    tasks = [(g, n) for g in SCENARIOS for n in SCENARIOS[g]]
    with Pool(2) as p:
        out = p.map(job, tasks, chunksize=1)
    pd.DataFrame([r for rows in out for r in rows]).to_csv(
        os.path.join(ROOT, "results", "tables", "noise_per_seed.csv"), index=False)
    print("done in %.0f s" % (time.time() - t0))
