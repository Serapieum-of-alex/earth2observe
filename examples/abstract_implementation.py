from earth2observe.earth2observe import Earth2Observe

source = "chirps"
start = "2009-01-01"
end = "2009-01-10"
temporal_resolution = "daily"
latlim = [4.19, 4.64]
lonlim = [-75.65, -74.73]
path = r"examples\data\chirps"
variables = ["precipitation"]
e2o = Earth2Observe(
    data_source=source,
    start=start,
    end=end,
    variables=variables,
    lat_lim=latlim,
    lon_lim=lonlim,
    temporal_resolution=temporal_resolution,
    path=path,
)
# e2o.download()
#%%
path = r"examples\data\chirps-cores"

e2o = Earth2Observe(
    data_source=source,
    start=start,
    end=end,
    variables=variables,
    lat_lim=latlim,
    lon_lim=lonlim,
    temporal_resolution=temporal_resolution,
    path=path,
)
# e2o.download(cores=4)
#%%

path = r"examples\data\ecmwf"
source = "ecmwf"
variables = ["E"]
e2o = Earth2Observe(
    data_source=source,
    start=start,
    end=end,
    variables=variables,
    lat_lim=latlim,
    lon_lim=lonlim,
    temporal_resolution=temporal_resolution,
    path=path,
)
e2o.download()
