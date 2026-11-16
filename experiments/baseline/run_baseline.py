"""Reproduction experiment (MRR): fixed-time vs FPA-TSC vs Type-1 FL-TSC vs IT2 FL-TSC (CSA-optimised MFs).

usage:  python experiments/baseline/run_baseline.py [--pop 20] [--iters 100]
Outputs: results/tables/baseline_per_seed.csv, results/params/baseline_params.json, results/tables/baseline_opt_log.csv
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from config import SCENARIOS, TEST_SEEDS                       # noqa: E402
from exp_utils import base_plans, make_fis, evaluate, optimise  # noqa: E402
from fuzzy_systems import default_vector                       # noqa: E402


def job(args):
    geo, name, kind, pop, iters = args
    vol, gw, gf = base_plans(geo, name)
    res = optimise(vol, gf, kind, "CSA", run_seed=0, pop=pop, iters=iters)
    return geo, name, kind, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", type=int, default=20)
    ap.add_argument("--iters", type=int, default=100)
    ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args()

    tasks = [(g, n, k, a.pop, a.iters) for g in SCENARIOS for n in SCENARIOS[g] for k in ("t1", "it2")]
    t0 = time.time()
    with Pool(a.procs) as p:
        results = p.map(job, tasks, chunksize=1)
    print("optimisation finished in %.1f s" % (time.time() - t0))

    params, logs = {}, []
    for geo, name, kind, r in results:
        params[f"{geo}/{name}/{kind}"] = r["vec"].tolist()
        logs.append({"geo": geo, "scenario": name, "kind": kind, "train_delay_default": r["train_fit_default"],
                     "train_delay_opt": r["train_fit"], "opt_time_s": r["time_s"]})
    os.makedirs(os.path.join(ROOT, "results", "params"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "params", "baseline_params.json"), "w") as fh:
        json.dump(params, fh)
    pd.DataFrame(logs).to_csv(os.path.join(ROOT, "results", "tables", "baseline_opt_log.csv"), index=False)

    rows = []
    for geo in SCENARIOS:
        for name, vol in SCENARIOS[geo].items():
            vol, gw, gf = base_plans(geo, name)
            ctrls = {
                "FixedTime(Webster)": (gw, None, False),
                "FPA-TSC": (gf, None, False),
                "T1-FL(uniform MF)": (gf, make_fis("t1", default_vector("t1")), False),
                "T1-FL(CSA)": (gf, make_fis("t1", np.array(params[f"{geo}/{name}/t1"])), False),
                "IT2-FL(uniform MF)": (gf, make_fis("it2", default_vector("it2")), False),
                "IT2-FL(CSA)": (gf, make_fis("it2", np.array(params[f"{geo}/{name}/it2"])), False),
                "IT2-FL(CSA)+PSS": (gf, make_fis("it2", np.array(params[f"{geo}/{name}/it2"])), True),
            }
            for cname, (g, fis, pss) in ctrls.items():
                d = evaluate(vol, g, fis, TEST_SEEDS, pss=pss)
                for s, v in zip(TEST_SEEDS, d):
                    rows.append({"geo": geo, "scenario": name, "controller": cname, "seed": s, "delay": v})
    pd.DataFrame(rows).to_csv(os.path.join(ROOT, "results", "tables", "baseline_per_seed.csv"), index=False)
    print("done, total %.1f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
