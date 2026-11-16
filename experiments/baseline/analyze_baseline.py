"""Tables, statistics and figures of the reproduction experiment (reads results/tables/baseline_per_seed.csv)."""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from config import SCENARIOS                                  # noqa: E402

TAB = os.path.join(ROOT, "results", "tables")
FIG = os.path.join(ROOT, "results", "figures")
MAIN = ["FixedTime(Webster)", "FPA-TSC", "T1-FL(CSA)", "IT2-FL(CSA)"]
COL = {"FixedTime(Webster)": "#7f7f7f", "FPA-TSC": "#1f77b4", "T1-FL(CSA)": "#ff7f0e", "IT2-FL(CSA)": "#2ca02c"}
# numbers printed in Table 13 of the reference paper (|MPE|, %); sign convention: positive = improvement
PAPER = {"3leg": {"FT->T1": 8.64, "FT->FPA": 10.73, "FT->HTSC": 11.59, "T1->FPA": 1.67, "T1->HTSC": 2.70, "FPA->HTSC": 0.80},
         "4leg": {"FT->T1": 19.81, "FT->FPA": 20.27, "FT->HTSC": 23.99, "T1->FPA": 0.42, "T1->HTSC": 5.26, "FPA->HTSC": 4.83}}


def main():
    df = pd.read_csv(os.path.join(TAB, "baseline_per_seed.csv"))
    m = df.groupby(["geo", "scenario", "controller"])["delay"].agg(["mean", "std"]).reset_index()
    mean = m.pivot_table(index=["geo", "scenario"], columns="controller", values="mean")
    order = [(g, s) for g in SCENARIOS for s in SCENARIOS[g]]
    mean = mean.loc[order]
    mean.round(2).to_csv(os.path.join(TAB, "baseline_mean_delay_per_scenario.csv"))

    # ---- descriptive statistics over the 9 scenarios (cf. Table 11 of the paper)
    rows = []
    for g in SCENARIOS:
        sub = mean.loc[g]
        for c in sub.columns:
            rows.append({"geo": g, "controller": c, "mean": sub[c].mean(), "std": sub[c].std(ddof=1),
                         "min": sub[c].min(), "max": sub[c].max()})
    desc = pd.DataFrame(rows)
    desc.round(2).to_csv(os.path.join(TAB, "baseline_descriptive.csv"), index=False)

    # ---- MPE / improvement (Eq. 11, positive = better), cf. Table 13 of the paper
    def mpe(sub, ref, new):
        return float(np.mean(100.0 * (sub[ref] - sub[new]) / sub[ref]))

    imp = []
    for g in SCENARIOS:
        sub = mean.loc[g]
        pairs = {"FT->T1": ("FixedTime(Webster)", "T1-FL(CSA)"), "FT->FPA": ("FixedTime(Webster)", "FPA-TSC"),
                 "FT->IT2": ("FixedTime(Webster)", "IT2-FL(CSA)"), "T1->FPA": ("T1-FL(CSA)", "FPA-TSC"),
                 "T1->IT2": ("T1-FL(CSA)", "IT2-FL(CSA)"), "FPA->IT2": ("FPA-TSC", "IT2-FL(CSA)")}
        for k, (r, n) in pairs.items():
            imp.append({"geo": g, "comparison": k, "ours_%": mpe(sub, r, n), "paper_% (HTSC)": PAPER[g][k.replace("IT2", "HTSC")]})
    imp = pd.DataFrame(imp)
    imp.round(2).to_csv(os.path.join(TAB, "baseline_improvement_vs_paper.csv"), index=False)

    # ---- Friedman test over the 9 scenarios (cf. Table 12)
    fr = []
    for g in SCENARIOS:
        sub = mean.loc[g][MAIN]
        stat, p = stats.friedmanchisquare(*[sub[c].values for c in MAIN])
        ranks = sub.rank(axis=1).mean()
        fr.append({"geo": g, "chi2": stat, "p": p, **{f"rank[{c}]": ranks[c] for c in MAIN}})
    pd.DataFrame(fr).round(4).to_csv(os.path.join(TAB, "baseline_friedman.csv"), index=False)

    # ---- paired Wilcoxon per scenario: IT2 vs T1 (20 common-random-number seeds)
    wl = []
    for g, s in order:
        a = df[(df.geo == g) & (df.scenario == s) & (df.controller == "T1-FL(CSA)")].sort_values("seed").delay.values
        b = df[(df.geo == g) & (df.scenario == s) & (df.controller == "IT2-FL(CSA)")].sort_values("seed").delay.values
        f = df[(df.geo == g) & (df.scenario == s) & (df.controller == "FPA-TSC")].sort_values("seed").delay.values
        try:
            p1 = stats.wilcoxon(a, b).pvalue
        except ValueError:
            p1 = 1.0
        try:
            p2 = stats.wilcoxon(f, b).pvalue
        except ValueError:
            p2 = 1.0
        wl.append({"geo": g, "scenario": s, "T1": a.mean(), "IT2": b.mean(), "IT2_vs_T1_%": 100 * (a.mean() - b.mean()) / a.mean(),
                   "p(IT2 vs T1)": p1, "FPA-TSC": f.mean(), "IT2_vs_FPA_%": 100 * (f.mean() - b.mean()) / f.mean(),
                   "p(IT2 vs FPA)": p2})
    pd.DataFrame(wl).round(4).to_csv(os.path.join(TAB, "baseline_wilcoxon.csv"), index=False)

    # ---- ablation: uniform vs optimised MFs, PSS
    ab = mean.groupby(level=0).mean()[["T1-FL(uniform MF)", "T1-FL(CSA)", "IT2-FL(uniform MF)", "IT2-FL(CSA)", "IT2-FL(CSA)+PSS"]]
    ab.round(2).to_csv(os.path.join(TAB, "baseline_ablation_mf_opt_pss.csv"))

    # ---- figures
    for g, title in (("3leg", "Three-leg intersection"), ("4leg", "Four-leg intersection")):
        sub = mean.loc[g][MAIN]
        x = np.arange(len(sub))
        w = 0.2
        fig, ax = plt.subplots(figsize=(7.2, 3.6))
        for k, c in enumerate(MAIN):
            ax.bar(x + (k - 1.5) * w, sub[c].values, w, label=c, color=COL[c])
        ax.set_xticks(x)
        ax.set_xticklabels([str(i + 1) for i in x])
        ax.set_xlabel("Traffic scenario (1-3 low, 4-6 medium, 7-9 high; Tables 9/10 of the paper)")
        ax.set_ylabel("Average delay (s/veh)")
        ax.set_title(title + " - mean of 20 seeds")
        ax.legend(fontsize=8, ncol=2)
        ax.grid(axis="y", alpha=.3)
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, f"baseline_delay_{g}.png"), dpi=200)
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True)
    for ax, g in zip(axes, SCENARIOS):
        sub = mean.loc[g]
        ax.axhline(0, color="k", lw=.6)
        ax.bar(np.arange(9) - .2, 100 * (sub["T1-FL(CSA)"] - sub["IT2-FL(CSA)"]) / sub["T1-FL(CSA)"], .4, label="IT2 vs T1", color="#2ca02c")
        ax.bar(np.arange(9) + .2, 100 * (sub["FPA-TSC"] - sub["IT2-FL(CSA)"]) / sub["FPA-TSC"], .4, label="IT2 vs FPA-TSC (fixed)", color="#1f77b4")
        ax.set_xticks(range(9))
        ax.set_xticklabels([str(i + 1) for i in range(9)])
        ax.set_title(g)
        ax.set_xlabel("scenario")
        ax.grid(axis="y", alpha=.3)
    axes[0].set_ylabel("delay reduction (%)")
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "baseline_it2_improvement.png"), dpi=200)
    plt.close(fig)
    print(desc.round(2).to_string())
    print(imp.round(2).to_string())
    print(pd.DataFrame(fr).round(3).to_string())
    print(pd.DataFrame(wl).round(3).to_string())
    print(ab.round(2).to_string())


if __name__ == "__main__":
    main()
