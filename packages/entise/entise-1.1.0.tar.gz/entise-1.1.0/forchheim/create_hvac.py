"""
Example script demonstrating the pipeline architecture.

This script demonstrates how to use the pipeline architecture to generate
time series for multiple buildings.
"""

import concurrent.futures
import os
from functools import partial

import pandas as pd
from tqdm import tqdm

from entise.core.generator import TimeSeriesGenerator


def save_hvac_csv(item, year_path):
    bid, results = item
    file_path = os.path.join(year_path, 'hvac', f"hvac_{int(bid)}.csv")
    results['hvac'].to_csv(file_path, index=True)


# Load data

years = next(os.walk('./input'))[1]  # Get all subdirectories (years)
data = {}
data['weather'] = pd.read_csv('./input/weather.csv', parse_dates=True)
data['ventilation'] = pd.read_csv('./input/ventilation.csv', parse_dates=True)
totals = pd.DataFrame(columns=['year', 'total_heating', 'total_cooling'])
for year in years:
    print(f"Processing year: {year}")
    if year != '2045':
        continue
    cwd = os.path.join('./input', year)  # Current working directory: change if necessary
    objects = pd.read_csv(os.path.join(cwd, "objects.csv"))
    data_folder = "data"
    for file in os.listdir(os.path.join(cwd, data_folder)):
        if file.endswith(".csv"):
            name = file.split(".")[0]
            data[name] = pd.read_csv(os.path.join(os.path.join(cwd, data_folder, file)), parse_dates=True)

    # Instantiate and configure the generator
    gen = TimeSeriesGenerator()

    # Filter objects to only include one object (for debugging)
    objects_filtered = objects
    gen.add_objects(objects_filtered)

    # Generate time series
    summary, df = gen.generate(data, workers=7)

    # Add year to totals DataFrame
    total_heating = summary['demand_heating'].sum() / 1e9 # Convert to GWh
    total_cooling = summary['demand_cooling'].sum() / 1e9  # Convert to GWh
    totals = totals._append({'year': year,
                            'total_heating': total_heating,
                            'total_cooling': total_cooling}, ignore_index=True)

    objects_expanded = pd.concat([objects.set_index('id'), summary], axis=1)
    # objects_expanded.index = objects_expanded.index.astype(int)  # Ensure index is integer type
    objects_expanded.to_csv(os.path.join(os.path.join('./output', year), "objects_expanded.csv"), index=True)

    hvac_output_path = os.path.join('./output', year, 'hvac')

    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        save_func = partial(save_hvac_csv, year_path=os.path.join('./output', year))
        list(tqdm(executor.map(save_func, df.items()),
                  desc=f"Saving year {year}",
                  total=len(df)))

# Print summary
print("Summary [GWh]:")
print(totals)
# totals.to_csv('./output/total_energy.csv', index=False)



