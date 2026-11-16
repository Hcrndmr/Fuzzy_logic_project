"""Global constants of the simulation study.

Values marked [paper] are taken from Korkmaz & Akguengoer (2024), Soft Computing 28:7227-7249.
Values marked [assumption] are NOT given in the paper; they are my own modelling choices and are
documented in the report (Section 7, Experimental Setup).
"""
import numpy as np

# ---------------------------------------------------------------- simulation
SIM_TIME = 900.0            # [paper] 900 s simulation period (15 min)
APPROACH_LEN = 175.0        # [paper] detector range 175 m
V_FREE = 50.0 / 3.6         # [paper] free-flow speed 50 km/h
T_TRAVEL = APPROACH_LEN / V_FREE   # time to travel the detector range at free flow (12.6 s)
LANES_PER_LEG = 2           # [paper] two lanes per leg
SAT_FLOW = 1800.0           # [paper] veh/h/lane (passenger-car stream)
SAT_HEADWAY = 3600.0 / SAT_FLOW    # 2.0 s
STARTUP_LOST = 3.6          # [paper] start-up lost time
YELLOW = 2.0                # [paper]
ALL_RED = 1.0               # [paper]
LOST_PER_PHASE = ALL_RED + 2.0     # approx. lost time per phase used by Webster / HCM (assumption)
QUEUE_GAP = 2.0             # [assumption] standstill gap between queued vehicles (m)

# vehicle mix [paper]: 80 % car, 10 % minibus, 5 % bus, 3 % lorry, 2 % truck
VEH_NAMES = ["car", "minibus", "bus", "lorry", "truck"]
VEH_PROB = np.array([0.80, 0.10, 0.05, 0.03, 0.02])
VEH_LEN = np.array([5.0, 6.0, 12.0, 13.5, 8.5])      # [paper] Table 2 (m)
# headway multiplier relative to a car in the discharging queue [assumption]
# (the paper uses Synchro acceleration tables, which are not reproduced here)
VEH_HEADWAY_MULT = np.array([1.0, 1.15, 1.8, 2.0, 1.6])
MEAN_PCE = float(np.dot(VEH_PROB, VEH_HEADWAY_MULT))
SAT_FLOW_EFF = SAT_FLOW / MEAN_PCE                    # effective lane saturation flow, mixed stream

# ---------------------------------------------------------------- signal limits
G_MIN, G_MAX = 8.0, 60.0    # [paper] green limits used by the (phase) optimisation module
G_ABS_MIN, G_ABS_MAX = 5.0, 66.0   # [assumption] hard limits after fuzzy adjustment (+-6 s)
DELTA_MAX = 6.0             # [paper] green change in [-6, +6] s

# ---------------------------------------------------------------- fuzzy universes
CNT_RANGE = (0.0, 40.0)     # [paper] Fig. 7: number of vehicles (7 MFs)
QLEN_RANGE = (0.0, 175.0)   # [paper] Fig. 8: queue length in m (6 MFs)
N_CNT_MF, N_Q_MF = 7, 6     # [paper] -> 42 rules
OUT_VALUES = np.array([-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0])   # [paper] Table 8
LOWER_HEIGHT = 0.5          # [assumption, read from Figs. 7-8] height of lower MFs

# ---------------------------------------------------------------- scenarios [paper] Tables 9 and 10
SCENARIOS_3LEG = {   # veh/h on W, E, N
    "low_equal100": (100, 100, 100), "low_equal400": (400, 400, 400), "low_mixed": (100, 250, 400),
    "med_equal500": (500, 500, 500), "med_equal800": (800, 800, 800), "med_mixed": (650, 800, 800),
    "high_equal900": (900, 900, 900), "high_equal1200": (1200, 1200, 1200), "high_mixed": (900, 1050, 1050),
}
SCENARIOS_4LEG = {   # veh/h on W, E, N, S
    "low_equal100": (100, 100, 100, 100), "low_equal400": (400, 400, 400, 400), "low_mixed": (100, 250, 400, 400),
    "med_equal500": (500, 500, 500, 500), "med_equal800": (800, 800, 800, 800), "med_mixed": (650, 800, 800, 500),
    "high_equal900": (900, 900, 900, 900), "high_equal1200": (1200, 1200, 1200, 1200), "high_mixed": (900, 1050, 1050, 1200),
}
SCENARIOS = {"3leg": SCENARIOS_3LEG, "4leg": SCENARIOS_4LEG}

# ---------------------------------------------------------------- experiment protocol
TEST_SEEDS = list(range(1, 21))          # [paper] 20 different seeds for evaluation
TRAIN_SEEDS = [1001, 1002, 1003, 1004]   # [assumption] disjoint seeds used only inside the optimiser
