import pandas as pd, numpy as np
from matplotlib import pyplot as plt
import calkulate as calk

# Initialise random number generator
rng = np.random.default_rng(7)

# Import GLODAP Atlantic dataset and tidy up
glodap = pd.read_csv(
    "/home/matthew/data/glodap/GLODAPv2.2021_Atlantic_Ocean.csv",  # Ubuntu
    # "C:/Users/mphum/Documents/data/GLODAP/GLODAPv2.2021_Atlantic_Ocean.csv",  # Windows
    na_values=-9999,
)
cols_G2 = {col: col.replace("G2", "") for col in glodap.columns}
glodap.rename(columns=cols_G2, inplace=True)
glodap.rename(columns={"tco2": "dic", "talk": "alkalinity"}, inplace=True)

#%% Find lat/lon/depth min/max of all cruises
lldmm = (
    glodap[["cruise", "longitude", "latitude", "depth"]]
    .groupby(by="cruise")
    .agg([np.min, np.max, np.size])
)

# Cut to cruises which cross both equator AND prime meridian, and that go deep
lon = lldmm.longitude
lat = lldmm.latitude
lldmm = lldmm[
    (lon.amin < 0)
    & (lon.amax > 0)
    & (lat.amin < 0)
    & (lat.amax > 0)
    & (lldmm.depth.amax > 5000)
]

# Plot those cruises
fig, ax = plt.subplots(dpi=300)
for cruise in lldmm.index:
    ax.scatter(
        "longitude",
        "latitude",
        data=glodap[glodap.cruise == cruise],
        s=10,
        edgecolor="none",
        label=cruise,
    )
ax.legend()
ax.grid(alpha=0.3)

#%% Plot just one cruise
cruise = 346
fig, ax = plt.subplots(dpi=300)
ax.scatter("latitude", "depth", c="salinity", data=glodap[glodap.cruise == cruise], s=5)
ax.invert_yaxis()

#%% Extract data for the selected cruise and reorganise
data = glodap[glodap.cruise == cruise].copy()
data["station"] = data.station.astype(int)
data["cast"] = data.cast.astype(int)

# Renumber bottles for simplicity
b = 0
s = data.station.iloc[0]
for i, row in data.iterrows():
    if row.station == s:
        b += 1
        data.loc[i, "bottle"] = b
    else:
        b = 1
        data.loc[i, "bottle"] = b
        s += 1

# Get stations, convert to degrees and minutes, add errors, write to text file
stations = (
    data[["station", "cast", "latitude", "longitude"]]
    .groupby(["station", "cast"])
    .mean()
)
with open("data/stations.txt", "w") as f:
    f.write("Station no.\tCast\tLatitude\tLongitude\n")
    for s, row in stations.iterrows():
        lat_deg = np.floor(np.abs(row.latitude))
        lat_dec_mins = (np.abs(row.latitude) - lat_deg) * 60
        lat_dir = "N" if row.latitude > 0 else "S"
        lat_mins = np.floor(lat_dec_mins)
        lat_secs = (lat_dec_mins - lat_mins) * 60
        lon_deg = np.floor(np.abs(row.longitude))
        lon_dec_mins = (np.abs(row.longitude) - lon_deg) * 60
        lon_dir = "E" if row.longitude > 0 else "W"
        lon_mins = np.floor(lon_dec_mins)
        lon_secs = (lon_dec_mins - lon_mins) * 60
        s_random = rng.integers(3)
        if s_random == 0:
            f.write(
                (
                    "{station:.0f}\t{cast:.0f}\t"
                    + "{lat_deg:02.0f}°{lat_mins:05.2f}'{lat_dir}\t"
                    + "{lon_deg:03.0f}°{lon_mins:05.2f}'{lon_dir}\n"
                ).format(
                    station=s[0],
                    cast=s[1],
                    lat_deg=lat_deg,
                    lat_mins=lat_dec_mins,
                    lat_dir=lat_dir,
                    lon_deg=lon_deg,
                    lon_mins=lon_dec_mins,
                    lon_dir=lon_dir,
                )
            )
        elif s_random == 1:
            f.write(
                ("{station:.0f}\t{cast:.0f}\t" + "{lat:.4f}\t" + "{lon:.4f}\n").format(
                    station=s[0], cast=s[1], lat=row.latitude, lon=row.longitude
                )
            )
        else:
            # lat_dir = "S"  # deliberate error
            f.write(
                (
                    "{station:.0f}\t{cast:.0f}\t"
                    + "{lat_deg:02.0f}°{lat_mins:02.0f}'{lat_secs:02.0f}\"{lat_dir}\t"
                    + "{lon_deg:03.0f}°{lon_mins:02.0f}'{lon_secs:02.0f}\"{lon_dir}\n"
                ).format(
                    station=s[0],
                    cast=s[1],
                    lat_deg=lat_deg,
                    lat_mins=lat_mins,
                    lat_secs=lat_secs,
                    lat_dir=lat_dir,
                    lon_deg=lon_deg,
                    lon_mins=lon_mins,
                    lon_secs=lon_secs,
                    lon_dir=lon_dir,
                )
            )

