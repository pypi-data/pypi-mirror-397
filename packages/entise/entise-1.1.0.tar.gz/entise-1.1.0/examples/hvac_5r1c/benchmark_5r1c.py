"""
Benchmark script for HVAC: 5R1C (ISO 13790)

This script tests the performance of the 5R1C method with many HVAC objects.
It generates synthetic HVAC objects with varying parameters, uses the R5C1
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
    """Generate 5R1C HVAC objects with varying parameters.
    """
    rng = np.random.default_rng(seed)

    objs: list[dict] = []

    # Choose internal gains columns from the shared dataset
    gains_columns = ["residential", "office", "commercial", "industrial"]

    for i in range(num_objects):
        # Reasonable aggregated RC parameters for 5R1C (ISO 13790)
        Htr_is = float(rng.uniform(300.0, 900.0))      # W/K (air↔surfaces)
        Htr_ms = float(rng.uniform(900.0, 2000.0))     # W/K (surfaces↔mass)
        Htr_em = float(rng.uniform(500.0, 1200.0))     # W/K (mass↔outdoor)
        Htr_w  = float(rng.uniform(10.0, 60.0))        # W/K (glazing)
        C_m    = float(rng.uniform(2.0e7, 8.0e7))      # J/K  (mass)

        # Ventilation conductance (W/K)
        ventilation = float(rng.uniform(40.0, 250.0))

        # Temperature setpoints
        temp_init = float(rng.uniform(19.0, 22.0))
        temp_min  = float(rng.uniform(19.0, 22.0))
        temp_max  = float(rng.uniform(23.0, 26.0))

        # Geometry (for air capacity and auxiliaries if needed)
        area   = float(rng.uniform(120.0, 2000.0))
        height = float(rng.uniform(2.5, 3.5))
        lat = 49.72 + float(rng.uniform(-0.02, 0.02))
        lon = 11.05 + float(rng.uniform(-0.02, 0.02))

        # Internal gains: 50% constant vs 50% referenced schedule
        if rng.random() < 0.5:
            gains_internal = float(rng.uniform(50.0, 1200.0))
            gains_internal_col = ""
        else:
            gains_internal = "internal_gains"  # reference dataset key
            gains_internal_col = str(rng.choice(gains_columns))

        # HVAC sigma: keep simple; convective HVAC (ideal loads) is common → surface sigma small
        sigma_surface = float(rng.uniform(0.0, 0.2))

        obj = {
            O.ID: f"hvac5_{i+1}",
            "hvac": "5R1C",
            O.WEATHER: "weather",
            # RC parameters
            O.H_TR_IS: Htr_is,
            O.H_TR_MS: Htr_ms,
            O.H_TR_EM: Htr_em,
            O.H_TR_W: Htr_w,
            O.C_M: C_m,
            # Ventilation (scalar constant)
            O.VENTILATION: ventilation,
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
            # Keep solar off to avoid dependency on windows mapping for synthetic IDs
            O.ACTIVE_GAINS_SOLAR: False,
            # Splits
            O.SIGMA_SURFACE: sigma_surface,
            O.FRAC_CONV_INTERNAL: 0.5,
            O.FRAC_RAD_SURFACE: 0.7,
            O.FRAC_RAD_MASS: 0.3,
        }
        objs.append(obj)

    return pd.DataFrame(objs)


def run_benchmark(num_objects: int = 100, workers: int = 1) -> tuple[float, pd.DataFrame, dict]:
    """Run the 5R1C benchmark with a given number of objects and workers."""
    objects = generate_hvac_objects(num_objects)

    # Load data
    cwd = "."  # benchmark script directory
    data: dict[str, pd.DataFrame] = {}

    # Common weather (shared across examples)
    common_data_folder = "../common_data"
    for file in os.listdir(os.path.join(cwd, common_data_folder)):
        if file.endswith(".csv"):
            name = file.split(".")[0]
            data[name] = pd.read_csv(os.path.join(cwd, common_data_folder, file), parse_dates=True)

    # Optional: local example data (windows, etc.)
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
    print("Running 5R1C benchmark with 1 worker…")
    t1, _, _ = run_benchmark(num_objects=100, workers=1)
    print(f"Runtime (1 worker): {t1:.2f} s")

    print("\nRunning 5R1C benchmark with 4 workers…")
    t4, _, _ = run_benchmark(num_objects=100, workers=4)
    print(f"Runtime (4 workers): {t4:.2f} s")

    # Print speedup
    speedup = t1 / t4
    print(f"\nSpeedup with 4 workers: {speedup:.2f}x")
