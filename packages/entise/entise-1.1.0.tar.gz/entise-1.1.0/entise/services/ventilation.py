import numpy as np
import pandas as pd

# TYPICAL VENTILATION

# SEASONAL AVERAGE AIR CHANGE RATES (h^-1)
n_winter = 0.3  # Dec, Jan, Feb
n_spring_autumn = 0.4  # Mar, Apr, May, Sep, Oct, Nov
n_summer = 0.6  # Jun, Jul, Aug

# HOURLY VENTILATION PROFILE FOR TYPICAL DAY (fraction of daily mean)
hourly_pattern = np.array([
    0.6, 0.6, 0.6, 0.6, 0.6, 0.6,  # 0–6 am (night)
    2.0, 1.5,                      # 6–8 am (morning airing)
    0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7,  # 8 am–4 pm (day, low)
    1.2, 2.0,                      # 4–6 pm (evening airing)
    1.2, 1.0, 0.8, 0.6, 0.6, 0.6   # 6–12 pm (winding down)
])
hourly_pattern /= hourly_pattern.mean()  # Normalize so average = 1

# Generate 8760 hourly n values with seasonal scaling
n_values = np.zeros(8760)
for day in range(365):
    month = pd.Timestamp('2024-01-01') + pd.Timedelta(days=day)
    if month.month in [12, 1, 2]:
        daily_avg = n_winter
    elif month.month in [6, 7, 8]:
        daily_avg = n_summer
    else:
        daily_avg = n_spring_autumn
    n_values[day*24:(day+1)*24] = daily_avg * hourly_pattern

# For leap year, add extra day
if len(n_values) < 8760:
    n_values = np.concatenate([n_values, n_spring_autumn * hourly_pattern])

# OPTIONAL: Create DataFrame for inspection
vent_df = pd.DataFrame({
    'hour': np.arange(1, 8761),
    'n [1/h]': n_values.round(2),
})

# Save to CSV (uncomment if needed)
vent_df.to_csv('ventilation_loss_profile_typical.csv', index=False)


# ENERGY EFFICIENT

n_values = np.zeros(8760)
for day in range(365):
    month = pd.Timestamp('2024-01-01') + pd.Timedelta(days=day)
    hour_base = day * 24
    # WINTER: Dec, Jan, Feb
    if month.month in [12, 1, 2]:
        n_day = np.full(24, 0.25)  # Minimum
        n_day[12] = 0.7            # Midday airing (e.g., 12:00–13:00)
    # SUMMER: Jun, Jul, Aug
    elif month.month in [6, 7, 8]:
        n_day = np.full(24, 0.3)   # Daytime minimum
        n_day[22:] = 1.2           # Night flush (22:00–24:00)
        n_day[:7] = 1.2            # Night flush (00:00–07:00)
    # SPRING/AUTUMN: Mar–May, Sep–Nov
    else:
        n_day = np.full(24, 0.35)  # Intermediate
        n_day[12] = 0.8            # Midday airing
    n_values[hour_base:hour_base+24] = n_day

# For leap year, add extra day (optional)
if len(n_values) < 8760:
    n_values = np.concatenate([n_values, np.full(24, 0.35)])

# OPTIONAL: Create DataFrame for inspection
vent_df = pd.DataFrame({
    'hour': np.arange(1, 8761),
    'n [1/h]': n_values.round(2),
})

# Uncomment to save
vent_df.to_csv('ventilation_loss_profile_efficient.csv', index=False)


# # OPTIMAL (BASED ON WEATHER FILE)
#
# # Prepare datetime
# weather['datetime'] = pd.to_datetime(weather['datetime'])
# weather['month'] = weather['datetime'].dt.month
# weather['hour'] = weather['datetime'].dt.hour
#
# # Create optimal n(t) series
# def optimal_n(row, indoor_setpoint=23):
#     if row['month'] in [6, 7, 8]:  # Summer months
#         # Night flushing: 22:00–07:00, if outdoor is cooler than setpoint
#         if ((row['hour'] >= 22 or row['hour'] <= 7) and row['temp_out'] < indoor_setpoint):
#             return 1.2
#         else:
#             return 0.25
#     else:  # Rest of year: always minimum
#         return 0.25
#
# weather['n_optimal'] = weather.apply(optimal_n, axis=1)