#%% Extract nutrient data
data["density25"] = calk.density.seawater_1atm_MP81(
    temperature=25, salinity=data.salinity
)
nuts_list = ["nitrate", "nitrite", "silicate", "phosphate"]
for nut in nuts_list:
    data["{}_vol".format(nut)] = data[nut] * data.density25
data["nitrate_nitrite_vol"] = data.nitrate_vol + data.nitrite_vol
nuts = data[
    [
        "station",
        "cast",
        "bottle",
        "nitrate_nitrite_vol",
        "nitrite_vol",
        "silicate_vol",
        "phosphate_vol",
    ]
].copy().sort_values(["station", "cast", "bottle"])
nuts = nuts[(nuts.station != 81) & (nuts.station != 82)]  # these are screwed up somehow

# Construct new station-cast-bottle column
nuts["sample_id"] = ""
s = -999
c = -999
for i, row in nuts.iterrows():
    if (row.station == s) & (row.cast == c):
        nuts.loc[i, "sample_id"] = "{:.0f}".format(row.bottle)
    else:
        nuts.loc[i, "sample_id"] = "{:.0f}-{:.0f}-{:.0f}".format(
            row.station, row.cast, row.bottle
        )
        s = row.station
        c = row.cast
nuts = nuts[
    [
        "sample_id",
        "nitrate_nitrite_vol",
        "nitrite_vol",
        "silicate_vol",
        "phosphate_vol",
    ]
]
nuts = nuts[
    ~pd.isnull(nuts.nitrate_nitrite_vol)
    | ~pd.isnull(nuts.nitrite_vol)
    | ~pd.isnull(nuts.silicate_vol)
    | ~pd.isnull(nuts.phosphate_vol)
]

# Replace zeros with less-thans
nuts.loc[nuts.nitrite_vol == 0, "nitrite_vol"] = "<0.01"
nuts.loc[nuts.nitrate_nitrite_vol == 0, "nitrate_nitrite_vol"] = "<0.01"
nuts.loc[nuts.phosphate_vol == 0, "phosphate_vol"] = "<0.01"

# Rename columns and save to file
nuts.rename(
    columns={
        "sample_id": "Sample ID",
        "nitrate_nitrite_vol": "NO3+NO2",
        "nitrite_vol": "NO2",
        "silicate_vol": "Si",
        "phosphate_vol": "PO4",
    },
    inplace=True,
)
excel_file = "data/nutrients.xlsx"
nuts.to_excel(
    excel_file, sheet_name="Station {:.0f}".format(s), index=False, na_rep="n.a."
)

#%% Extract CTD data
ctd = data[
    [
        "station",
        "cast",
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "bottomdepth",
        "bottle",
        "pressure",
        "depth",
        "temperature",
        "salinity",
        "oxygen",
    ]
].copy()
ctd.rename(columns={"bottomdepth": "bottom_depth"}, inplace=True)

# Add oxygen and salinity calibrations
oxygen_slope = 1.03  # slope of oxygen calibration
oxygen_offset = 4.7  # offset in oxygen calibration
oxygen_std = 1.0  # 1-sigma uncertainty in discrete oxygen measurements
oxygen_true = ctd.oxygen.copy()
ctd["oxygen"] = (oxygen_true - oxygen_offset) / oxygen_slope
salinity_slope = 0.991  # slope of salinity calibration
salinity_offset = 0.28  # offset in salinity calibration
salinity_std = 0.01  # 1-sigma uncertainty in discrete salinity measurements
salinity_true = ctd.salinity.copy()
ctd["salinity"] = (salinity_true - salinity_offset) / salinity_slope

# Export CTD data files
for s, srow in stations.iterrows():
    S = (ctd.station == s[0]) & (ctd.cast == s[1])
    ctd[S].drop(columns=["station", "cast"]).to_csv(
        "data/ctd-bottles/ctd-bottles-{}-{}.csv".format(*s), na_rep=-999, index=False
    )
