import re
import pandas as pd, numpy as np

# Import lat/lon/station info
stations = pd.read_table("data/stations.txt", encoding="unicode_escape")

# Parse lat/lon text into decimal degrees
stations["lat"] = np.nan
stations["lon"] = np.nan
for i, station in stations.iterrows():

    # Define all latitude formats
    lat_dmf = re.match("(\d+)°(\d+\.\d+)'([NS])", station.Latitude)
    lat_dmsf = re.match("(\d+)°(\d+)'(\d+)\"([NS])", station.Latitude)

    # Parse decimal minutes format --- latitude
    if lat_dmf:
        lat = float(lat_dmf.group(1)) + float(lat_dmf.group(2)) / 60
        if lat_dmf.group(3) == "S":
            lat *= -1

    # Parse degrees minutes seconds format --- latitude
    elif lat_dmsf:
        lat = (
            float(lat_dmsf.group(1))
            + float(lat_dmsf.group(2)) / 60
            + float(lat_dmsf.group(3)) / 3600
        )
        if lat_dmsf.group(4) == "S":
            lat *= -1

    # Parse decimal degrees format --- latitude
    else:
        lat = float(stations.loc[i, "Latitude"])

    # Put final latitude value into the table
    stations.loc[i, "lat"] = lat

    # Deal with longitude
    try:
        stations.loc[i, "lon"] = float(stations.loc[i, "Longitude"])
    except:
        pass
