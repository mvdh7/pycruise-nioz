import os
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
ctd["datetime"] = pd.to_datetime(ctd[['year', 'month', 'day', 'hour', 'minute']])
# Next: use groupby() to condense ^ into stations table

#%% Put averages from ctd back into stations
stations['datetime'] = ctd[['station_cast', 'datetime']].groupby(
    'station_cast'
).mean()

#%% Import nutrients dataset (Excel file)
nutrients = pd.read_excel(
    'data/nutrients.xlsx', na_values=['n.a.']
    ).rename(
    columns={'Sample ID': 'sample_id', 'NO3+NO2': 'NO3_NO2'}
    )

# nutrients.where(
#     nutrients != '<0.01', other=0, inplace=True)
for n in ['NO3_NO2', 'NO2', 'PO4']:
    nutrients[n].where(
        nutrients[n] != '<0.01', other=0, inplace=True)
    nutrients[n] = nutrients[n].astype(float)

def parse_nutrients_sample_id(sid):
    '''Convert station_id column in nutrients df into separate
    station, cast, and bottle values.
    '''
    sid_split = sid.split('-')
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
    return pd.Series({
        'station': station,
        'cast': cast,
        'bottle': bottle,
        })

sids = nutrients.sample_id.apply(parse_nutrients_sample_id)

# nutrients = pd.concat([nutrients, sids], axis=1)

for c, cdata in sids.iteritems():
    nutrients[c] = cdata

# Fill NaNs in station and cast
nutrients.station.fillna(method='ffill', inplace=True)
nutrients.cast.fillna(method='ffill', inplace=True)
