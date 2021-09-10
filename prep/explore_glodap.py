import pandas as pd, numpy as np
from matplotlib import pyplot as plt

# Import GLODAP Atlantic dataset and tidy up
glodap = pd.read_csv(
    "/home/matthew/data/glodap/GLODAPv2.2021_Atlantic_Ocean.csv", na_values=-9999
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
data = glodap[glodap.cruise == cruise]

# Get stations, convert to degrees and minutes, add errors, write to text file
stations = data[["station", "latitude", "longitude"]].groupby("station").mean()
with open("data/stations.txt", "w") as f:
    f.write("Station no.\tLatitude\tLongitude\n")
    for s, row in stations.iterrows():
        lat_deg = np.floor(np.abs(row.latitude))
        lat_dec_mins = (np.abs(row.latitude) - lat_deg) * 60
        # lat_dir = "N" if row.latitude > 0 else "S"  # correct approach
        lat_dir = "S"  # deliberate error
        lat_mins = np.floor(lat_dec_mins)
        lat_secs = (lat_dec_mins - lat_mins) * 60
        lon_deg = np.floor(np.abs(row.longitude))
        lon_dec_mins = (np.abs(row.longitude) - lon_deg) * 60
        lon_dir = "E" if row.longitude > 0 else "W"
        lon_mins = np.floor(lon_dec_mins)
        lon_secs = (lon_dec_mins - lon_mins) * 60
        if s < 75 or s > 114:
            f.write(
                (
                    "{station:.0f}\t"
                    + "{lat_deg:02.0f}°{lat_mins:05.2f}'{lat_dir}\t"
                    + "{lon_deg:03.0f}°{lon_mins:05.2f}'{lon_dir}\n"
                ).format(
                    station=s,
                    lat_deg=lat_deg,
                    lat_mins=lat_dec_mins,
                    lat_dir=lat_dir,
                    lon_deg=lon_deg,
                    lon_mins=lon_dec_mins,
                    lon_dir=lon_dir,
                )
            )
        else:
            f.write(
                (
                    "{station:.0f}\t"
                    + "{lat_deg:02.0f}°{lat_mins:02.0f}'{lat_secs:02.0f}\"{lat_dir}\t"
                    + "{lon_deg:03.0f}°{lon_mins:02.0f}'{lon_secs:02.0f}\"{lon_dir}\n"
                ).format(
                    station=s,
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
