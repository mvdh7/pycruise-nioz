import pandas as pd, numpy as np

ctd1 = pd.read_csv("data/ctd-bottles-variants/00-ctd-bottles-2-1.csv", na_values=-999)

ctd1.plot.scatter("salinity", 'depth')

# Import lat/lon/station info
stations = pd.read_table("data/stations.txt", encoding="unicode_escape")

# Parse station information
row = stations.iloc[1]

stations["lat"] = np.nan
stations["lon"] = np.nan
for i, station in stations.iterrows():
    try:
        stations.loc[i, "lat"] = float(stations.loc[i, "Latitude"])
        stations.loc[i, "lon"] = float(stations.loc[i, "Longitude"])
    except:
        pass

print("ok")

stations.lat
stations["lat"]
