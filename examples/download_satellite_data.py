"""
Download Satellite data
ECMWF
Installation of ECMWF API key
1 - to be able to use Hapi to download ECMWF data you need to register and setup your account in the ECMWF website (https://apps.ecmwf.int/registration/)

2 - Install ECMWF key (instruction are here https://confluence.ecmwf.int/display/WEBAPI/Access+ECMWF+Public+Datasets#AccessECMWFPublicDatasets-key)
"""
from earth2observe.chirps import CHIRPS
from earth2observe.ecmwf import ECMWF, Variables

#%% precipitation
start = "2009-01-01"
end = "2009-01-10"
time = "daily"
lat = [4.190755, 4.643963]
lon = [-75.649243, -74.727286]
path = "/data/satellite_data/"
# Temperature, Evapotranspiration
variables = ["T", "E"]
#%%
Vars = Variables("daily")
Vars.__str__()
#%% Temperature
start = "2009-01-01"
end = "2009-02-01"
Time = "daily"
latlim = [4.19, 4.64]
lonlim = [-75.65, -74.73]
path = r"C:\MyComputer\01Algorithms\Hydrology\earth2observe\examples\data\ecmwf"
# Temperature, Evapotranspiration
variables = ["T", "E"]

Coello = ECMWF(
    time=time,
    start=start,
    end=end,
    lat_lim=latlim,
    lon_lim=lonlim,
    path=path,
    variables=variables,
)

Coello.download()

#%%
path = r"C:\MyComputer\01Algorithms\Hydrology\earth2observe\examples\data\chirps"
Coello = CHIRPS(
    time=time,
    start=start,
    end=end,
    lat_lim=latlim,
    lon_lim=lonlim,
    path=path,
)
Coello.Download()  # cores=4
