"""Live-demo tool.

  python src/demo.py infer    --count 18 --queue 80 --scenario 4leg/med_equal800
        shows memberships, the most active rules and the Type-1 / Type-2 output for one detector reading
  python src/demo.py simulate --legs 650 800 800 500 [--seeds 5] [--tune]
        runs fixed time, FPA-TSC, Type-1 and Type-2 control for ANY demand (veh/h per leg); --tune adds a quick
        CSA tuning (about 10-30 s) for this demand, otherwise uniform MFs or the stored tuned MFs are used
  python src/demo.py plot     --scenario 4leg/med_equal800 [--out results/figures/mf_demo.png]
        plots uniform and CSA-tuned upper/lower MFs of both inputs
"""
import argparse
import json
import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import CNT_RANGE, QLEN_RANGE, N_CNT_MF, N_Q_MF, SCENARIOS, TEST_SEEDS, OUT_VALUES
from fuzzy_systems import (Type1Sugeno, IntervalType2Sugeno, default_vector, RULE_Z, tri, karnik_mendel,
                           Z_SORTED, _ORDER)
from exp_utils import make_fis, evaluate, optimise
from signal_plans import webster_greens, fpa_greens, hcm_delay

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PARAM_FILE = os.path.join(ROOT, "results", "params", "baseline_params.json")


def load_vec(scn, kind):
    if scn and os.path.exists(PARAM_FILE):
        p = json.load(open(PARAM_FILE))
        key = f"{scn}/{kind}"
        if key in p:
            return np.array(p[key])
    return default_vector(kind)


def cmd_infer(a):
    for kind, name in (("t1", "Type-1"), ("it2", "Interval Type-2")):
        vec = load_vec(a.scenario, kind)
        f = make_fis(kind, vec)
        cnt = f.cnt if kind == "t1" else f.cnt
        mc_u = tri(a.count, f.cnt["c"], f.cnt["wl"], f.cnt["wr"])
        mq_u = tri(a.queue, f.q["c"], f.q["wl"], f.q["wr"])
        print(f"\n=== {name} system ({'tuned for ' + a.scenario if a.scenario else 'uniform MFs'}) ===")
        print("vehicle-count memberships (upper):", np.round(mc_u, 3))
        print("queue-length memberships  (upper):", np.round(mq_u, 3))
        if kind == "it2":
            mc_l, mq_l = f._lower(f.cnt, a.count), f._lower(f.q, a.queue)
            print("vehicle-count memberships (lower):", np.round(mc_l, 3))
            print("queue-length memberships  (lower):", np.round(mq_l, 3))
            wl, wu = f.firing(a.count, a.queue)
            top = np.argsort(-wu)[:5]
            print("most active rules  (count MF, queue MF, consequent s, [w_lower, w_upper]):")
            for r in top:
                if wu[r] > 0:
                    print(f"   MF{r // N_Q_MF + 1}, MF{r % N_Q_MF + 1}, z={RULE_Z[r]:+.0f}, [{wl[r]:.3f}, {wu[r]:.3f}]")
            yl, yr = karnik_mendel(Z_SORTED, wl[_ORDER], wu[_ORDER])
            print(f"type-reduced interval [y_l, y_r] = [{yl:.3f}, {yr:.3f}] s  ->  crisp = {0.5 * (yl + yr):.3f} s")
            print(f"Nie-Tan alternative = {IntervalType2Sugeno(vec, 'nt')(a.count, a.queue):.3f} s")
        else:
            w = np.minimum.outer(mc_u, mq_u).ravel()
            top = np.argsort(-w)[:5]
            print("most active rules (count MF, queue MF, consequent s, firing):")
            for r in top:
                if w[r] > 0:
                    print(f"   MF{r // N_Q_MF + 1}, MF{r % N_Q_MF + 1}, z={RULE_Z[r]:+.0f}, w={w[r]:.3f}")
            print(f"output = sum(w z)/sum(w) = {f(a.count, a.queue):.3f} s")


