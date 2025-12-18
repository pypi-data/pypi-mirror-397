"""
Benchmark script for Heat Pump: Ruhnau

This script tests the performance of the Ruhnau heat pump method with multiple heat pump objects.
It generates heat pump objects with varying parameters, uses the Ruhnau method
to generate time series for all objects, and measures the execution time.
"""

import os
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the TimeSeriesGenerator
from entise.constants import Columns as C
from entise.constants import Objects as O
from entise.constants import Types
from entise.core.generator import TimeSeriesGenerator


def create_weather_dataset(size=8760):  # 1 year of hourly data
    """
    Create a synthetic weather dataset for testing.
    
    Args:
        size (int): Number of data points to generate
        
    Returns:
        pd.DataFrame: DataFrame containing weather data
    """
    print(f"Creating synthetic weather dataset with {size} rows...")

    # Create a datetime index
    start_date = pd.Timestamp('2020-01-01')
    dates = pd.date_range(start=start_date, periods=size, freq='H')

    # Create temperature data with seasonal variation
    t = np.arange(size)

    # Air temperature: seasonal + daily variation + random noise
    air_temp = 15 + 10 * np.sin(2 * np.pi * t / 8760) + 5 * np.sin(2 * np.pi * t / 24) + np.random.normal(0, 2, size)

    # Soil temperature: more stable, follows air temperature with delay and dampened amplitude
    soil_temp = 10 + 5 * np.sin(2 * np.pi * (t - 1000) / 8760) + np.random.normal(0, 0.5, size)

    # Groundwater temperature: very stable
    water_temp = np.ones(size) * 10 + np.random.normal(0, 0.2, size)

    # Create DataFrame with all required temperature columns
    df = pd.DataFrame({
        'datetime': dates,
        C.TEMP_AIR: air_temp,
        C.TEMP_SOIL: soil_temp,
        C.TEMP_WATER: water_temp
    })

    return df

def generate_hp_objects(num_objects=100):
    """
    Generate heat pump objects with varying parameters.
    
    Args:
        num_objects (int): Number of heat pump objects to generate
        
    Returns:
        pd.DataFrame: DataFrame containing heat pump objects
    """
    # Create a list to store the objects
    objects_list = []
    
    # Define heat pump source types
    hp_sources = ["air", "soil", "water"]
    
    # Define heat sink types
    hp_sinks = ["floor", "radiator"]
    
    # Generate objects with varying parameters
    for i in range(num_objects):
        # Generate random variations for parameters
        hp_source = np.random.choice(hp_sources)
        hp_sink = np.random.choice(hp_sinks)
        
        # Set temperature parameters based on sink type
        if hp_sink == "floor":
            temp_sink = np.random.randint(25, 35)  # Floor heating: 25-35°C
            gradient_sink = np.random.uniform(-0.7, -0.3)  # Typical gradient for floor heating
        else:  # radiator
            temp_sink = np.random.randint(35, 50)  # Radiator: 35-50°C
            gradient_sink = np.random.uniform(-1.2, -0.8)  # Typical gradient for radiators
        
        # DHW temperature
        temp_water = np.random.randint(45, 60)  # DHW: 45-60°C
        
        # Create the object
        obj = {
            O.ID: f'hp_{i+1}',
            Types.HP: 'ruhnau',
            O.WEATHER: 'weather_data',
            O.HP_SOURCE: hp_source,
            O.HP_SINK: hp_sink,
            O.TEMP_SINK: temp_sink,
            O.GRADIENT_SINK: gradient_sink,
            O.TEMP_WATER: temp_water
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
        num_objects (int): Number of heat pump objects to generate
        workers (int): Number of workers to use for parallel processing
        visualize (bool): Whether to visualize the results
        
    Returns:
        tuple: A tuple containing:
            - execution_time (float): Execution time in seconds
            - summary (pd.DataFrame): Summary statistics
            - timeseries (dict): Time series data
    """
    # Generate heat pump objects
    print(f"Generating {num_objects} heat pump objects...")
    objects = generate_hp_objects(num_objects)
    
    # Create weather data
    weather_data = create_weather_dataset()
    
    # Prepare data dictionary
    data = {
        "weather_data": weather_data
    }
    
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
    
    # Print summary
    print("Summary statistics:")
    print(summary.head())  # Print only the first few rows
    
    # Visualize results if requested
    if visualize:
        # Convert index to datetime for all time series
        for obj_id in df:
            if Types.HP in df[obj_id]:
                df[obj_id][Types.HP].index = pd.to_datetime(df[obj_id][Types.HP].index)
        
        # Get heat pump parameters from objects dataframe
        system_configs = {}
        for _, row in objects.iterrows():
            obj_id = row['id']
            if obj_id in df:
                hp_source = row['hp_source'] if not pd.isna(row.get('hp_source', pd.NA)) else "Default"
                hp_sink = row['hp_sink'] if not pd.isna(row.get('hp_sink', pd.NA)) else "Default"
                temp_sink = row['temp_sink'] if not pd.isna(row.get('temp_sink', pd.NA)) else "Default"
                system_configs[obj_id] = {
                    'hp_source': hp_source,
                    'hp_sink': hp_sink,
                    'temp_sink': temp_sink
                }
        
        # Figure 1: Histogram of average COP values
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        heating_cop_avg = [summary.loc[obj_id][f"{Types.HP}_{Types.HEATING}_avg"] for obj_id in df.keys()]
        plt.hist(heating_cop_avg, bins=20)
        plt.title('Histogram of Average Heating COP')
        plt.xlabel('Average COP')
        plt.ylabel('Count')
        plt.grid(axis='y')
        
        plt.subplot(1, 2, 2)
        dhw_cop_avg = [summary.loc[obj_id][f"{Types.HP}_{Types.DHW}_avg"] for obj_id in df.keys()]
        plt.hist(dhw_cop_avg, bins=20)
        plt.title('Histogram of Average DHW COP')
        plt.xlabel('Average COP')
        plt.ylabel('Count')
        plt.grid(axis='y')
        
        plt.tight_layout()
        plt.show()
        
        # Figure 2: Sample of daily profiles for a few systems
        plt.figure(figsize=(12, 8))
        sample_ids = list(df.keys())[:5]  # Take first 5 systems
        
        for i, obj_id in enumerate(sample_ids):
            if Types.HP in df[obj_id]:
                # Get a sample day (e.g., a winter day)
                sample_day = df[obj_id][Types.HP].iloc[:24].copy()
                
                # Get system parameters for the title
                hp_source = system_configs[obj_id]['hp_source'] if obj_id in system_configs else "Default"
                hp_sink = system_configs[obj_id]['hp_sink'] if obj_id in system_configs else "Default"
                
                # Plot the daily profile
                plt.subplot(len(sample_ids), 1, i+1)
                heating_col = f"{Types.HP}_{Types.HEATING}"
                dhw_col = f"{Types.HP}_{Types.DHW}"
                
                if heating_col in sample_day.columns:
                    plt.plot(range(24), sample_day[heating_col].values, label="Heating COP")
                if dhw_col in sample_day.columns:
                    plt.plot(range(24), sample_day[dhw_col].values, label="DHW COP", linestyle='--')
                
                plt.title(f'ID {obj_id}, Source: {hp_source}, Sink: {hp_sink}')
                plt.xlabel('Hour of Day')
                plt.ylabel('COP')
                plt.grid(True)
                plt.xticks(range(0, 24, 2))
                plt.legend()
        
        plt.tight_layout()
        plt.show()
    
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
    # _, _, _ = run_benchmark(num_objects=20, workers=4, visualize=True)