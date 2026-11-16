"""Draws the architecture figure used in the report and presentation."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
G, N = "#cfe8cf", "#dddddd"
fig, ax = plt.subplots(figsize=(7.6, 3.5))
ax.set_xlim(0, 100); ax.set_ylim(0, 46); ax.axis("off")


def box(x, y, w, h, text, c):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=c, ec="k", lw=.8))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7.2)


def arr(x1, y1, x2, y2, both=False):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="<->" if both else "->", mutation_scale=9, lw=.9))


box(1, 31, 20, 11, "Intersection geometry\nand traffic volumes\n(Tables 9-10)", G)
box(28, 31, 25, 11, "Phase optimisation\n(FPA, HCM delay)\nhere: green times only", N)
box(60, 31, 19, 11, "Phase sequence\nselection (PSS)\noptional extra", G)
box(33, 14, 22, 11, "Traffic simulator\n(own mesoscopic\nsimulator)", G)
box(63, 14, 35, 11, "Green-time optimisation\nIT2 Sugeno (vehicles, queue)\n42 rules, change in [-6,+6] s", G)
box(63, 0.5, 35, 8, "CSA tunes upper/lower MFs\nper scenario (offline)", G)
box(1, 14, 22, 11, "Delay per vehicle,\nsignal times", G)
arr(21.6, 36.5, 27.4, 36.5); arr(40.5, 30.5, 44, 25.6); arr(70, 30.5, 55.8, 22, True)
arr(55.6, 19.5, 62.4, 19.5, True); arr(80, 8.9, 80, 13.4); arr(32.4, 19.5, 23.6, 19.5)
ax.text(1, 5, "green = re-implemented in this project\ngrey = reduced (FPA only tunes greens;\nphase plan is fixed to split phasing)", fontsize=7, va="center",
        bbox=dict(fc="white", ec="k", lw=.5))
ax.text(58, 27.5, "control after\neach phase", fontsize=6.5, ha="center")
fig.savefig(os.path.join(ROOT, "report", "fig_architecture.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(ROOT, "results", "figures", "architecture.png"), dpi=200, bbox_inches="tight")
