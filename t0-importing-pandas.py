import pandas as pd, numpy as np

#%%
ctd1 = pd.read_csv(
    "data/ctd-bottles-variants/00-ctd-bottles-2-1.csv",
    na_values=-999,
)

#%%
ctd1 = pd.read_csv(
    "data/ctd-bottles-variants/01-ctd-bottles-2-1.csv",
    na_values=-999,
    skiprows=3,
)

#%%
ctd1 = pd.read_csv(
    "data/ctd-bottles-variants/02-ctd-bottles-2-1.csv",
    na_values=-999,
    skiprows=[1],
    encoding="unicode_escape",
)

#%%
ctd1 = pd.read_csv(
    "data/ctd-bottles-variants/03-ctd-bottles-2-1.csv",
    na_values=-999,
    header=3,
    skiprows=[4],
    encoding="unicode_escape",
)

#%%
ctd1 = pd.read_csv(
    "data/ctd-bottles-variants/04-ctd-bottles-2-1.txt",
    na_values=-999,
    header=3,
    skiprows=[4],
    encoding="unicode_escape",
    delimiter="\t",
)

#%%
ctd1 = pd.read_excel(
    "data/ctd-bottles-variants/05-ctd-bottles-2-1.xlsx",
    na_values=-999,
    header=3,
    skiprows=[4],
)

#%%
ctd1 = pd.read_excel(
    "data/ctd-bottles-variants/06-ctd-bottles-2-1.xlsx",
    na_values=[-999, -777],
    header=3,
    skiprows=[4],
)

#%%
ctd1 = pd.read_excel(
    "data/ctd-bottles-variants/07-ctd-bottles-2-1.xlsx",
    na_values=[-999, -777],
    header=3,
    skiprows=[4],
).rename(columns={'Depth': 'depth', 'Practical salinity': 'salinity'})

#%%
ctd1 = pd.read_csv(
    "data/ctd-bottles-variants/08-ctd-bottles-2-1.csv",
    na_values=[-999, -777],
    header=3,
    skiprows=[4],
    encoding="unicode_escape",
    skipfooter=3,
).rename(columns={'Depth': 'depth', 'Practical salinity': 'salinity'})

#%%
ctd1.plot.scatter("salinity", 'depth')

#%% Import lat/lon/station info
stations = pd.read_table("data/stations.txt", encoding="unicode_escape")

# Parse station information
# row = stations.iloc[1]

# 54°00'04"S 
# -53.5000
# 50°30.00'S

import re

# Decimal minutes format
dmf = re.match("(\d+)°(\d+\.\d+)'([NS])", "50°30.00'S")
lat = float(dmf.group(1)) + float(dmf.group(2)) / 60
if dmf.group(3) == "S":
    # lat = lat * -1
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

