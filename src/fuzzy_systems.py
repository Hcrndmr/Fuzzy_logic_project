"""Type-1 and interval Type-2 Sugeno fuzzy green-time controllers.

Inputs : number of vehicles in the detector range (7 triangular MFs on [0, 40])
         queue length in metres               (6 triangular MFs on [0, 175])
Rules  : 7 x 6 = 42 rules, "IF count is MFi AND queue is MFj THEN green_change is z_ij"  (min t-norm)
Output : Sugeno singletons z in {-6,-4,-2,0,2,4,6} s (Table 8 of the reference paper)

The paper does not publish its rule table.  The table used here is my own monotone design:
the longer the queue and the more vehicles, the more green is added (see rule_table()).

Parameter vectors live in the unit hyper-cube [0,1]^D so that any metaheuristic can optimise them.
"""
import numpy as np

from config import (CNT_RANGE, QLEN_RANGE, N_CNT_MF, N_Q_MF, OUT_VALUES, LOWER_HEIGHT)

# --------------------------------------------------------------------------- rule base


def rule_table():
    """Consequent index (0..6) for every (count MF i, queue MF j)."""
    tab = np.zeros((N_CNT_MF, N_Q_MF), dtype=int)
    for i in range(N_CNT_MF):
        for j in range(N_Q_MF):
            s = 0.5 * (i / (N_CNT_MF - 1) + j / (N_Q_MF - 1))
            tab[i, j] = int(round(s * (len(OUT_VALUES) - 1)))
    return tab


RULE_Z = OUT_VALUES[rule_table()].ravel()          # 42 crisp consequents (row-major: count major)
_ORDER = np.argsort(RULE_Z, kind="stable")         # fixed ascending order needed by Karnik-Mendel
Z_SORTED = RULE_Z[_ORDER]

# --------------------------------------------------------------------------- parameter encoding
# per input variable with K MFs:  K centres, K left legs, K right legs [, K lower-left, K lower-right]
W_MIN, W_MAX = 0.03, 0.60       # leg width limits as a fraction of the universe
F_MIN, F_MAX = 0.05, 1.00       # lower-leg width as a fraction of the upper leg (IT2)


def n_params(kind):
    per = 3 if kind == "t1" else 5
    return per * (N_CNT_MF + N_Q_MF)


def _decode_var(u, K, lo, hi, kind):
    """u: slice of the unit-cube vector for one variable -> dict of MF parameter arrays (absolute units)."""
    rng = hi - lo
    c = lo + rng * np.sort(u[:K])
    wl = (W_MIN + (W_MAX - W_MIN) * u[K:2 * K]) * rng
    wr = (W_MIN + (W_MAX - W_MIN) * u[2 * K:3 * K]) * rng
    out = {"c": c, "wl": wl, "wr": wr}
    if kind == "it2":
        out["fl"] = F_MIN + (F_MAX - F_MIN) * u[3 * K:4 * K]
        out["fr"] = F_MIN + (F_MAX - F_MIN) * u[4 * K:5 * K]
    return out


def decode(vec, kind):
    vec = np.asarray(vec, dtype=float)
    per = 3 if kind == "t1" else 5
    a = per * N_CNT_MF
    return (_decode_var(vec[:a], N_CNT_MF, *CNT_RANGE, kind),
            _decode_var(vec[a:], N_Q_MF, *QLEN_RANGE, kind))


def default_vector(kind, fou=0.6):
    """Uniformly spaced triangular MFs (adjacent MFs cross at 0.5); IT2 lower legs = fou * upper legs."""
    parts = []
    for K in (N_CNT_MF, N_Q_MF):
        centres = np.linspace(0.0, 1.0, K)
        leg_frac = 1.0 / (K - 1)
        u_leg = (leg_frac - W_MIN) / (W_MAX - W_MIN)
        blocks = [centres, np.full(K, u_leg), np.full(K, u_leg)]
        if kind == "it2":
            u_f = (fou - F_MIN) / (F_MAX - F_MIN)
            blocks += [np.full(K, u_f), np.full(K, u_f)]
        parts.append(np.concatenate(blocks))
    return np.concatenate(parts)


