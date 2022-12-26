from earth2observe.chirps import CHIRPS

# %% precipitation
start = "2009-01-01"
end = "2009-01-10"
time = "daily"
latlim = [4.19, 4.64]
lonlim = [-75.65, -74.73]

path = r"examples\data\chirps"
Coello = CHIRPS(
    time=time,
    start=start,
    end=end,
    lat_lim=latlim,
    lon_lim=lonlim,
    path=path,
)
#%%
# Coello.Download()  # cores=4
#%%
Coello.Download(cores=4)
