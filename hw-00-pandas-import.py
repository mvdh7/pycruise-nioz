import pandas as pd

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
).rename(columns={"Depth": "depth", "Practical salinity": "salinity"})

#%%
ctd1 = pd.read_csv(
    "data/ctd-bottles-variants/08-ctd-bottles-2-1.csv",
    na_values=[-999, -777],
    header=3,
    skiprows=[4],
    encoding="unicode_escape",
    skipfooter=3,
).rename(columns={"Depth": "depth", "Practical salinity": "salinity"})

#%%
ctd1.plot.scatter("salinity", "depth")
