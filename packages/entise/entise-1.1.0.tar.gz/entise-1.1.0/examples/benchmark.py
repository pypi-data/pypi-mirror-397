import time

import pandas as pd

from examples.hvac_1r1c.runme import get_input as input_1r1c
from examples.hvac_1r1c.runme import simulate as simulate_1r1c


def run_benchmarks(methods, num_workers_list, num_objects) -> None:
    """Runs benchmarks for different methods and worker counts"""
    results = []

    for method in methods:
        for num_workers in num_workers_list:
            df = benchmark_method(method, num_workers, num_objects)
            results.append({
                'method': method,
                'num_workers': num_workers,
                'dataframe': df
            })

    return pd.DataFrame(results)

def benchmark_method(method: str, num_workers: int, num_objects: int) -> None:
    """Runs the benchmark for a given method, number of workers, and number of objects"""

    # Create HVAC objects by multiplying the base input
    objects, data = input_1r1c(path=f"./{method}")
    objects = pd.concat([objects]* (num_objects // len(objects)), ignore_index=True).iloc[:num_objects]

    # Run the simulation and measure execution time
    start = time.perf_counter()
    summary, df = simulate_1r1c(objects, data, workers=num_workers, path=f"./{method}")
    end = time.perf_counter()
    return end - start

def create_report(df):
    """Creates a csv from the benchmark results dataframe"""
    df.to_csv("benchmark_results.csv")
    pass

def create_barplot(df):
    """Creates a barplot from the benchmark results dataframe"""
    df.plot()
    pass

def main(methods, num_wokers, num_objects, plot: bool = False) -> None:
    df = run_benchmarks(methods, num_wokers, num_objects)
    create_report(df)
    create_barplot(df)


if __name__ == '__main__':
    methods = ['pv_pvlib', 'wind_wplib']
    num_workers = [1, 4]
    num_objects = 10
    main(methods, num_workers, num_objects, plot=True)
