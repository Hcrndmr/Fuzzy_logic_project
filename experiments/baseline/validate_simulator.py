"""Sanity check of the simulator against the HCM delay model (Eqs. 7-9 of the reference paper).

Fixed-time control, equal flows on all legs, undersaturated to near-saturated demand.  We compare the
simulated mean delay (20 seeds) with the flow-weighted HCM control delay for the same green times.
usage: python experiments/baseline/validate_simulator.py
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from config import TEST_SEEDS                                   # noqa: E402
from simulator import get_instance, simulate                    # noqa: E402
from signal_plans import webster_greens, hcm_delay              # noqa: E402

rows = []
for n_leg in (3, 4):
    for q in range(100, 801, 100):
        vol = (q,) * n_leg
        g = webster_greens(vol)
        sim = np.mean([simulate(get_instance(vol, s), list(g)) for s in TEST_SEEDS])
        hcm, X = hcm_delay(vol, g)
        rows.append({"legs": n_leg, "flow_per_leg": q, "green_s": round(float(g[0]), 1), "X_max": round(X, 2),
                     "sim_delay": sim, "hcm_delay": hcm})
df = pd.DataFrame(rows)
r = np.corrcoef(df.sim_delay, df.hcm_delay)[0, 1]
mape = float(np.mean(np.abs(df.sim_delay - df.hcm_delay) / df.hcm_delay) * 100)
df.round(2).to_csv(os.path.join(ROOT, "results", "tables", "simulator_vs_hcm.csv"), index=False)
print(df.round(2).to_string()); print("R2 = %.3f   MAPE = %.1f %%" % (r ** 2, mape))
fig, ax = plt.subplots(figsize=(3.6, 3.4))
for n_leg, m in ((3, "o"), (4, "s")):
    s = df[df.legs == n_leg]
    ax.scatter(s.hcm_delay, s.sim_delay, marker=m, label=f"{n_leg}-leg")
mx = max(df.hcm_delay.max(), df.sim_delay.max())
ax.plot([0, mx], [0, mx], "k--", lw=.7)
ax.set_xlabel("HCM delay (s/veh)"); ax.set_ylabel("simulated delay (s/veh)")
ax.set_title("R$^2$=%.3f, MAPE=%.1f%%" % (r ** 2, mape), fontsize=9); ax.legend(fontsize=8); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "results", "figures", "simulator_vs_hcm.png"), dpi=200)
