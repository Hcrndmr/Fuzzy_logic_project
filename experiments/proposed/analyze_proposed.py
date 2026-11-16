"""Tables and figures for the proposed extensions A (optimisers), B (noise), C (type reduction, budget)."""
import json
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TAB = os.path.join(ROOT, "results", "tables")
FIG = os.path.join(ROOT, "results", "figures")
PAR = os.path.join(ROOT, "results", "params")


def holm(ps):
    ps = np.asarray(ps)
    order = np.argsort(ps)
    adj = np.empty_like(ps)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (len(ps) - rank) * ps[i])
        adj[i] = min(1.0, running)
    return adj


def optimizer_comparison():
    p = os.path.join(TAB, "optimizer_comparison_runs.csv")
    if not os.path.exists(p):
        return
    df = pd.read_csv(p)
    df["gain_%"] = 100 * (df.uniform_test_delay - df.test_delay) / df.uniform_test_delay
    sc = df.groupby(["geo", "scenario", "method"]).agg(test=("test_delay", "mean"), gain=("gain_%", "mean"),
                                                         train=("train_delay", "mean"), t=("time_s", "mean")).reset_index()
    piv = sc.pivot_table(index=["geo", "scenario"], columns="method", values="test")
    methods = ["CSA", "FPA", "PSO", "DE"]
    piv = piv[methods]
    piv.round(2).to_csv(os.path.join(TAB, "optimizer_mean_test_delay.csv"))
    g = sc.pivot_table(index=["geo", "scenario"], columns="method", values="gain")[methods]
    run_gain = df.groupby(["method", "run"])["gain_%"].mean().groupby("method").agg(["mean", "std"])
    summ = pd.DataFrame({"mean_gain_vs_uniform_%": g.mean(), "std_over_runs_%": run_gain["std"],
                         "mean_test_delay": piv.mean(), "mean_time_s": sc.groupby("method")["t"].mean()}).loc[methods]
    stat, pf = stats.friedmanchisquare(*[piv[m].values for m in methods])
    ranks = piv.rank(axis=1).mean()
    summ["mean_rank"] = ranks
    pw = []
    for m in methods[1:]:
        try:
            pw.append(stats.wilcoxon(piv["CSA"], piv[m]).pvalue)
        except ValueError:
            pw.append(1.0)
    pw_adj = holm(pw)
    summ["p_vs_CSA(Holm)"] = [np.nan] + list(pw_adj)
    summ.round(4).to_csv(os.path.join(TAB, "optimizer_summary.csv"))
    with open(os.path.join(TAB, "optimizer_friedman.txt"), "w") as fh:
        fh.write(f"Friedman chi2={stat:.3f} p={pf:.4f} (18 scenarios x 4 optimisers)\n")
    print(summ.round(3).to_string(), "\nFriedman", stat, pf)
    # convergence figure
    hist = json.load(open(os.path.join(PAR, "optimizer_comparison_hist.json")))
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    for m, c in zip(methods, ["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728"]):
        H = np.array([np.array(v) / v[0] for k, v in hist.items() if k.split("/")[2] == m])
        ax.plot(100 * (1 - H.mean(axis=0)), label=m, color=c)
    ax.set_xlabel("iteration"); ax.set_ylabel("training-delay reduction (%)")
    ax.set_title("Convergence (mean over 18 scenarios x 3 runs)", fontsize=9)
    ax.legend(); ax.grid(alpha=.3); fig.tight_layout()
    fig.savefig(os.path.join(FIG, "optimizer_convergence.png"), dpi=200); plt.close(fig)
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    ax.bar(methods, g.mean().values, color=["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728"])
    ax.errorbar(methods, g.mean().values, yerr=[run_gain.loc[m, "std"] for m in methods], fmt="none", ecolor="k", capsize=3)
    ax.set_ylabel("test-delay reduction vs uniform MF (%)"); ax.grid(axis="y", alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "optimizer_gain.png"), dpi=200); plt.close(fig)


