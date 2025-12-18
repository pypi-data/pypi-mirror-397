"""
Benchmark script for Wind: wplib

This script tests the performance of the wplib method with 100 wind turbine objects.
It generates 100 wind turbine objects with varying parameters, uses the WPLib method
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


def generate_wind_objects(num_objects=100):
    """
    Generate wind turbine objects with varying parameters.
    
    Args:
        num_objects (int): Number of wind turbine objects to generate
        
    Returns:
        pd.DataFrame: DataFrame containing wind turbine objects
    """
    # Create a list to store the objects
    objects_list = []
    
    # Define a list of common turbine types from windpowerlib
    turbine_types = [
        "SWT130/3600",  # Siemens
        "V164/8000",    # Vestas
        "E-101/3500",   # Enercon
        "GE130/3200",   # GE Wind
        "N117/2400",    # Nordex
        "S122/3200",    # Senvion/REpower
        "AD116/5000",   # Adwen/Areva
        "SWT142/3150"   # Siemens
    ]
    
    # Generate objects with varying parameters
    for i in range(num_objects):
        # Generate random variations for parameters
        power = np.random.randint(1000000, 8000000)  # Power between 1MW and 8MW
        turbine_type = np.random.choice(turbine_types)
        hub_height = np.random.randint(140, 180)  # Hub height between 80m and 180m
        
        # Create the object
        obj = {
            O.ID: f'wind_{i+1}',
            Types.WIND: 'wplib',
            O.WEATHER: 'weather',
            O.POWER: power,
            O.TURBINE_TYPE: turbine_type,
            O.HUB_HEIGHT: hub_height
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
        num_objects (int): Number of wind turbine objects to generate
        workers (int): Number of workers to use for parallel processing
        visualize (bool): Whether to visualize the results
        
    Returns:
        tuple: A tuple containing:
            - execution_time (float): Execution time in seconds
            - summary (pd.DataFrame): Summary statistics
            - timeseries (dict): Time series data
    """
    # Generate wind turbine objects
    objects = generate_wind_objects(num_objects)
    
    # Load data
    cwd = '.'  # Current working directory
    data = {}
    data_folder = '../common_data'
    for file in os.listdir(os.path.join(cwd, data_folder)):
        if file.endswith('.csv'):
            name = file.split('.')[0]
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
    time_1, _, _ = run_benchmark(num_objects=100, workers=1, visualize=False)
    print(f"Runtime: {time_1:.2f} seconds")
    
    print("\nRunning benchmark with 4 workers...")
    time_4, _, _ = run_benchmark(num_objects=100, workers=4, visualize=False)
    print(f"Runtime: {time_4:.2f} seconds")
    
    # Print speedup
    speedup = time_1 / time_4
    print(f"\nSpeedup with 4 workers: {speedup:.2f}x")
    
    # # Run with visualization for the last run
    # print("\nRunning benchmark with visualization...")
    # _, _, _ = run_benchmark(num_objects=100, workers=4, visualize=True)