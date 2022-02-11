import os
import pandas as pd, numpy as np
from scipy.optimize import least_squares
from matplotlib import pyplot as plt
import pycruise_tools as pct

# Import lat/lon/station info
stations = pd.read_table("data/stations.txt", encoding="unicode_escape")
stations.rename(columns={"Station no.": "station", "Cast": "cast"}, inplace=True)

# Parse lat/lon text into decimal degrees
stations["lat"] = stations.Latitude.apply(pct.parse_latitude_text)
stations["lon"] = stations.Longitude.apply(pct.parse_longitude_text)

# row = stations.iloc[1]
#
stations["station_cast"] = ""
for i, row in stations.iterrows():
    sc = "{}-{}".format(row.station, row.cast)
    stations.loc[i, "station_cast"] = sc


# # apply() approach
# def get_station_cast(row):
#     return "{}-{}".format(row.station, row.cast)

# stations["station_cast_v2"] = stations.apply(get_station_cast, axis=1)

# # apply() approach with a lambda
# stations["station_cast_v3"] = stations.apply(
#     lambda row: "{}-{}".format(row.station, row.cast),
#     axis=1
#     )

stations.set_index("station_cast", inplace=True)

#%% Import CTD data from all stations
filepath = "data/ctd-bottles/"
extra_ctd_files = os.listdir(filepath)
extra_ctd_files = [f for f in extra_ctd_files if f.endswith(".csv")]
missing_ctd_files = []
ctd = []
for i, row in stations.iterrows():
    print(i)

    # Determine filename from row of stations table (station & cast)
    # filename = "data/ctd-bottles/ctd-bottles-1-1.csv"
    # filename = "data/ctd-bottles/ctd-bottles-" + "1" + "-" + "1" + ".csv"
    # filename = "data/ctd-bottles/ctd-bottles-" + str(row.station) + "-" + str(row.cast) + ".csv"
    filename = "ctd-bottles-{}-{}.csv".format(row.station, row.cast)

    try:

        # Import CTD data for this station and append to list
        _ctd = pd.read_csv(filepath + filename, na_values=-999)
        _ctd["station_cast"] = i
        ctd.append(_ctd)

        # Take file out of extra_ctd_files list
        extra_ctd_files.remove(filename)

    except FileNotFoundError:

        missing_ctd_files.append(filename)

#%% Concatenate all stations into single df
ctd = pd.concat(ctd)

#%% Put data from stations into ctd
for var in ["lat", "lon", "station", "cast"]:
    ctd[var] = stations.loc[ctd.station_cast, var].values

# Get datetime
ctd["datetime"] = pd.to_datetime(ctd[["year", "month", "day", "hour", "minute"]])
# Next: use groupby() to condense ^ into stations table

#%% Put averages from ctd back into stations
stations["datetime"] = ctd[["station_cast", "datetime"]].groupby("station_cast").mean()

#%% Import nutrients dataset (Excel file)
nutrients = pd.read_excel("data/nutrients.xlsx", na_values=["n.a."]).rename(
    columns={"Sample ID": "sample_id", "NO3+NO2": "NO3_NO2"}
)

# nutrients.where(
#     nutrients != '<0.01', other=0, inplace=True)
for n in ["NO3_NO2", "NO2", "PO4"]:
    nutrients[n].where(nutrients[n] != "<0.01", other=0, inplace=True)
    nutrients[n] = nutrients[n].astype(float)


def parse_nutrients_sample_id(sid):
    """Convert station_id column in nutrients df into separate
    station, cast, and bottle values.
    """
    sid_split = sid.split("-")
    if len(sid_split) == 3:
        # station = sid_split[0]
        # cast = sid_split[1]
        # bottle = sid_split[2]
        station, cast, bottle = sid_split
    elif len(sid_split) == 1:
        station = np.nan
        cast = np.nan
        bottle = sid_split[0]
    else:
        station = np.nan
        cast = np.nan
        bottle = np.nan
    return pd.Series(
        {
            "station": station,
            "cast": cast,
            "bottle": bottle,
        }
    )


sids = nutrients.sample_id.apply(parse_nutrients_sample_id)
# nutrients = pd.concat([nutrients, sids], axis=1)

for c, cdata in sids.iteritems():
    nutrients[c] = cdata

# Fill NaNs in station and cast
nutrients.station.fillna(method="ffill", inplace=True)
nutrients.cast.fillna(method="ffill", inplace=True)

#%%
# Import calibration dataset
cali = pd.read_csv("data/sensor-calibration.csv")

# Convert station, cast and bottle to integers not strings
for col in ["station", "cast", "bottle"]:
    nutrients[col] = nutrients[col].astype(int)
    cali[col] = cali[col].astype(int)
ctd["bottle"] = ctd["bottle"].astype(int)


def get_station_cast_bottle(row):
    """Get station-cast-bottle string from the relevant columns."""
    return "{:.0f}-{:.0f}-{:.0f}".format(row.station, row.cast, row.bottle)


# Set station-cast-bottle as the index for ctd and nutrients dfs
for df in [ctd, nutrients, cali]:
    df["scb"] = df.apply(get_station_cast_bottle, axis=1)
    df.set_index("scb", inplace=True)  # must use inplace not df = df.... !

# Move nutrients data across to ctd
for col in ["NO3_NO2", "NO2", "Si", "PO4"]:
    ctd[col] = nutrients[col]

# Get NO3
ctd["NO3"] = ctd.NO3_NO2 - ctd.NO2

ctd["salinity_raw"] = ctd.salinity.copy()

#%% Calibrate salinity and oxygen
def convert_salinity(sal_coeffs, sensor_salinity):
    """Convert sensor salinity values into calibrated real values."""
    squared, slope, intercept = sal_coeffs
    real_salinity = squared * sensor_salinity ** 2 + slope * sensor_salinity + intercept
    return real_salinity


def _lsqfun_convert_salinity(sal_coeffs, sensor_salinity, true_salinity):
    return convert_salinity(sal_coeffs, sensor_salinity) - true_salinity


L = ~np.isnan(cali.salinity)

opt_result_salinity = least_squares(
    _lsqfun_convert_salinity,
    [0, 1, 0],
    args=(cali[L].salinity.to_numpy(), cali[L].salinity_lab.to_numpy()),
)

ctd["salinity"] = convert_salinity(opt_result_salinity["x"], ctd.salinity_raw)


fx = np.linspace(ctd.salinity_raw.min(), ctd.salinity_raw.max(), num=500)
fy = convert_salinity(opt_result_salinity["x"], fx)

fig, ax = plt.subplots(dpi=300)
cali.plot.scatter("salinity", "salinity_lab", ax=ax)
ax.plot(fx, fy)
ax.set_xlabel("Sensor raw salinity")
ax.set_ylabel("Calibrated lab measurements")
ax.set_title(
    "Salinity = {:.3f} raw$^2$ + {:.2f} raw + {:.1f}".format(*opt_result_salinity["x"])
)
plt.tight_layout()
plt.savefig("figures/salinity_calibration.png")

#%% Save the CTD data
ctd.to_csv("results/ctd.csv")
