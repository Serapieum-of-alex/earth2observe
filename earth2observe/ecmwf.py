"""Created on Fri Apr  2 06:58:20 2021.

@author: mofarrag
"""
import calendar
import datetime as dt
import os

import numpy as np
import pandas as pd
import yaml
from ecmwfapi import ECMWFDataServer
from loguru import logger
from netCDF4 import Dataset
from pyramids.raster import Raster

from earth2observe import __path__
from earth2observe.utils import print_progress_bar


class ECMWF:
    """RemoteSensing.

    RemoteSensing class contains methods to download ECMWF data

    Methods:
        1- main
        2- DownloadData
        3- API
        4- ListAttributes
    """

    def __init__(
        self,
        time: str = "daily",
        start: str = "",
        end: str = "",
        path: str = "",
        variables: list = [],
        lat_lim: list = [],
        lon_lim: list = [],
        fmt: str = "%Y-%m-%d",
    ):
        """RemoteSensing.

        Parameters
        ----------
        time (str, optional):
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
            [ymin, ymax]. Defaults to [].
        lon_lim (list, optional):
            [xmin, xmax]. Defaults to [].
        fmt (str, optional):
            [description]. Defaults to "%Y-%m-%d".
        """
        self.start = dt.datetime.strptime(start, fmt)
        self.end = dt.datetime.strptime(end, fmt)

        if time == "six_hourly":
            # Set required data for the three hourly option
            self.string1 = "oper"
        # Set required data for the daily option
        elif time == "daily":
            self.Dates = pd.date_range(self.start, self.end, freq="D")
        elif time == "monthly":
            self.Dates = pd.date_range(self.start, self.end, freq="MS")

        self.time = time
        self.path = path
        self.vars = variables

        # correct latitude and longitude limits
        latlim_corr_one = np.floor(lat_lim[0] / 0.125) * 0.125
        latlim_corr_two = np.ceil(lat_lim[1] / 0.125) * 0.125
        self.latlim_corr = [latlim_corr_one, latlim_corr_two]

        # correct latitude and longitude limits
        lonlim_corr_one = np.floor(lon_lim[0] / 0.125) * 0.125
        lonlim_corr_two = np.ceil(lon_lim[1] / 0.125) * 0.125
        self.lonlim_corr = [lonlim_corr_one, lonlim_corr_two]
        # TODO move it to the ECMWF method later
        # for ECMWF only
        self.date_str = f"{self.start}/to/{self.end}"

    def download(self, dataset: str = "interim", progress_bar: bool = True):
        """ECMWF.

        ECMWF method downloads ECMWF daily data for a given variable, time
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
        for var in self.vars:
            # Download data
            logger.info(
                f"Download ECMWF {var} data for period {self.start} till {self.end}"
            )
            self.downloadData(
                var, dataset=dataset, progress_bar=progress_bar
            )  # CaseParameters=[SumMean, Min, Max]
        # delete the downloaded netcdf
        del_ecmwf_dataset = os.path.join(self.path, "data_interim.nc")
        os.remove(del_ecmwf_dataset)

    def downloadData(
        self, var: str, dataset: str = "interim", progress_bar: bool = True
    ):
        """This function downloads ECMWF six-hourly, daily or monthly data.

        Parameters
        ----------
        var: [str]
            variable name
        dataset: [str]
            Default is "interm"
        progress_bar: [bool]
            True if you want to display a progress bar.
        """
        # Load factors / unit / type of variables / accounts
        VarInfo = Variables(self.time)
        var_info = VarInfo.catalog.get(var)
        # Create Out directory
        out_dir = f"{self.path}, {self.time}, {VarInfo.catalog.get('file name')}"

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

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
        grid = "0.125/0.125"
        class_str = "ei"
        # N, W, S, E
        area_str = f"{self.latlim_corr[1]}/{self.lonlim_corr[0]}/{self.latlim_corr[0]}/{self.lonlim_corr[1]}"

        # Download data by using the ECMWF API
        logger.info("Use API ECMWF to collect the data, please wait")
        ECMWF.API(
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
        geo = tuple([geo_one, 0.125, 0.0, geo_four, 0.0, -0.125])

        # Create Waitbar
        if progress_bar:
            total_amount = len(self.Dates)
            amount = 0
            print_progress_bar(
                amount, total_amount, prefix="Progress:", suffix="Complete", length=50
            )

        for date in self.Dates:

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

            if self.time == "daily":
                days_later = 1
            if self.time == "monthly":
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
                f"%{var_output_name}_ECMWF_ERA-Interim_{Var_unit}_{self.time}_{year}.{month}.{day}.tif",
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

    @staticmethod
    def API(
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

        os.chdir(output_folder)
        server = ECMWFDataServer()
        # url = os.environ['ECMWF_API_URL'],
        # key = os.environ['ECMWF_API_KEY'],
        # email = os.environ['ECMWF_API_EMAIL'],
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


class Variables:
    """This class contains the information about the ECMWF variables http://rda.ucar.edu/cgi-bin/transform?xml=/metadata/ParameterTables/WMO_GRIB1.98-0.128.xml&view=gribdoc."""

    with open(f"{__path__[0]}/ecmwf_data_catalog.yaml", "r") as stream:
        catalog = yaml.safe_load(stream)

    def __init__(self, step, version: int = 1):
        self.version = version

    # def __str__(self):
    #     print(
    #         f"Variable name:\n {self.var_name}\nDescriptions\n{self.descriptions}\nUnits : \n{self.units}"
    #     )

    def ListAttributes(self):
        """Print Attributes List."""
        print("\n")
        print(
            f"Attributes List of: {repr(self.__dict__['name'])} - {self.__class__.__name__} Instance\n"
        )
        self_keys = list(self.__dict__.keys())
        self_keys.sort()
        for key in self_keys:
            if key != "name":
                print(str(key) + " : " + repr(self.__dict__[key]))

        print("\n")


# class MSWEP():
"http://www.gloh2o.org/mswx/"
