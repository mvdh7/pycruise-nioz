import pandas as pd, numpy as np
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
ctd = []
for i, row in stations.iterrows():
    print(i)
    
    # Determine filename from row of stations table (station & cast)
    # filename = "data/ctd-bottles/ctd-bottles-1-1.csv"
    # filename = "data/ctd-bottles/ctd-bottles-" + "1" + "-" + "1" + ".csv"
    # filename = "data/ctd-bottles/ctd-bottles-" + str(row.station) + "-" + str(row.cast) + ".csv"
    filename = "data/ctd-bottles/ctd-bottles-{}-{}.csv".format(row.station, row.cast)
    
    # Import CTD data for this station and append to list
    _ctd = pd.read_csv(filename, na_values=-999)
    _ctd["station_cast"] = i
    ctd.append(_ctd)

# Concatenate all stations into single df
ctd = pd.concat(ctd)

#%% Put data from stations into ctd
for var in ["lat", "lon", "station", "cast"]:
    ctd[var] = stations.loc[ctd.station_cast, var].values

# Get datetime
ctd["datetime"] = pd.to_datetime(ctd[['year', 'month', 'day', 'hour', 'minute']])
# Next: use groupby() to condense ^ into stations table