def noise():
    p = os.path.join(TAB, "noise_per_seed.csv")
    if not os.path.exists(p):
        return
    df = pd.read_csv(p)
    ref = df[df.controller == "FPA-TSC"].groupby(["geo", "scenario"])["delay"].mean().rename("fpa")
    d = df[df.controller != "FPA-TSC"].groupby(["geo", "scenario", "sigma", "controller"])["delay"].mean().reset_index()
    d = d.merge(ref.reset_index(), on=["geo", "scenario"])
    d["gain_vs_fixed_%"] = 100 * (d.fpa - d.delay) / d.fpa
    base0 = d[d.sigma == 0.0].set_index(["geo", "scenario", "controller"])["delay"]
    d["degr_%"] = [100 * (r.delay - base0[(r.geo, r.scenario, r.controller)]) / base0[(r.geo, r.scenario, r.controller)]
                   for r in d.itertuples()]
    tab = d.groupby(["geo", "sigma", "controller"])[["delay", "gain_vs_fixed_%", "degr_%"]].mean().round(3)
    tab.to_csv(os.path.join(TAB, "noise_summary.csv"))
    rows = []
    for sg in sorted(d.sigma.unique()):
        a = d[(d.sigma == sg) & (d.controller == "T1-FL(CSA)")].sort_values(["geo", "scenario"])
        b = d[(d.sigma == sg) & (d.controller == "IT2-FL(CSA)")].sort_values(["geo", "scenario"])
        try:
            pv = stats.wilcoxon(a["gain_vs_fixed_%"].values, b["gain_vs_fixed_%"].values).pvalue
        except ValueError:
            pv = 1.0
        rows.append({"sigma": sg, "T1_gain_%": a["gain_vs_fixed_%"].mean(), "IT2_gain_%": b["gain_vs_fixed_%"].mean(),
                     "T1_degr_%": a["degr_%"].mean(), "IT2_degr_%": b["degr_%"].mean(), "p_wilcoxon(18 scen.)": pv})
    pd.DataFrame(rows).round(4).to_csv(os.path.join(TAB, "noise_t1_vs_it2.csv"), index=False)
    print(pd.DataFrame(rows).round(3).to_string())
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True)
    for ax, g in zip(axes, ["3leg", "4leg"]):
        for c, col in (("T1-FL(CSA)", "#ff7f0e"), ("IT2-FL(CSA)", "#2ca02c")):
            s = d[(d.geo == g) & (d.controller == c)].groupby("sigma")["gain_vs_fixed_%"].agg(["mean", "std"])
            ax.errorbar(s.index * 100, s["mean"], yerr=s["std"] / np.sqrt(9), marker="o", ms=4, label=c, color=col, capsize=2)
        ax.axhline(0, color="k", lw=.7)
        ax.set_title(g); ax.set_xlabel("detector noise sigma (%)"); ax.grid(alpha=.3)
    axes[0].set_ylabel("delay reduction vs fixed FPA-TSC (%)"); axes[0].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "noise_robustness.png"), dpi=200); plt.close(fig)


def type_reduction_and_budget():
    p = os.path.join(TAB, "type_reduction_per_seed.csv")
    if os.path.exists(p):
        df = pd.read_csv(p)
        a = df[df.reduction == "km"].sort_values(["geo", "scenario", "seed"]).delay.values
        b = df[df.reduction == "nt"].sort_values(["geo", "scenario", "seed"]).delay.values
        pv = stats.wilcoxon(a, b).pvalue
        res = df.groupby(["geo", "reduction"])["delay"].mean().round(3)
        res.to_csv(os.path.join(TAB, "type_reduction_summary.csv"))
        with open(os.path.join(TAB, "type_reduction_test.txt"), "w") as fh:
            fh.write(f"KM mean={a.mean():.3f} NT mean={b.mean():.3f} Wilcoxon p={pv:.4f} (n={a.size} paired runs)\n")
        print(res, pv)
    p = os.path.join(TAB, "budget_study.csv")
    if os.path.exists(p):
        b = pd.read_csv(p)
        base = pd.read_csv(os.path.join(TAB, "baseline_per_seed.csv"))
        base = base[base.controller.isin(["T1-FL(CSA)", "IT2-FL(CSA)"])].groupby(["geo", "scenario", "controller"])["delay"].mean()
        b["test_delay_100it"] = [base[(r.geo, r.scenario, "T1-FL(CSA)" if r.kind == "t1" else "IT2-FL(CSA)")] for r in b.itertuples()]
        b.round(3).to_csv(os.path.join(TAB, "budget_study_summary.csv"), index=False)
        print(b.round(2).to_string())


if __name__ == "__main__":
    optimizer_comparison()
    noise()
    type_reduction_and_budget()
