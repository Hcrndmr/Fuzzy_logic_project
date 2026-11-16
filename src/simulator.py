"""Event-based mesoscopic simulator of an isolated signalised intersection.

This is NOT a re-implementation of KU-Trsim (the simulator of the reference paper is not public).
It reproduces the aspects needed by the fuzzy controller: exponential arrivals, mixed vehicle types,
a 175 m detector range, queue length in metres, saturation headway, start-up lost time, yellow and
all-red intervals.  Split phasing is used: every approach gets its own phase.

Delay definition: d_i = (time the vehicle crosses the stop line) - (time it would cross at free flow).
Vehicles still queued at the end of the simulation contribute (T_end - free-flow arrival).
"""
from bisect import bisect_right
import numpy as np

from config import (SIM_TIME, T_TRAVEL, LANES_PER_LEG, SAT_HEADWAY, STARTUP_LOST, YELLOW, ALL_RED,
                    VEH_PROB, VEH_LEN, VEH_HEADWAY_MULT, QUEUE_GAP, G_ABS_MIN, G_ABS_MAX,
                    CNT_RANGE, QLEN_RANGE)


class Lane:
    __slots__ = ("gen", "arr", "h", "cq", "csarr", "n")

    def __init__(self, gen, length, hmult):
        self.gen = gen.tolist()                       # time the vehicle enters the 175 m range
        arr = gen + T_TRAVEL
        self.arr = arr.tolist()                       # free-flow arrival at the stop line
        self.h = (SAT_HEADWAY * hmult).tolist()       # discharge headway of each vehicle
        self.cq = np.concatenate([[0.0], np.cumsum(length + QUEUE_GAP)]).tolist()   # cumulative queue metres
        self.csarr = np.concatenate([[0.0], np.cumsum(arr)]).tolist()
        self.n = len(self.gen)


class Instance:
    """One random realisation of the demand (volumes, seed)."""

    def __init__(self, volumes, seed, T=SIM_TIME):
        rng = np.random.default_rng(seed)
        self.volumes = tuple(volumes)
        self.legs = []
        self.n_veh = 0
        for q in volumes:
            n_est = int(q / 3600.0 * T * 2) + 60
            gen = np.cumsum(rng.exponential(3600.0 / q, size=n_est))      # exponential headways
            gen = gen[gen <= T - T_TRAVEL]
            vt = rng.choice(len(VEH_PROB), size=gen.size, p=VEH_PROB)
            lane_id = rng.integers(0, LANES_PER_LEG, size=gen.size)
            lanes = []
            for li in range(LANES_PER_LEG):
                m = lane_id == li
                lanes.append(Lane(gen[m], VEH_LEN[vt[m]], VEH_HEADWAY_MULT[vt[m]]))
                self.n_veh += lanes[-1].n
            self.legs.append(lanes)


_CACHE = {}


def get_instance(volumes, seed):
    key = (tuple(volumes), seed)
    if key not in _CACHE:
        if len(_CACHE) > 4000:
            _CACHE.clear()
        _CACHE[key] = Instance(volumes, seed)
    return _CACHE[key]


def observe(leg, ptr, t):
    """Detector information of one leg at time t: (vehicles in range, queue length in m), max over lanes."""
    cnt = 0.0
    qlen = 0.0
    tot = 0
    for li, lane in enumerate(leg):
        p = ptr[li]
        nr = bisect_right(lane.gen, t) - p
        nq = bisect_right(lane.arr, t) - p
        q = lane.cq[p + nq] - lane.cq[p]
        cnt = max(cnt, nr)
        qlen = max(qlen, q)
        tot += nr
    return cnt, qlen, tot


def simulate(inst, base_green, fis=None, pss=False, noise=0.0, noise_rng=None, T=SIM_TIME, return_info=False):
    """Run one simulation.

    base_green : list of base green times (s), one per phase/leg
    fis        : callable (n_vehicles, queue_length_m) -> green change in s, or None (fixed time)
    pss        : phase-sequence selection (serve the not-yet-served phase with most vehicles first)
    noise      : relative std of multiplicative Gaussian detector noise
    Returns the average delay per vehicle (s/veh).
    """
    legs = inst.legs
    n = len(legs)
    ptr = [[0] * LANES_PER_LEG for _ in range(n)]
    total_delay = 0.0
    t = 0.0
    n_phases = 0
    green_sum = 0.0
    while t < T:
        remaining = list(range(n))
        while remaining and t < T:
            if pss and len(remaining) > 1:
                best, bval = remaining[0], -1.0
                for ph in remaining:
                    c, q, tot = observe(legs[ph], ptr[ph], t)
                    if noise > 0.0:
                        tot = max(0.0, tot * (1.0 + noise * noise_rng.standard_normal()))
                    if tot > bval:
                        best, bval = ph, tot
                ph = best
            else:
                ph = remaining[0]
            remaining.remove(ph)
            g = base_green[ph]
            if fis is not None:
                c, q, _ = observe(legs[ph], ptr[ph], t)
                if noise > 0.0:
                    c = max(0.0, c * (1.0 + noise * noise_rng.standard_normal()))
                    q = max(0.0, q * (1.0 + noise * noise_rng.standard_normal()))
                c = min(c, CNT_RANGE[1])
                q = min(q, QLEN_RANGE[1])
                g = min(max(g + fis(c, q), G_ABS_MIN), G_ABS_MAX)
            ge = t + g + YELLOW                 # vehicles may still cross during the yellow interval
            for li, lane in enumerate(legs[ph]):
                p = ptr[ph][li]
                arr, h, N = lane.arr, lane.h, lane.n
                prev = None
                while p < N and arr[p] <= ge:
                    if prev is None:
                        td = t + STARTUP_LOST if arr[p] <= t else arr[p]    # queue discharge vs. free flow
                    else:
                        td = arr[p] if arr[p] > prev + h[p] else prev + h[p]
                    if td > ge or td > T:
                        break
                    total_delay += td - arr[p]
                    prev = td
                    p += 1
                ptr[ph][li] = p
            t = ge + ALL_RED
            n_phases += 1
            green_sum += g
    # vehicles still in the system at the end of the simulation
    for ph in range(n):
        for li, lane in enumerate(legs[ph]):
            p = ptr[ph][li]
            total_delay += T * (lane.n - p) - (lane.csarr[lane.n] - lane.csarr[p])
    avg = total_delay / inst.n_veh if inst.n_veh else 0.0
    if return_info:
        return avg, {"phases": n_phases, "mean_green": green_sum / max(n_phases, 1)}
    return avg
