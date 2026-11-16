"""Proposed extension C: type-reduction method (Karnik-Mendel vs Nie-Tan) and computational cost.

* delay: the CSA-tuned IT2 MFs (tuned with KM) are evaluated with KM and with Nie-Tan on all scenarios
* cost : micro-benchmark of one inference call and of one 900 s simulation for T1, IT2-KM, IT2-NT

usage: python experiments/proposed/run_type_reduction.py   (run it alone: timing is not meaningful while other jobs run)
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from config import SCENARIOS, TEST_SEEDS                    # noqa: E402
from exp_utils import base_plans, make_fis, evaluate        # noqa: E402
from simulator import get_instance, simulate                # noqa: E402

PARAMS = json.load(open(os.path.join(ROOT, "results", "params", "baseline_params.json")))

rows = []
for g in SCENARIOS:
    for n in SCENARIOS[g]:
        vol, gw, gf = base_plans(g, n)
        v = np.array(PARAMS[f"{g}/{n}/it2"])
        for red in ("km", "nt"):
            d = evaluate(vol, gf, make_fis("it2", v, reduction=red), TEST_SEEDS)
            for s, x in zip(TEST_SEEDS, d):
                rows.append({"geo": g, "scenario": n, "reduction": red, "seed": s, "delay": x})
pd.DataFrame(rows).to_csv(os.path.join(ROOT, "results", "tables", "type_reduction_per_seed.csv"), index=False)

# ---- timing (single process, repeated, median of 5 repeats)
rng = np.random.default_rng(0)
pts = [(rng.uniform(0, 40), rng.uniform(0, 175)) for _ in range(2000)]
vol, gw, gf = base_plans("4leg", "med_equal800")
v1 = np.array(PARAMS["4leg/med_equal800/t1"])
v2 = np.array(PARAMS["4leg/med_equal800/it2"])
systems = {"Type-1 Sugeno": make_fis("t1", v1), "IT2 Sugeno (Karnik-Mendel)": make_fis("it2", v2, "km"),
           "IT2 Sugeno (Nie-Tan)": make_fis("it2", v2, "nt")}
out = []
for name, f in systems.items():
    t_inf = []
    for _ in range(5):
        t0 = time.perf_counter()
        for c, q in pts:
            f(c, q)
        t_inf.append((time.perf_counter() - t0) / len(pts) * 1e6)
    inst = get_instance(vol, 1)
    t_sim = []
    for _ in range(5):
        t0 = time.perf_counter()
        for _ in range(10):
            simulate(inst, list(gf), fis=f)
        t_sim.append((time.perf_counter() - t0) / 10 * 1e3)
    out.append({"system": name, "inference_us_per_call": float(np.median(t_inf)), "sim_ms_per_900s_run": float(np.median(t_sim))})
t0 = time.perf_counter()
for _ in range(10):
    simulate(inst, list(gf))
out.append({"system": "Fixed time (no inference)", "inference_us_per_call": 0.0,
            "sim_ms_per_900s_run": (time.perf_counter() - t0) / 10 * 1e3})
pd.DataFrame(out).round(2).to_csv(os.path.join(ROOT, "results", "tables", "compute_cost.csv"), index=False)
print(pd.DataFrame(out).round(2).to_string())
