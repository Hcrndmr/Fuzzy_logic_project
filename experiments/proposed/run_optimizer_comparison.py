"""Proposed extension A: which metaheuristic should tune the IT2 membership functions?

CSA (used by the reference paper) is compared with FPA, PSO and DE under an identical evaluation budget
(pop * (iters + 1) simulations) on all 18 scenarios, with N_RUNS independent optimiser runs each.
Training uses 4 seeds; the reported delay is the mean over 20 disjoint test seeds.

usage: python experiments/proposed/run_optimizer_comparison.py [--runs 3] [--pop 20] [--iters 60]
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
from config import SCENARIOS, TEST_SEEDS                    # noqa: E402
from exp_utils import base_plans, make_fis, evaluate, optimise  # noqa: E402
from fuzzy_systems import default_vector                    # noqa: E402

METHODS = ["CSA", "FPA", "PSO", "DE"]


def job(args):
    geo, name, method, run, pop, iters = args
    vol, gw, gf = base_plans(geo, name)
    r = optimise(vol, gf, "it2", method, run_seed=100 + run, pop=pop, iters=iters)
    d = evaluate(vol, gf, make_fis("it2", r["vec"]), TEST_SEEDS)
    return {"geo": geo, "scenario": name, "method": method, "run": run, "train_delay": r["train_fit"],
            "train_delay_default": r["train_fit_default"], "test_delay": float(d.mean()), "time_s": r["time_s"],
            "hist": r["hist"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--pop", type=int, default=20)
    ap.add_argument("--iters", type=int, default=60)
    ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args()
    tasks = [(g, n, m, r, a.pop, a.iters) for g in SCENARIOS for n in SCENARIOS[g] for m in METHODS for r in range(a.runs)]
    t0 = time.time()
    with Pool(a.procs) as p:
        res = p.map(job, tasks, chunksize=1)
    print("finished in %.0f s" % (time.time() - t0))
    hist = {f"{r['geo']}/{r['scenario']}/{r['method']}/{r['run']}": r.pop("hist") for r in res}
    with open(os.path.join(ROOT, "results", "params", "optimizer_comparison_hist.json"), "w") as fh:
        json.dump(hist, fh)
    df = pd.DataFrame(res)
    # reference: uniform (un-optimised) IT2 MFs on the same test seeds
    ref = []
    for g in SCENARIOS:
        for n in SCENARIOS[g]:
            vol, gw, gf = base_plans(g, n)
            ref.append({"geo": g, "scenario": n, "uniform_test_delay":
                        float(evaluate(vol, gf, make_fis("it2", default_vector("it2")), TEST_SEEDS).mean())})
    df = df.merge(pd.DataFrame(ref), on=["geo", "scenario"])
    df.to_csv(os.path.join(ROOT, "results", "tables", "optimizer_comparison_runs.csv"), index=False)


if __name__ == "__main__":
    main()
