"""
Benchmark script for HVAC: 7R2C (VDI 6007)

This script tests the performance of the 7R2C method with many HVAC objects.
It generates synthetic HVAC objects with varying parameters, uses the R7C2
method to generate time series for all objects, and measures the execution time.

It mirrors the style of examples/hvac_1r1c/benchmark_1r1c.py.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

# Ensure project root on sys.path for direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from entise.constants import Objects as O
from entise.core.generator import TimeSeriesGenerator


def generate_hvac_objects(num_objects: int = 100, seed: int = 42) -> pd.DataFrame:
    """Generate 7R2C HVAC objects with varying parameters.
    """
    rng = np.random.default_rng(seed)

    objs: list[dict] = []
    gains_columns = ["residential", "office", "commercial", "industrial"]

    for i in range(num_objects):
        # 7R2C RC parameters (resistances in K/W, capacities in J/K)
        R1AW = float(rng.uniform(0.05, 0.30))   # AW mass↔surface
        C1AW = float(rng.uniform(8.0e5, 3.0e6))
        R1IW = float(rng.uniform(0.08, 0.40))   # IW mass↔surface
        C1IW = float(rng.uniform(5.0e5, 2.0e6))

        RalphaStarIL = float(rng.uniform(0.005, 0.025))  # air↔star (internal film)
        RalphaStarAW = float(rng.uniform(0.005, 0.025))  # AW surf↔star
        RalphaStarIW = float(rng.uniform(0.005, 0.025))  # IW surf↔star
        RrestAW      = float(rng.uniform(0.05, 0.50))    # remainder to T_eq

        # Ventilation total (W/K) and split (fraction to mechanical branch)
        Hve_total = float(rng.uniform(40.0, 250.0))
        vent_split = float(rng.uniform(0.6, 1.0))  # commonly mostly mechanical

        # Controls
        temp_init = float(rng.uniform(19.0, 22.0))
        temp_min  = float(rng.uniform(19.0, 22.0))
        temp_max  = float(rng.uniform(23.0, 26.0))

        # Geometry for air capacity and auxiliaries
        area   = float(rng.uniform(120.0, 2000.0))
        height = float(rng.uniform(2.5, 3.5))
        lat = 49.72 + float(rng.uniform(-0.02, 0.02))
        lon = 11.05 + float(rng.uniform(-0.02, 0.02))

        # Internal gains: half constant, half schedule reference
        if rng.random() < 0.5:
            gains_internal = float(rng.uniform(50.0, 1200.0))
            gains_internal_col = ""
        else:
            gains_internal = "internal_gains"
            gains_internal_col = str(rng.choice(gains_columns))

        # HVAC sigma (three-way). Provide AW and IW; conv will be derived in the method.
        sigma_aw = float(rng.uniform(0.10, 0.40))
        sigma_iw = float(rng.uniform(0.05, 0.35))
        if sigma_aw + sigma_iw > 0.95:
            scale = 0.95 / (sigma_aw + sigma_iw)
            sigma_aw *= scale
            sigma_iw *= scale

        # Radiant gains split between AW and IW
        f_rad_aw = float(rng.uniform(0.5, 0.8))

        obj = {
            O.ID: f"hvac7_{i+1}",
            "hvac": "7R2C",
            O.WEATHER: "weather",
            # RC network
            O.R_1_AW: R1AW,
            O.C_1_AW: C1AW,
            O.R_1_IW: R1IW,
            O.C_1_IW: C1IW,
            O.R_ALPHA_STAR_IL: RalphaStarIL,
            O.R_ALPHA_STAR_AW: RalphaStarAW,
            O.R_ALPHA_STAR_IW: RalphaStarIW,
            O.R_REST_AW: RrestAW,
            # Ventilation
            O.VENTILATION: Hve_total,
            O.VENTILATION_SPLIT: vent_split,
            # Controls
            O.TEMP_INIT: temp_init,
            O.TEMP_MIN: temp_min,
            O.TEMP_MAX: temp_max,
            O.POWER_HEATING: float("inf"),
            O.POWER_COOLING: float("inf"),
            O.ACTIVE_HEATING: True,
            O.ACTIVE_COOLING: True,
            # Geometry
            O.AREA: area,
            O.HEIGHT: height,
            O.LAT: lat,
            O.LON: lon,
            # Keep SolarGains auxiliary off for this synthetic benchmark (T_eq computation still uses GHI)
            O.ACTIVE_GAINS_SOLAR: False,
            # Splits
            O.SIGMA_7R2C_AW: sigma_aw,
            O.SIGMA_7R2C_IW: sigma_iw,
            O.FRAC_CONV_INTERNAL: 0.5,
            O.FRAC_RAD_AW: f_rad_aw,  # IW derived as (1 - f_rad_aw)
            # T_eq parameters if not provided as series
            O.T_EQ_ALPHA_SW: 0.6,
            O.T_EQ_H_O: 20.0,
        }
        objs.append(obj)

    return pd.DataFrame(objs)


def run_benchmark(num_objects: int = 100, workers: int = 1) -> tuple[float, pd.DataFrame, dict]:
    """Run the 7R2C benchmark with a given number of objects and workers."""
    objects = generate_hvac_objects(num_objects)

    # Load data
    cwd = "."
    data: dict[str, pd.DataFrame] = {}

    # Common weather
    common_data_folder = "../common_data"
    for file in os.listdir(os.path.join(cwd, common_data_folder)):
        if file.endswith(".csv"):
            name = file.split(".")[0]
            data[name] = pd.read_csv(os.path.join(cwd, common_data_folder, file), parse_dates=True)

    # Local example data if any (windows not required for solver-only benchmark)
    data_folder = "data"
    if os.path.isdir(os.path.join(cwd, data_folder)):
        for file in os.listdir(os.path.join(cwd, data_folder)):
            if file.endswith(".csv"):
                name = file.split(".")[0]
                data[name] = pd.read_csv(os.path.join(cwd, data_folder, file), parse_dates=True)

    # Configure generator
    gen = TimeSeriesGenerator()
    gen.add_objects(objects)

    # Execute and time
    t0 = time.time()
    summary, out = gen.generate(data, workers=workers)
    t1 = time.time()

    exec_time = t1 - t0

    return exec_time, summary, out


if __name__ == "__main__":
    # Run two configurations to estimate parallel speedup
    print("Running 7R2C benchmark with 1 worker…")
    t1, _, _ = run_benchmark(num_objects=100, workers=1)
    print(f"Runtime (1 worker): {t1:.2f} s")

    print("\nRunning 7R2C benchmark with 4 workers…")
    t4, _, _ = run_benchmark(num_objects=100, workers=4)
    print(f"Runtime (4 workers): {t4:.2f} s")

    # Print speedup
    speedup = t1 / t4
    print(f"\nSpeedup with 4 workers: {speedup:.2f}x")
