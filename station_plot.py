import pandas as pd
from matplotlib import pyplot as plt

# from load_cruise_data import ctd  # tidy but slow

# Import CTD again
ctd = pd.read_csv("results/ctd.csv")
ctd.set_index("scb", inplace=True)
ctd["datetime"] = pd.to_datetime(ctd.datetime)

# Draw figure
fig, ax = plt.subplots(dpi=300)

ax.scatter("salinity", "temperature", c="NO3", alpha=1, s=5, edgecolor="none", data=ctd)

# ctd.plot.scatter('salinity', 'temperature', ax=ax)
