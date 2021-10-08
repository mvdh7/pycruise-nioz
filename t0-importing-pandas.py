import re
import pandas as pd, numpy as np

#%% Import lat/lon/station info
stations = pd.read_table("data/stations.txt", encoding="unicode_escape")

# Parse station information
# station = stations.iloc[127]

# Decimal minutes format --- latitude
lat_dmf = re.match("(\d+)°(\d+\.\d+)'([NS])", "50°30.00'S")
lat = float(lat_dmf.group(1)) + float(lat_dmf.group(2)) / 60
if lat_dmf.group(3) == "S":
    lat *= -1

#%%
stations["lat"] = np.nan
stations["lon"] = np.nan
for i, station in stations.iterrows():
    try:
        stations.loc[i, "lat"] = float(stations.loc[i, "Latitude"])
        stations.loc[i, "lon"] = float(stations.loc[i, "Longitude"])
    except:
        pass
