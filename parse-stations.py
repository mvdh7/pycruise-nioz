import re
import pandas as pd, numpy as np

#%% Import lat/lon/station info
stations = pd.read_table("data/stations.txt", encoding="unicode_escape")

# Parse station information
station = stations.loc[9]


# Decimal minutes format --- longitude
lon_dmf = re.match("(\d+)°(\d+\.\d+)'([EW])", station.Longitude)
lon = float(lon_dmf.group(1)) + float(lon_dmf.group(2)) / 60
if lon_dmf.group(3) == "W":
    lon *= -1


station = stations.loc[0]

    
# 54°00'04"S

#%%
stations["lat"] = np.nan
stations["lon"] = np.nan

# # Make a deliberate error
# stations.loc[29, "Latitude"] = "OH NO!!!"

# Deal with badly formatted values
stations["lat_good_format"] = True
# stations.loc[(stations["Station no."] == 30) & (stations.Cast == 1),
#              "lat_good_format"] = False

for i, station in stations.iterrows():
    
    if station.lat_good_format:
    
        # Define all formats
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
