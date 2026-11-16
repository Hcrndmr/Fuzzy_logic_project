"""Does IT2 need a larger optimisation budget than Type-1 (65 vs 39 parameters)?

Same set-up as the baseline experiment but pop = 20 and iters in {100, 400} for four hard scenarios.
usage: python experiments/proposed/run_budget_study.py
"""
import os
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from config import TEST_SEEDS                                # noqa: E402
from exp_utils import base_plans, make_fis, evaluate, optimise  # noqa: E402

CASES = [("3leg", "med_equal800"), ("3leg", "high_mixed"), ("4leg", "med_equal500"), ("4leg", "med_mixed")]


def job(a):
    geo, name, kind, iters = a
    vol, gw, gf = base_plans(geo, name)
    r = optimise(vol, gf, kind, "CSA", run_seed=7, pop=20, iters=iters)
    d = evaluate(vol, gf, make_fis(kind, r["vec"]), TEST_SEEDS)
    return {"geo": geo, "scenario": name, "kind": kind, "iters": iters, "train_delay": r["train_fit"],
            "test_delay": float(d.mean()), "time_s": r["time_s"]}


if __name__ == "__main__":
    tasks = [(g, n, k, it) for g, n in CASES for k in ("t1", "it2") for it in (400,)]
    with Pool(2) as p:
        rows = p.map(job, tasks, chunksize=1)
    pd.DataFrame(rows).to_csv(os.path.join(ROOT, "results", "tables", "budget_study.csv"), index=False)
