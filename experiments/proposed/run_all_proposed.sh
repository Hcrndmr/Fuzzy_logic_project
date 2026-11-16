#!/bin/bash
# Runs all extension experiments sequentially (about 35-45 minutes on 2 cores).
cd "$(dirname "$0")/../.."
python3 experiments/proposed/run_optimizer_comparison.py --runs 3 --pop 20 --iters 60
python3 experiments/proposed/run_noise_robustness.py
python3 experiments/proposed/run_budget_study.py
python3 experiments/proposed/run_type_reduction.py     # last: timing needs an idle machine
