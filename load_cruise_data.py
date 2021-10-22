import pandas as pd, numpy as np
import pycruise_tools as pct

# Import lat/lon/station info
stations = pd.read_table("data/stations.txt", encoding="unicode_escape")

# Parse lat/lon text into decimal degrees
stations["lat"] = stations.Latitude.apply(pct.parse_latitude_text)
stations["lon"] = stations.Longitude.apply(pct.parse_longitude_text)
