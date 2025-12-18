"""
Benchmark script for PV: pvlib

This script tests the performance of the pvlib method with 100 PV objects.
It generates 100 PV objects with varying parameters, uses the PVLib method
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
from entise.constants import Types
from entise.core.generator import TimeSeriesGenerator


def generate_pv_objects(num_objects=100, base_latitude=49.72, base_longitude=11.05):
    """
    Generate PV objects with varying parameters.
    
    Args:
        num_objects (int): Number of PV objects to generate
        base_latitude (float): Base latitude for the objects
        base_longitude (float): Base longitude for the objects
        
    Returns:
        pd.DataFrame: DataFrame containing PV objects
    """
    # Create a list to store the objects
    objects_list = []
    
    # Generate objects with varying parameters
    for i in range(num_objects):
        # Generate random variations for parameters
        latitude = base_latitude + np.random.uniform(-0.01, 0.01)
        longitude = base_longitude + np.random.uniform(-0.01, 0.01)
        power = np.random.randint(1000, 20000)  # Power between 1kW and 20kW
        azimuth = np.random.randint(0, 360)  # Azimuth between 0 and 360 degrees
        tilt = np.random.randint(0, 90)  # Tilt between 0 and 90 degrees
        
        # Create the object
        obj = {
            O.ID: f'pv_{i+1}',
            Types.PV: 'pvlib',
            O.LAT: latitude,
            O.LON: longitude,
            O.WEATHER: 'weather',
            O.POWER: power,
            O.AZIMUTH: azimuth,
            O.TILT: tilt,
            O.ALTITUDE: None,
            O.PV_ARRAYS: None
        }
        
        # Add the object to the list
        objects_list.append(obj)
    
    # Convert the list to a DataFrame
    objects_df = pd.DataFrame(objects_list)
    
    return objects_df

def run_benchmark(num_objects=100, workers=1, visualize=False):
    """
    Run the benchmark with the specified number of objects and workers.
    
    Args:
        num_objects (int): Number of PV objects to generate
        workers (int): Number of workers to use for parallel processing
        visualize (bool): Whether to visualize the results
        
    Returns:
        tuple: A tuple containing:
            - execution_time (float): Execution time in seconds
            - summary (pd.DataFrame): Summary statistics
            - timeseries (dict): Time series data
    """
    # Generate PV objects
    print(f"Generating {num_objects} PV objects...")
    objects = generate_pv_objects(num_objects)
    
    # Load data
    print("Loading data...")
    cwd = '.'  # Current working directory
    data = {}
    data_folder = '../common_data'
    for file in os.listdir(os.path.join(cwd, data_folder)):
        if file.endswith('.csv'):
            name = file.split('.')[0]
            data[name] = pd.read_csv(os.path.join(os.path.join(cwd, data_folder, file)), parse_dates=True)
    print('Loaded data keys:', list(data.keys()))
    
    # Instantiate and configure the generator
    print("Configuring generator...")
    gen = TimeSeriesGenerator()
    gen.add_objects(objects)
    
    # Generate time series and measure execution time
    print(f"Generating time series with {workers} worker(s)...")
    start_time = time.time()
    summary, df = gen.generate(data, workers=workers)
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Print execution time
    print(f"Execution time: {execution_time:.2f} seconds")
    
    return execution_time, summary, df

if __name__ == "__main__":
    # Run the benchmark with different numbers of workers
    print("Running benchmark with 1 worker...")
    time_1, _, _ = run_benchmark(num_objects=100, workers=1)
    print(f"Runtime: {time_1:.2f} seconds")
    
    print("\nRunning benchmark with 4 workers...")
    time_4, _, _ = run_benchmark(num_objects=100, workers=4)
    print(f"Runtime: {time_4:.2f} seconds")
    
    # Print speedup
    speedup = time_1 / time_4
    print(f"\nSpeedup with 4 workers: {speedup:.2f}x")
    
    # # Run with visualization for the last run
    # print("\nRunning benchmark with visualization...")
    # _, _, _ = run_benchmark(num_objects=100, workers=4, visualize=True)