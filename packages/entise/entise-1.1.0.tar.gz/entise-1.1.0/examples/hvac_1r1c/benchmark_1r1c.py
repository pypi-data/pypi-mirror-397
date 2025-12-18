"""
Benchmark script for HVAC: 1r1c

This script tests the performance of the 1R1C method with 100 HVAC objects.
It generates 100 HVAC objects with varying parameters, uses the R1C1 method
to generate time series for all objects, and measures the execution time.
"""

import os
import sys
import time

import numpy as np
import pandas as pd

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the TimeSeriesGenerator
from entise.constants import Objects as O
from entise.core.generator import TimeSeriesGenerator


def generate_hvac_objects(num_objects=100, seed=42):
    """
    Generate HVAC objects with varying parameters.
    """
    # Set random seed for reproducibility
    np.random.seed(seed)
    
    # Create a list to store the objects
    objects_list = []
    
    # Generate objects with varying parameters
    for i in range(num_objects):
        # Generate random variations for parameters
        # Thermal resistance (K/W) - typical range from 0.0002 to 0.004
        resistance = np.random.uniform(0.0002, 0.004)
        
        # Thermal capacitance (J/K) - typical range from 10M to 350M
        capacitance = np.random.uniform(10e6, 350e6)
        
        # Ventilation rate (W/K) - typically scales with building size
        ventilation = capacitance * np.random.uniform(1e-6, 5e-6)
        
        # Temperature setpoints (°C)
        temp_init = np.random.uniform(18, 22)
        temp_min = np.random.uniform(18, 22)
        temp_max = np.random.uniform(22, 26)
        
        # Latitude and longitude (small variations around a base location)
        latitude = 49.72 + np.random.uniform(-0.01, 0.01)
        longitude = 11.05 + np.random.uniform(-0.01, 0.01)
        
        # Heated area (m²) - typical range from 100 to 5000
        heated_area = np.random.uniform(100, 5000)
        
        # Internal gains - either a constant value or a reference to a data source
        # For simplicity, we'll use a 50/50 split between constant values and data references
        if np.random.random() < 0.5:
            gains_internal = np.random.uniform(100, 1000)  # Constant value in W
            gains_internal_column = ""
        else:
            gains_internal = "internal_gains"  # Reference to data source
            # Choose a random column from available options
            column_options = ["residential", "office", "commercial", "industrial"]
            gains_internal_column = np.random.choice(column_options)
        
        # Create the object
        obj = {
            'id': f'hvac_{i+1}',
            'hvac': '1R1C',
            O.WEATHER: 'weather',
            O.RESISTANCE: resistance,
            O.CAPACITANCE: capacitance,
            O.VENTILATION: ventilation,
            O.TEMP_INIT: temp_init,
            O.TEMP_MIN: temp_min,
            O.TEMP_MAX: temp_max,
            O.WINDOWS: 'windows',
            O.LAT: latitude,
            O.LON: longitude,
            O.AREA: heated_area,
            O.GAINS_INTERNAL: gains_internal,
            O.GAINS_INTERNAL_COL: gains_internal_column
        }
        
        # Add the object to the list
        objects_list.append(obj)
    
    # Convert the list to a DataFrame
    objects_df = pd.DataFrame(objects_list)
    
    return objects_df

def run_benchmark(num_objects=100, workers=1):
    """
    Run the benchmark with the specified number of objects and workers.
    """
    # Generate HVAC objects
    objects = generate_hvac_objects(num_objects)
    
    # Load data
    cwd = '.'  # Current working directory
    data = {}
    common_data_folder = "../common_data"
    for file in os.listdir(os.path.join(cwd, common_data_folder)):
        if file.endswith(".csv"):
            name = file.split(".")[0]
            data[name] = pd.read_csv(os.path.join(os.path.join(cwd, common_data_folder, file)), parse_dates=True)
    data_folder = "data"
    for file in os.listdir(os.path.join(cwd, data_folder)):
        if file.endswith(".csv"):
            name = file.split(".")[0]
            data[name] = pd.read_csv(os.path.join(os.path.join(cwd, data_folder, file)), parse_dates=True)
    
    # Instantiate and configure the generator
    gen = TimeSeriesGenerator()
    gen.add_objects(objects)
    
    # Generate time series and measure execution time
    start_time = time.time()
    summary, df = gen.generate(data, workers=workers)
    end_time = time.time()
    execution_time = end_time - start_time
    
    return execution_time, summary, df

if __name__ == "__main__":
    # Run the benchmark with different numbers of workers
    print("Running benchmark with 1 worker...")
    t1, _, _ = run_benchmark(num_objects=100, workers=1)
    print(f"Runtime: {t1:.2f} seconds")
    
    print("\nRunning benchmark with 4 workers...")
    t4, _, _ = run_benchmark(num_objects=100, workers=4)
    print(f"Runtime: {t4:.2f} seconds")

    # Print speedup
    speedup = t1 / t4
    print(f"\nSpeedup with 4 workers: {speedup:.2f}x")
