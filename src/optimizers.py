"""Population based optimisers on the unit hyper-cube [0,1]^D (minimisation).

All optimisers share the same interface and evaluate exactly  pop * (iters + 1)  candidate solutions
(initial population + one candidate per member and iteration), so comparisons use an equal budget.
Returns (best_x, best_f, history) with history = best-so-far fitness after every iteration.

csa : Crow Search Algorithm        (Askarzadeh, 2016)   AP = 0.05, fl = 2   [values used in the reference paper]
fpa : Flower Pollination Algorithm (Yang, 2012)          p = 0.8, lambda = 1.5, gamma = 0.1
pso : Particle Swarm Optimisation  (Kennedy & Eberhart)  w = 0.7298, c1 = c2 = 1.49618
de  : Differential Evolution       (Storn & Price)       rand/1/bin, F = 0.5, CR = 0.9
"""
from math import gamma, sin, pi
import numpy as np


def _init_pop(rng, dim, pop, x0, sigma):
    """First member is x0 (the uniform-MF design), the others are Gaussian perturbations of it."""
    if x0 is None:
        return rng.random((pop, dim))
    X = np.clip(x0 + sigma * rng.standard_normal((pop, dim)), 0.0, 1.0)
    X[0] = x0
    return X


def csa(f, dim, pop=16, iters=40, seed=0, x0=None, init_sigma=0.15, AP=0.05, fl=2.0):
    rng = np.random.default_rng(seed)
    X = _init_pop(rng, dim, pop, x0, init_sigma)
    M = X.copy()
    fM = np.array([f(x) for x in M])
    hist = [fM.min()]
    for _ in range(iters):
        for i in range(pop):
            j = rng.integers(pop)
            if rng.random() >= AP:                       # crow j does not notice it is followed
                new = X[i] + rng.random() * fl * (M[j] - X[i])
            else:                                        # crow j fools the follower: random position
                new = rng.random(dim)
            new = np.clip(new, 0.0, 1.0)
            X[i] = new
            fn = f(new)
            if fn < fM[i]:
                M[i], fM[i] = new, fn
        hist.append(fM.min())
    k = int(np.argmin(fM))
    return M[k].copy(), float(fM[k]), hist


def _levy(rng, dim, beta=1.5):
    sigma = (gamma(1 + beta) * sin(pi * beta / 2) / (gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
    u = rng.standard_normal(dim) * sigma
    v = rng.standard_normal(dim)
    return u / np.abs(v) ** (1 / beta)


def fpa(f, dim, pop=16, iters=40, seed=0, x0=None, init_sigma=0.15, p=0.8, gam=0.1):
    rng = np.random.default_rng(seed)
    X = _init_pop(rng, dim, pop, x0, init_sigma)
    fX = np.array([f(x) for x in X])
    hist = [fX.min()]
    for _ in range(iters):
        g = X[int(np.argmin(fX))].copy()
        for i in range(pop):
            if rng.random() < p:                          # global pollination (Levy flight), Eq. (1)
                new = X[i] + gam * _levy(rng, dim) * (g - X[i])
            else:                                         # local pollination, Eq. (3)
                a, b = rng.choice(pop, 2, replace=False)
                new = X[i] + rng.random() * (X[a] - X[b])
            new = np.clip(new, 0.0, 1.0)
            fn = f(new)
            if fn < fX[i]:
                X[i], fX[i] = new, fn
        hist.append(fX.min())
    k = int(np.argmin(fX))
    return X[k].copy(), float(fX[k]), hist


def pso(f, dim, pop=16, iters=40, seed=0, x0=None, init_sigma=0.15, w=0.7298, c1=1.49618, c2=1.49618):
    rng = np.random.default_rng(seed)
    X = _init_pop(rng, dim, pop, x0, init_sigma)
    V = np.zeros((pop, dim))
    fX = np.array([f(x) for x in X])
    P, fP = X.copy(), fX.copy()
    hist = [fP.min()]
    for _ in range(iters):
        g = P[int(np.argmin(fP))]
        for i in range(pop):
            V[i] = w * V[i] + c1 * rng.random(dim) * (P[i] - X[i]) + c2 * rng.random(dim) * (g - X[i])
            V[i] = np.clip(V[i], -0.25, 0.25)
            X[i] = np.clip(X[i] + V[i], 0.0, 1.0)
            fn = f(X[i])
            if fn < fP[i]:
                P[i], fP[i] = X[i].copy(), fn
        hist.append(fP.min())
    k = int(np.argmin(fP))
    return P[k].copy(), float(fP[k]), hist


def de(f, dim, pop=16, iters=40, seed=0, x0=None, init_sigma=0.15, F=0.5, CR=0.9):
    rng = np.random.default_rng(seed)
    X = _init_pop(rng, dim, pop, x0, init_sigma)
    fX = np.array([f(x) for x in X])
    hist = [fX.min()]
    for _ in range(iters):
        for i in range(pop):
            a, b, c = rng.choice([k for k in range(pop) if k != i], 3, replace=False)
            mutant = X[a] + F * (X[b] - X[c])
            cross = rng.random(dim) < CR
            cross[rng.integers(dim)] = True
            trial = np.clip(np.where(cross, mutant, X[i]), 0.0, 1.0)
            ft = f(trial)
            if ft <= fX[i]:
                X[i], fX[i] = trial, ft
        hist.append(fX.min())
    k = int(np.argmin(fX))
    return X[k].copy(), float(fX[k]), hist


OPTIMIZERS = {"CSA": csa, "FPA": fpa, "PSO": pso, "DE": de}