def cmd_simulate(a):
    vol = tuple(a.legs)
    scn = None
    for g in SCENARIOS:
        for n, v in SCENARIOS[g].items():
            if tuple(v) == vol:
                scn = f"{g}/{n}"
    gw, gf = webster_greens(vol), fpa_greens(vol)
    seeds = TEST_SEEDS[:a.seeds]
    print(f"demand {vol} veh/h | Webster greens {np.round(gw, 1)} | FPA greens {np.round(gf, 1)}")
    print(f"HCM delay of FPA greens: {hcm_delay(vol, gf)[0]:.1f} s/veh")
    res = {"Fixed time (Webster)": evaluate(vol, gw, None, seeds), "FPA-TSC (fixed)": evaluate(vol, gf, None, seeds)}
    for kind, name in (("t1", "Type-1 FL"), ("it2", "IT2 FL")):
        if a.tune:
            r = optimise(vol, gf, kind, "CSA", 0, pop=12, iters=25)
            vec, tag = r["vec"], "tuned now (small budget)"
        elif scn:
            vec, tag = load_vec(scn, kind), f"tuned for {scn}"
        else:
            vec, tag = default_vector(kind), "uniform MFs"
        res[f"{name} [{tag}]"] = evaluate(vol, gf, make_fis(kind, vec), seeds)
    for k, v in res.items():
        print(f"{k:42s} mean delay {v.mean():7.2f} s/veh  (std over seeds {v.std(ddof=1):.2f})")


def cmd_plot(a):
    fig, axes = plt.subplots(2, 2, figsize=(9, 5.5))
    for col, (var, (lo, hi), K, lab) in enumerate((("cnt", CNT_RANGE, N_CNT_MF, "vehicles in range"),
                                                   ("q", QLEN_RANGE, N_Q_MF, "queue length (m)"))):
        x = np.linspace(lo, hi, 600)
        for row, (kind, title) in enumerate((("it2", "uniform"), ("it2", "CSA-tuned"))):
            vec = default_vector("it2") if row == 0 else load_vec(a.scenario, "it2")
            f = IntervalType2Sugeno(vec)
            p = getattr(f, var)
            ax = axes[row, col]
            for i in range(K):
                up = [float(tri(v, p["c"][i], p["wl"][i], p["wr"][i])) for v in x]
                lo_ = [float(IntervalType2Sugeno._lower({k: p[k][i] for k in p}, v)) for v in x]
                ax.plot(x, up, lw=1.2)
                ax.fill_between(x, lo_, up, alpha=.15)
            ax.set_title(f"{lab}: {title}", fontsize=9)
            ax.set_ylim(0, 1.05)
            ax.grid(alpha=.3)
    fig.suptitle(f"Interval Type-2 MFs ({a.scenario}); line = upper MF, shaded = FOU", fontsize=10)
    fig.tight_layout()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    fig.savefig(a.out, dpi=180)
    print("saved", a.out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("infer")
    p.add_argument("--count", type=float, required=True)
    p.add_argument("--queue", type=float, required=True)
    p.add_argument("--scenario", default=None, help="e.g. 4leg/med_equal800 (uses its tuned MFs)")
    p.set_defaults(fn=cmd_infer)
    p = sub.add_parser("simulate")
    p.add_argument("--legs", type=float, nargs="+", required=True, help="3 or 4 volumes in veh/h")
    p.add_argument("--seeds", type=int, default=5)
    p.add_argument("--tune", action="store_true")
    p.set_defaults(fn=cmd_simulate)
    p = sub.add_parser("plot")
    p.add_argument("--scenario", required=True)
    p.add_argument("--out", default=os.path.join(ROOT, "results", "figures", "mf_demo.png"))
    p.set_defaults(fn=cmd_plot)
    args = ap.parse_args()
    args.fn(args)