# --------------------------------------------------------------------------- membership functions


def tri(x, c, wl, wr):
    """Triangular MF with apex c, left leg wl, right leg wr (peak value 1) evaluated at scalar x."""
    left = (x - (c - wl)) / wl
    right = ((c + wr) - x) / wr
    return np.clip(np.minimum(left, right), 0.0, 1.0)


# --------------------------------------------------------------------------- inference


class Type1Sugeno:
    kind = "t1"

    def __init__(self, vec):
        self.cnt, self.q = decode(vec, "t1")

    def __call__(self, count, qlen):
        mc = tri(count, self.cnt["c"], self.cnt["wl"], self.cnt["wr"])
        mq = tri(qlen, self.q["c"], self.q["wl"], self.q["wr"])
        w = np.minimum.outer(mc, mq).ravel()
        s = w.sum()
        if s <= 1e-9:
            return 0.0                       # no rule fires -> keep the base green time
        return float(np.dot(w, RULE_Z) / s)


class IntervalType2Sugeno:
    """Interval Type-2 Sugeno with exact Karnik-Mendel (default) or Nie-Tan type reduction."""
    kind = "it2"

    def __init__(self, vec, reduction="km"):
        self.cnt, self.q = decode(vec, "it2")
        self.reduction = reduction

    @staticmethod
    def _lower(p, x):
        return LOWER_HEIGHT * tri(x, p["c"], p["wl"] * p["fl"], p["wr"] * p["fr"])

    def firing(self, count, qlen):
        mcu = tri(count, self.cnt["c"], self.cnt["wl"], self.cnt["wr"])
        mqu = tri(qlen, self.q["c"], self.q["wl"], self.q["wr"])
        mcl = self._lower(self.cnt, count)
        mql = self._lower(self.q, qlen)
        wu = np.minimum.outer(mcu, mqu).ravel()
        wl = np.minimum.outer(mcl, mql).ravel()
        return wl, wu

    def __call__(self, count, qlen):
        wl, wu = self.firing(count, qlen)
        if wu.sum() <= 1e-9:
            return 0.0
        wl = wl[_ORDER]
        wu = wu[_ORDER]
        if self.reduction == "nt":
            return nie_tan(Z_SORTED, wl, wu)
        yl, yr = karnik_mendel(Z_SORTED, wl, wu)
        return 0.5 * (yl + yr)


def karnik_mendel(z, wl, wu):
    """Exact end points [y_l, y_r] of the Sugeno IT2 output (z sorted ascending).

    The KM iteration converges to the optimum over all switch points k, which is evaluated here directly
    with prefix sums (verified against brute force enumeration in tests/test_fuzzy.py).
    """
    zwu = z * wu
    zwl = z * wl
    cu = np.concatenate([[0.0], np.cumsum(zwu)])
    cl = np.concatenate([[0.0], np.cumsum(zwl)])
    wcu = np.concatenate([[0.0], np.cumsum(wu)])
    wcl = np.concatenate([[0.0], np.cumsum(wl)])
    # y_l: upper weights for i < k, lower weights for i >= k
    num = cu + (cl[-1] - cl)
    den = wcu + (wcl[-1] - wcl)
    ok = den > 1e-12
    yl = np.min(num[ok] / den[ok]) if ok.any() else 0.0
    # y_r: lower weights for i < k, upper weights for i >= k
    num = cl + (cu[-1] - cu)
    den = wcl + (wcu[-1] - wcu)
    ok = den > 1e-12
    yr = np.max(num[ok] / den[ok]) if ok.any() else 0.0
    return float(yl), float(yr)


def nie_tan(z, wl, wu):
    w = 0.5 * (wl + wu)
    s = w.sum()
    return float(np.dot(w, z) / s) if s > 1e-12 else 0.0
