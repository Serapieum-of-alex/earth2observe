"""Created on Fri Apr  2 06:58:20 2021.

@author: mofarrag
"""
import calendar
import datetime as dt
import os
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import yaml
from ecmwfapi import ECMWFDataServer
from loguru import logger
from netCDF4 import Dataset
from pyramids.raster import Raster

from earth2observe import __path__
from earth2observe.abstractdatasource import AbstractCatalog, AbstractDataSource
from earth2observe.utils import print_progress_bar


class ECMWF(AbstractDataSource):
    """RemoteSensing.

    RemoteSensing class contains methods to download ECMWF data
    """

    temporal_resolution = ["daily", "monthly"]
    spatial_resolution = 0.125

    def __init__(
        self,
        temporal_resolution: str = "daily",
        start: str = None,
        end: str = None,
        path: str = "",
        variables: list = None,
        lat_lim: list = None,
        lon_lim: list = None,
        fmt: str = "%Y-%m-%d",
    ):
        """RemoteSensing.

        Parameters
        ----------
        temporal_resolution (str, optional):
            [description]. Defaults to 'daily'.
        start (str, optional):
            [description]. Defaults to ''.
        end (str, optional):
            [description]. Defaults to ''.
        path (str, optional):
            Path where you want to save the downloaded data. Defaults to ''.
        variables (list, optional):
            Variable code: VariablesInfo('day').descriptions.keys(). Defaults to [].
        lat_lim (list, optional):
            [ymin, ymax]. Defaults to None.
        lon_lim (list, optional):
            [xmin, xmax]. Defaults to None.
        fmt (str, optional):
            [description]. Defaults to "%Y-%m-%d".
        """
        super().__init__(
            start=start,
            end=end,
            variables=variables,
            temporal_resolution=temporal_resolution,
            lat_lim=lat_lim,
            lon_lim=lon_lim,
            fmt=fmt,
        )
        self.path = Path(path).absolute()

    def check_input_dates(
        self, start: str, end: str, temporal_resolution: str, fmt: str
    ):
        """check validity of input dates.

        Parameters
        ----------
        temporal_resolution: (str, optional)
            [description]. Defaults to 'daily'.
        start: (str, optional)
            [description]. Defaults to ''.
        end: (str, optional)
            [description]. Defaults to ''.
        fmt: (str, optional)
            [description]. Defaults to "%Y-%m-%d".
        """
        self.start = dt.datetime.strptime(start, fmt)
        self.end = dt.datetime.strptime(end, fmt)

        if temporal_resolution == "six_hourly":
            # Set required data for the three hourly option
            self.string1 = "oper"
        # Set required data for the daily option
        elif temporal_resolution == "daily":
            self.dates = pd.date_range(self.start, self.end, freq="D")
        elif temporal_resolution == "monthly":
            self.dates = pd.date_range(self.start, self.end, freq="MS")

        self.date_str = f"{self.start}/to/{self.end}"

    def initialize(self):
        """Initialize connection with ECMWF server."""
        try:
            url = os.environ["ECMWF_API_URL"]
            key = os.environ["ECMWF_API_KEY"]
            email = os.environ["ECMWF_API_EMAIL"]
        except KeyError:
            raise AuthenticationError(
                "Please define the following environment variables to successfully establish a "
                "connection with ecmwf server ECMWF_API_URL, ECMWF_API_KEY, ECMWF_API_EMAIL"
            )

        self.server = ECMWFDataServer(url=url, key=key, email=email)

    def create_grid(self, lat_lim: list, lon_lim: list):
        """Create_grid.

            create grid from the lat/lon boundaries

        Parameters
        ----------
        lat_lim: []
            latitude boundaries
        lon_lim: []
            longitude boundaries
        """
        cell_size = self.spatial_resolution
        # correct latitude and longitude limits
        latlim_corr_one = np.floor(lat_lim[0] / cell_size) * cell_size
        latlim_corr_two = np.ceil(lat_lim[1] / cell_size) * cell_size
        self.latlim_corr = [latlim_corr_one, latlim_corr_two]

        # correct latitude and longitude limits
        lonlim_corr_one = np.floor(lon_lim[0] / cell_size) * cell_size
        lonlim_corr_two = np.ceil(lon_lim[1] / cell_size) * cell_size
        self.lonlim_corr = [lonlim_corr_one, lonlim_corr_two]

    def download(
        self, dataset: str = "interim", progress_bar: bool = True, *args, **kwargs
    ):
        """Download wrapper over all given variables.

        ECMWF method downloads ECMWF daily data for a given variable, temporal_resolution
        interval, and spatial extent.


        Parameters
        ----------
        progress_bar : TYPE, optional
            0 or 1. to display the progress bar
        dataset:[str]
            Default is "interim"

        Returns
        -------
        None.
        """
        # read the datasource catalog
        catalog = Catalog()

        for var in self.vars:
            # Download data
            logger.info(
                f"Download ECMWF {var} data for period {self.start} till {self.end}"
            )
            var_info = catalog.get_variable(var)
            self.downloadDataset(
                var_info, dataset=dataset, progress_bar=progress_bar
            )
        # delete the downloaded netcdf
        del_ecmwf_dataset = os.path.join(self.path, "data_interim.nc")
        os.remove(del_ecmwf_dataset)

    def downloadDataset(
        self,
        var_info: Dict[str, str],
        dataset: str = "interim",
        progress_bar: bool = True,
    ):
        """Download a climate variable.

            This function downloads ECMWF six-hourly, daily or monthly data.

        Parameters
        ----------
        var_info: [str]
            variable detailed information
            >>> {
            >>>     'descriptions': 'Evaporation [m of water]',
            >>>     'units': 'mm',
            >>>     'types': 'flux',
            >>>     'temporal resolution': ['six hours', 'daily', 'monthly'],
            >>>     'file name': 'Evaporation',
            >>>     'download type': 2,
            >>>     'number_para': 182,
            >>>     'var_name': 'e',
            >>>     'factors_add': 0,
            >>>     'factors_mul': 1000
            >>> }
        dataset: [str]
            Default is "interm"
        progress_bar: [bool]
            True if you want to display a progress bar.
        """
        # Create the directory
        out_dir = f"{self.path}/{self.temporal_resolution}/{var_info.get('file name')}"
        # out_dir = f"{self.path}/{self.temporal_resolution}/{var_info.get('file name')}"
        # files = f"{out_dir}/{self.temporal_resolution}_{var_info.get('file name')}"

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # trigger the request to the server
        self.API(var_info, dataset)
        # process the downloaded data
        self.post_download(var_info, out_dir, dataset, progress_bar)

    def API(self, var_info, dataset):
        """form the request url abd trigger the request.

        Parameters
        ----------
        dataset: [str]
            dataset name
        var_info: [str]
            variable detailed information
            >>> {
            >>>     'descriptions': 'Evaporation [m of water]',
            >>>     'units': 'mm',
            >>>     'types': 'flux',
            >>>     'temporal resolution': ['six hours', 'daily', 'monthly'],
            >>>     'file name': 'Evaporation',
            >>>     'download type': 2,
            >>>     'number_para': 182,
            >>>     'var_name': 'e',
            >>>     'factors_add': 0,
            >>>     'factors_mul': 1000
            >>> }
        """
        download_type = var_info.get("download type")
        # https://www.ecmwf.int/en/computing/software/ecmwf-web-api
        stream = "oper"  # https://apps.ecmwf.int/codes/grib/format/mars/stream/
        # step is 0, 3, 6, 9, 12
        # time_str is 0, 6, 12, 18
        # levtype: sfc for surface, pl for pressure levels (DEFAULT), pv for potential vorticity level
        # type : 'fc' for forecast field, an for analysis field, ob for Observations, ai for Analysis input,
        #       im for Satellite images, ofb for ODB observation feedback, mfb for Monitoring feedback,
        #       oai for ODB analysis input, wp for Weather parameters (in BUFR format)
        # key words for the API https://confluence.ecmwf.int/display/UDOC/Identification+keywords
        if download_type == 1:
            step = "0"
            time_str = "00:00:00/06:00:00/12:00:00/18:00:00"
            levtype = "sfc"  # surface
            type_str = "an"  # analysis field

        if download_type == 2:
            step = "12"
            time_str = "00:00:00/12:00:00"
            levtype = "sfc"  # surface
            type_str = "fc"  # forecast field

        if download_type == 3:
            step = "0"
            time_str = "00:00:00/06:00:00/12:00:00/18:00:00"
            levtype = "pl"  # pressure levels (DEFAULT)
            type_str = "an"  # analysis field

        parameter_number = var_info.get("number_para")

        param = f"{parameter_number}.128"
        grid = f"{self.spatial_resolution}/{self.spatial_resolution}"
        class_str = "ei"
        # N, W, S, E
        area_str = f"{self.latlim_corr[1]}/{self.lonlim_corr[0]}/{self.latlim_corr[0]}/{self.lonlim_corr[1]}"

        # Download data by using the ECMWF API
        logger.info("Use API ECMWF to collect the data, please wait")
        self.callAPI(
            self.server,
            self.path,
            download_type,
            stream,
            levtype,
            param,
            step,
            grid,
            time_str,
            self.date_str,
            type_str,
            class_str,
            area_str,
            dataset=dataset,
        )

    @staticmethod
    def callAPI(
        server,
        output_folder: str,
        download_type: str,
        stream: str,
        levtype: str,
        param: str,
        step: str,
        grid: str,
        time_str: str,
        date_str: str,
        type_str: str,
        class_str: str,
        area_str: str,
        dataset: str = "interim",
    ):
        """send the request to the server.

        Parameters
        ----------
        output_folder: [str]
            directory where files will be saved
        download_type: [int]
        stream
        levtype
        param
        step
        grid
        time_str
        date_str
        type_str
        class_str
        area_str
        dataset
        """

        os.chdir(output_folder)

        if download_type == 1 or download_type == 2:
            server.retrieve(
                {
                    "stream": stream,
                    "levtype": levtype,
                    "param": param,
                    "dataset": dataset,
                    "step": step,
                    "grid": grid,
                    "time": time_str,
                    "date": date_str,
                    "type": type_str,  # http://apps.ecmwf.int/codes/grib/format/mars/type/
                    "class": class_str,  # http://apps.ecmwf.int/codes/grib/format/mars/class/
                    "area": area_str,
                    "format": "netcdf",
                    "target": f"data_{dataset}.nc",
                }
            )

        if download_type == 3:
            server.retrieve(
                {
                    "levelist": "1000",
                    "stream": stream,
                    "levtype": levtype,
                    "param": param,
                    "dataset": dataset,
                    "step": step,
                    "grid": grid,
                    "time": time_str,
                    "date": date_str,
                    "type": type_str,  # http://apps.ecmwf.int/codes/grib/format/mars/type/
                    "class": class_str,  # http://apps.ecmwf.int/codes/grib/format/mars/class/
                    "area": area_str,
                    "format": "netcdf",
                    "target": f"data_{dataset}.nc",
                }
            )

    def post_download(
        self, var_info: Dict[str, str], out_dir, dataset: str, progress_bar: bool = True
    ):
        """clip the downloaded data to the extent we want.

        Parameters
        ----------
        var_info: [str]
            variable detailed information
            >>> {
            >>>     'descriptions': 'Evaporation [m of water]',
            >>>     'units': 'mm',
            >>>     'types': 'flux',
            >>>     'temporal resolution': ['six hours', 'daily', 'monthly'],
            >>>     'file name': 'Evaporation',
            >>>     'download type': 2,
            >>>     'number_para': 182,
            >>>     'var_name': 'e',
            >>>     'factors_add': 0,
            >>>     'factors_mul': 1000
            >>> }
        out_dir: [str]
            root directory for where the files will be saved.
        dataset: [str]
            dataset name. Default is interm
        progress_bar: [bool]
            True to display a progress bar
        """
        # Open the downloaded data
        NC_filename = os.path.join(self.path, f"data_{dataset}.nc")
        fh = Dataset(NC_filename, mode="r")

        # Get the NC variable parameter
        parameter_var = var_info.get("var_name")
        Var_unit = var_info.get("units")
        factors_add = var_info.get("factors_add")
        factors_mul = var_info.get("factors_mul")

        # Open the NC data
        Data = fh.variables[parameter_var][:]
        Data_time = fh.variables["time"][:]
        lons = fh.variables["longitude"][:]
        lats = fh.variables["latitude"][:]

        # Define the georeference information
        geo_four = np.nanmax(lats)
        geo_one = np.nanmin(lons)
        geo = tuple(
            [
                geo_one,
                self.spatial_resolution,
                0.0,
                geo_four,
                0.0,
                -1 * self.spatial_resolution,
            ]
        )

        # Create Waitbar
        if progress_bar:
            total_amount = len(self.dates)
            amount = 0
            print_progress_bar(
                amount, total_amount, prefix="Progress:", suffix="Complete", length=50
            )

        for date in self.dates:

            # Define the year, month and day
            year = date.year
            month = date.month
            day = date.day

            # Hours since 1900-01-01
            start = dt.datetime(year=1900, month=1, day=1)
            end = dt.datetime(year, month, day)
            diff = end - start
            hours_from_start_begin = diff.total_seconds() / 60 / 60

            Date_good = np.zeros(len(Data_time))

            if self.temporal_resolution == "daily":
                days_later = 1
            if self.temporal_resolution == "monthly":
                days_later = calendar.monthrange(year, month)[1]

            Date_good[
                np.logical_and(
                    Data_time >= hours_from_start_begin,
                    Data_time < (hours_from_start_begin + 24 * days_later),
                )
            ] = 1

            Data_one = np.zeros(
                [int(np.sum(Date_good)), int(np.size(Data, 1)), int(np.size(Data, 2))]
            )
            Data_one = Data[np.int_(Date_good) == 1, :, :]

            # convert the values to the units we want
            Data_end = factors_mul * np.nanmean(Data_one, 0) + factors_add

            if var_info.get("types") == "flux":
                Data_end = Data_end * days_later

            var_output_name = var_info.get("file name")

            # Define the out name
            name_out = os.path.join(
                out_dir,
                f"%{var_output_name}_ECMWF_ERA-Interim_{Var_unit}_{self.temporal_resolution}_{year}.{month}.{day}.tif",
            )

            # Create Tiff files
            # Raster.Save_as_tiff(name_out, Data_end, geo, "WGS84")
            Raster.createRaster(path=name_out, arr=Data_end, geo=geo, epsg="WGS84")

            if progress_bar:
                amount = amount + 1
                print_progress_bar(
                    amount,
                    total_amount,
                    prefix="Progress:",
                    suffix="Complete",
                    length=50,
                )

        fh.close()


class Catalog(AbstractCatalog):
    """ECMWF data catalog This class contains the information about the ECMWF variables http://rda.ucar.edu/cgi-bin/transform?xml=/metadata/ParameterTables/WMO_GRIB1.98-0.128.xml&view=gribdoc."""

    def __init__(self):
        # get the catalog
        super().__init__()
        pass

    def get_catalog(self):
        """readthe data catalog from disk."""
        with open(f"{__path__[0]}/ecmwf_data_catalog.yaml", "r") as stream:
            catalog = yaml.safe_load(stream)
        return catalog

    def get_variable(self, var_name):
        """retrieve a variable form the datasource catalog."""
        return super().get_variable(var_name)


class AuthenticationError(Exception):
    """Failed to establish connection with ECMWF server."""

    pass
